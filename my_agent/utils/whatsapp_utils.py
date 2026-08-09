from copy import deepcopy
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
from ..database.db import get_session
from ..routers.customer_router import create_order, get_customer_by_contact
from ..schemas.common_schema import OrderSchemaRequestSchema
from utils.common_utils import verify_geo_location
from ..utils.agent_utils import get_response_from_llm
from ..services.wa_services import send_whatsapp_message
from ..session.session_manager import update_step, has_session, get_step, save_session, delete_session, get_data, print_sessions


async def process_user_message(messages):
    print(messages)
    name = None
    contact_no = messages[0].get("from")
    contact_id = str(contact_no)[2:]
    async for session in get_session():
        response = await get_customer_by_contact(contact_id, session)
        name = response.get("name")
    if has_session(messages[0].get("from")):
        payload, contact_no = await handle_session_based_flow(messages[0])
    elif messages[0].get("type") == "interactive":
        contact_no, payload = await handle_interactive_message(messages[0])
    else:
        contact_no = messages[0].get("from")
        session_id = contact_no
        message = messages[0].get("text", {}).get("body")
        response = await get_response_from_llm(message, contact_no, session_id)
        payload = get_message_template(
            response=response, contact_no=contact_no, name=name)
    await send_whatsapp_message(contact_no, payload)


def get_message_template(response, contact_no, name):
    print("Raw LLM Response:")
    print(repr(response))
    response = response.replace("```json", "")
    response = response.replace("```", "")
    response = response.strip()

    response = json.loads(response)

    text = response["text"]

    match response["action_type"]:

        case "options_menu":
            parts = text.split("\n\n")
            header = parts[0] if len(parts) > 0 else ""
            body = parts[1] if len(parts) > 1 else ""
            footer = parts[2] if len(parts) > 2 else ""
            payload = deepcopy(interactive_tempalte_for_first_message)
            payload["interactive"]["header"][
                "text"] = f"Hello {name}! 👋 Welcome to Eco Rinse Laundry." if name is not None else header
            payload["interactive"]["body"]["text"] = (
                f"{body}\n\n{footer}"
            )
            payload["interactive"]["footer"]["text"] = "Eco Rinse Laundry"

            return payload

        case "service_menu":
            return service_template

        case "booking":
            save_session(
                contact_no,
                flow="pickup",
                step="name_details"
            )
            return handle_name_details()
        case "contact_details":
            return contact_details()
        case "text":
            return {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "type": "text",
                "text": {
                    "body": text
                }
            }


async def handle_interactive_message(message):
    print("Inside handle interactive messsage")
    print_sessions()
    contact_no = message.get("from")
    interactive = message.get("interactive", {})

    if interactive.get("type") == "button_reply":
        button_id = interactive["button_reply"]["id"]
        if button_id == "services":
            return contact_no, service_template

        elif button_id == "schedule_pickup":
            contact_id = str(contact_no)[2:]
            async for session in get_session():
                response = await get_customer_by_contact(contact_id, session)
                print(response)
                if response.get("name"):
                    save_session(
                        contact_no,
                        flow="pickup",
                        step="pickup_address",
                        name=response.get("name"),
                        phone_number=contact_id
                    )
                return contact_no, handle_user_address()

            save_session(
                contact_no,
                flow="pickup",
                step="name_details"
            )
            return contact_no, handle_name_details()
        elif button_id == "contact":
            return contact_no, contact_details()


