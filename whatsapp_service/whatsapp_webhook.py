from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import os
import httpx

router = APIRouter()

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")


@router.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)
    return JSONResponse(content={"status": "invalid token"}, status_code=403)


@router.post("/webhook")
async def receive_whatsapp_message(request: Request):
    body = await request.json()
    print("🔔 Incoming webhook:", body)

    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages")

        if messages:
            msg = messages[0]
            sender = msg["from"]
            text = msg["text"]["body"]

            print(f"📩 Message from {sender}: {text}")

            # Send back reply
            reply = f"You said: {text}"
            await send_whatsapp_message(sender, reply)

    except Exception as e:
        print("⚠️ Error processing message:", e)

    return {"status": "received"}


async def send_whatsapp_message(recipient_id: str, message: str):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message}
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        print("📤 Reply status:", response.status_code)
        print("📤 Reply response:", response.text)
