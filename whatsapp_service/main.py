from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.post("/whatsapp-webhook")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    from_number = form.get("From")
    message_body = form.get("Body")

    print(f"Received message from {from_number}: {message_body}")

    # Echo response for now
    return PlainTextResponse("Message received!")