async def handle_session_based_flow(message):
    response = message.get("text", {}).get("body")
    contact_id = message.get("from")
    step = get_step(contact_id)
    if step == "name_details":
        save_session(contact_id, name=response, phone_number=contact_id)
        update_step(contact_id, "pickup_address")
        return handle_user_address(), contact_id
    elif step == "pickup_address":
        if message.get("type") != "location":
            return handle_user_address(), contact_id

        location = message["location"]
        if verify_geo_location(location.get("longitude"), location.get("latitude")):
            return service_unavilable(), contact_id
        print(location)
        save_session(
            contact_id,
            step="landmark",
            latitude=location.get("latitude"),
            longitude=location.get("longitude"),
            pickup_address=location.get("address")
        )
        return handle_landmark(), contact_id

    elif step == "landmark":
        save_session(
            contact_id,
            step="date_step",
            landmark=response
        )
        return handle_date_slot(), contact_id

    elif step == "date_step":
        if message.get("type") == "interactive":
            list_reply = message.get("interactive", {}).get("list_reply")
            if not list_reply:
                return contact_id, handle_date_slot()
            date_slot = list_reply.get("title")
            save_session(
                contact_id,
                step="time_slot",
                pickup_date=date_slot
            )
            return handle_time(date_slot), contact_id

    elif step == "time_slot":
        if message.get("type") == "interactive":
            list_reply = message.get("interactive", {}).get("list_reply")
            if not list_reply:
                return date_slot(), contact_id
            time_slot = list_reply.get("title")
            print("time", time_slot)
            save_session(
                contact_id,
                step="confirm_step",
                pickup_time=time_slot
            )
            details = get_data(contact_id)

            return handle_confirm_step(
                details["name"],
                details["pickup_date"]
            ), contact_id
    elif step == "confirm_step":
        if message.get("type") == "interactive":
            button_id = message.get("interactive").get(
                "button_reply").get("id")
            details = get_data(contact_id)

            details["pickup_date"] = datetime.strptime(
                details["pickup_date"],
                "%d-%m-%Y"
            ).date()

            details["pickup_time"] = datetime.strptime(
                details["pickup_time"],
                "%H:%M"
            ).time()

            payload = OrderSchemaRequestSchema(**details)
            print(payload)
            if button_id == "confirm":
                async for session in get_session():
                    response = await create_order(payload, session)
                    delete_session(contact_id)
                    return handle_confirm_message(), contact_id
            else:
                delete_session(contact_id)
                return handle_cancel_message(), contact_id


def handle_name_details():
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "type": "text",
        "text": {
            "body": "Enter Your Name"
        }
    }
    return payload


def handle_landmark():
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "type": "text",
        "text": {
            "body": "Please provide a landmark"
        }
    }
    return payload


def contact_details():
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "type": "text",
        "text": {
            "preview_url": True,
            "body": (
                "📞 *Call Us*\n"
                "+919900388956\n\n"
                "📧 *Email*\n"
                "ecorinselaundry@gmail.com\n\n"
                "🌐 *Website*\n"
                "https://ecorinse.sumankumarsahu7890.workers.dev/\n\n"
                "📍 *Google Maps*\n"
                "https://www.google.com/maps/place/Eco+Rinse+Laundry/@13.0200617,77.6747846,17z/data=!3m1!4b1!4m6!3m5!1s0x3bae110b73219ed3:0x304fe9cd02c1c646!8m2!3d13.0200617!4d77.6747846!16s%2Fg%2F11zcr57kzc?entry=tts&g_ep=EgoyMDI2MDcxNS4wIPu8ASoASAFQAw%3D%3D&skid=b42986d7-18d7-4e7f-925e-2b1ebddabc78"
            )
        }
    }
    return payload


def handle_confirm_message():
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "type": "text",
        "text": {
            "body": "Thank You for choosing us!, We will make sure to provide the best service as possible"
        }
    }
    return payload


def handle_cancel_message():
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "type": "text",
        "text": {
            "body": (
                "Your pickup request has been cancelled successfully. ❌\n\n"
                "No worries! If you need our laundry services in the future, "
                "just send us a message anytime.\n\n"
                "Thank you for choosing Eco Rinse Laundry! 😊"
            )
        }
    }
    return payload


def handle_user_address():
    paylaod = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "type": "interactive",
        "interactive": {
            "type": "location_request_message",
            "body": {
                "text": "Let's start with your pickup, Can you please share your location"
            },
            "action": {
                "name": "send_location"
            }
        },
    }
    return paylaod


