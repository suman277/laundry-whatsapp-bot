from fastapi import APIRouter, Query, Request
from fastapi.responses import PlainTextResponse
from ..config import VERIFY_TOKEN
from ..utils.agent_utils import get_response_from_llm
from ..services.wa_services import send_whatsapp_message
from ..utils.whatsapp_utils import process_user_message

wp_router = APIRouter(prefix="/whatsapp", tags=["whatsapp routers"])


# @wp_router.get("/webhook")
# async def verify_webhook(
#     mode: str = Query(alias="hub.mode"),
#     challenge: str = Query(alias="hub.challenge"),
#     verify_token: str = Query(alias="hub.verify_token"),
# ):
#     if mode == "subscribe" and verify_token == VERIFY_TOKEN:
#         print(VERIFY_TOKEN)
#         return PlainTextResponse(challenge)

#     return PlainTextResponse("Forbidden", status_code=403)

@wp_router.get("/webhook")
async def verify_webhook(
    mode: str = Query(alias="hub.mode"),
    challenge: str = Query(alias="hub.challenge"),
    verify_token: str = Query(alias="hub.verify_token"),
):
    # print("MODE:", repr(mode))
    # print("VERIFY_TOKEN RECEIVED:", repr(verify_token))
    # print("VERIFY_TOKEN EXPECTED:", repr(VERIFY_TOKEN))
    # print("CHALLENGE:", repr(challenge))

    if mode == "subscribe" and verify_token == VERIFY_TOKEN:
        print("✅ VERIFIED")
        return PlainTextResponse(challenge)

    print("❌ TOKEN MISMATCH")
    return PlainTextResponse("Forbidden", status_code=403)


# @wp_router.post("/webhook")
# async def receive_message(request: Request):
#     data = await request.json()
#     print(data)
#     message = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
#     contact_no = data["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
#     session_id = contact_no
#     print(message)
#     response = await get_response_from_llm(message, contact_no, session_id)
#     print(response)
#     payload = {
#         "messaging_product": "whatsapp",
#         "recipient_type": "individual",
#         "type": "text",
#         "text": {
#             "body": response
#         },
#     }
#     await send_whatsapp_message(contact_no, payload)
#     return {"status": "received"}


@wp_router.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    # print(data)
    # message = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
    # contact_no = data["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    # session_id = contact_no
    # print(message)
    try:
        entry = data.get("entry")
        if not entry:
            return {"status": "ok"}
        changes = entry[0].get("changes")
        if not changes:
            return {"status": "ok"}
        value = changes[0].get("value")
        if not value:
            return {"status": "ok"}
        messages = value.get("messages")
        if not messages:
            return {"status":"ok"}
        await process_user_message(messages)

        # contact_no = messages[0].get("from")
        # session_id = contact_no
        # print(message)
        # response = await get_response_from_llm(message, contact_no, session_id)
        # print(response)
        # payload = {
        # "messaging_product": "whatsapp",
        # "recipient_type": "individual",
        # "type": "text",
        # "text": {
        #     "body": response
        # },
        # }
        # await send_whatsapp_message(contact_no, payload)
    except Exception as e:
        print("An error occured in recieve message webhook", e)
    
    return {"status": "received"}