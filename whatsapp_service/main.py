import os
from fastapi import FastAPI, APIRouter, Request, status
from fastapi.responses import JSONResponse
from twilio.rest import Client
import requests
from typing import List, Dict
from datetime import datetime

# In-memory message store: {sender: [ {body, timestamp, read}, ... ]}
MESSAGE_STORE: Dict[str, List[Dict]] = {}

router = APIRouter()

def store_message(sender: str, body: str):
    MESSAGE_STORE.setdefault(sender, []).append({
        "body": body,
        "timestamp": datetime.now().isoformat(),
        "read": False
    })

def get_unread_messages(sender: str):
    return [msg for msg in MESSAGE_STORE.get(sender, []) if not msg["read"]]

def mark_messages_as_read(sender: str):
    for msg in MESSAGE_STORE.get(sender, []):
        msg["read"] = True

@router.post("/twilio/webhook")
async def receive_message(request: Request):
    form_data = await request.form()
    whatsapp_message = form_data.get("Body")
    sender = form_data.get("From")

    # Store every incoming message
    store_message(sender, whatsapp_message)

    # Command parsing
    if whatsapp_message.strip().lower() == "summarize unread":
        unread_messages = get_unread_messages(sender)
        if not unread_messages:
            summary = "No unread messages to summarize."
        else:
            text = "\n".join([msg["body"] for msg in unread_messages])
            try:
                response = requests.post(
                    "http://llm_service:8001/summarize",  # Correct port
                    json={"text": text},
                    timeout=20
                )
                response.raise_for_status()
                summary = response.json().get("summary", "Sorry, I couldn't summarize that.")
                mark_messages_as_read(sender)
            except Exception as e:
                summary = f"Error summarizing: {str(e)}"
    else:
        # Default: summarize the incoming message only
        try:
            response = requests.post(
                "http://llm_service:8001/summarize",
                json={"text": whatsapp_message},
                timeout=20
            )
            response.raise_for_status()
            summary = response.json().get("summary", "Sorry, I couldn't summarize that.")
        except Exception as e:
            summary = f"Error summarizing: {str(e)}"

    # Send summary back to user via Twilio
    try:
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        client.messages.create(
            body=f"Summary:\n{summary}",
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=sender,
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Failed to send WhatsApp message: {str(e)}"}
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Summary sent."})

# FastAPI app
app = FastAPI()
app.include_router(router)
