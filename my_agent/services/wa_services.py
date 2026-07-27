from ..config import WHATSAPP_TOKEN, BASE_URL, VERSION, PHONE_NUMBER_ID
import requests
import httpx


# data = {
#     "audio": {
#         "id": "<AUDIO_OBJECT_ID>"
#     },
#     "messaging_product": "whatsapp",
#     "recipient_type": "individual",
#     "to": "{{Recipient-Phone-Number}}",
#     "type": "audio"
# }

# response = requests.request("POST", url, json=data, headers=headers)

# print(response.json())


async def send_whatsapp_message(number, payload):
    url = f"{BASE_URL}{VERSION}/{PHONE_NUMBER_ID}/messages"
    print(type(payload))
    print(payload)
    print(url)
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    print("Entered into whatsapp service")
    payload["to"] = number

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=payload,
            headers=headers,
        )
    print(url)
    print(headers)
    print(payload)
    print(response.status_code)
    print(response.text)

    return response