def handle_confirm_step(name, time):
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {
                "type": "text",
                "text": "Pickup Confirmation"
            },
            "body": {
                "text": (
                    f"Hi {name}! 👋\n\n"
                    f"Your pickup is scheduled for {time}.\n\n"
                    "Please use the buttons below to confirm or cancel your pickup."
                )
            },
            "footer": {
                "text": "Eco Rinse Laundry"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "confirm",
                            "title": "Confirm"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "cancel",
                            "title": "Cancel"
                        }
                    }
                ]
            }
        }
    }
    return payload


def handle_time(date_slot):
    time_slots = []

    store_opening = 11
    store_closing = 20

    ist = ZoneInfo("Asia/Kolkata")
    now = datetime.now(ist)

    selected_date = datetime.strptime(
        date_slot, "%d-%m-%Y"
    ).date()

    today_date = now.date()

    for hour in range(store_opening, store_closing):
        if selected_date == today_date and hour <= now.hour:
            continue

        time_slots.append({
            "id": f"{hour:02d}:00",
            "title": f"{hour:02d}:00"
        })

    return handle_time_slot(time_slots)


def handle_time_slot(time_slots):
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Select Time Slot"
            },
            "body": {
                "text": "Which Time Slot do you prefer"
            },
            "footer": {
                "text": "Based on time slot, we are going to pick ✌🏻"
            },
            "action": {
                "button": "Choose Your Slot",
                "sections": [
                    {
                        "title": "Pick Up Time Slots",
                        "rows": time_slots
                    }
                ]
            }
        },
    }
    return payload


def handle_date_slot():
    date_slots = []

    now = datetime.now(ZoneInfo("Asia/Kolkata"))

    store_opening = 11
    store_closing = 20

    today = now.date()

    for i in range(7):
        current_date = today + timedelta(days=i)

        if i == 0:
            if not (store_opening <= now.hour < store_closing):
                continue

        date_slots.append({
            "id": current_date.strftime("%d-%m-%Y"),
            "title": current_date.strftime("%d-%m-%Y")
        })

    return handle_date_message(date_slots)


interactive_tempalte_for_first_message = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": "<WHATSAPP_USER_PHONE_NUMBER>",
    "type": "interactive",
    "interactive": {
        "type": "button",
        "header": {
            "type": "text",
            "text": "<MESSAGE_HEADER>"
        },
        "body": {
            "text": "<BODY_TEXT>"
        },
        "footer": {
            "text": "<FOOTER_TEXT>"
        },
        "action": {
            "buttons": [
                {
                    "type": "reply",
                    "reply": {
                        "id": "services",
                        "title": "Services"
                    }
                },
                {
                    "type": "reply",
                    "reply": {
                        "id": "schedule_pickup",
                        "title": "Schedule a Pickup"
                    }
                },
                {
                    "type": "reply",
                    "reply": {
                        "id": "contact",
                        "title": "Contact-Us"
                    }
                }
            ]
        },
    }
}
service_template = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "type": "interactive",
    "interactive": {
        "type": "button",
        "body": {
            "text": "🧺 *Our Laundry Services*\n\n• Wash & Fold\n• Wash & Iron\n• Dry Cleaning\n• Steam Ironing\n• Shoe Cleaning\n• Premium Laundry\n• Carpet Cleaning\n• Curtain Cleaning\n\nNeed help? Book a pickup today!"
        },
        "action": {
            "buttons": [
                {
                    "type": "reply",
                    "reply": {
                        "id": "schedule_pickup",
                        "title": "Schedule Pickup"
                    }
                }
            ]
        }
    }
}


def service_unavilable():
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "type": "text",
        "text": {
            "body": (
                "Oops ! Your area is not serviceable"
            )
        }
    }
    return payload


def handle_date_message(date_slots: list):
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Select Date"
            },
            "body": {
                "text": "Which Date do you prefer"
            },
            "footer": {
                "text": "Based on Date, we are going to pick ✌🏻"
            },
            "action": {
                "button": "Choose Your Date",
                "sections": [
                    {
                        "title": "Pick Up Time Slots",
                        "rows": date_slots
                    }
                ]
            }
        },
    }
    return payload
