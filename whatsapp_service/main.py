# whatsapp_service/main.py
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
import os
from twilio.rest import Client
import requests

router = APIRouter()

@router.post("/twilio/webhook")

async def receive_message(request: Request):
    form_data = await request.form()
    whatsapp_message = form_data.get("Body")
    sender = form_data.get("From")

    # Call the LLM microservice
    response = requests.post(
        "http://llm_service:8000/summarize",
        json={"text": whatsapp_message}
    )
    summary = response.json().get("summary", "Sorry, I couldn't summarize that.")

    client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    client.messages.create(
        body=f"Summary:\n{summary}",
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        to=sender,
    )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Summary sent."})
