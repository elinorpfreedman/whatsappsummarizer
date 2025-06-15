from fastapi import FastAPI, Request
import httpx
import os
import logging
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
logging.basicConfig(level=logging.INFO)

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
        logging.info("✅ Webhook verified")
        return int(params["hub.challenge"])
    return {"status": "failed verification"}

@app.post("/webhook")
async def handle_webhook(req: Request):
    data = await req.json()
    logging.info(f"🔔 Incoming webhook: {data}")

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages")
        if messages:
            msg = messages[0]
            text = msg["text"]["body"]
            sender_id = msg["from"]
            logging.info(f"📩 Message from {sender_id}: {text}")

            # Call the LLM service
            async with httpx.AsyncClient() as client:
                try:
                    llm_response = await client.post(f"{LLM_SERVICE_URL}", json={"text": text})
                    llm_data = llm_response.json()
                    summary = llm_data.get("summary", "Sorry, there was a problem summarizing your message.")
                except Exception as e:
                    logging.error(f"❌ Error calling LLM service: {e}")
                    summary = "Sorry, there was a problem summarizing your message."

            # Reply to the user
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages",
                    params={"access_token": WHATSAPP_TOKEN},
                    json={
                        "messaging_product": "whatsapp",
                        "to": sender_id,
                        "text": {"body": summary},
                    },
                )
                logging.info(f"📤 Reply status: {response.status_code}")
                logging.info(f"📤 Reply response: {response.text}")
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"❌ Unexpected error: {str(e)}")
        return {"status": "error", "message": str(e)}
