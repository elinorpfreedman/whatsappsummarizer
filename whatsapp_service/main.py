from fastapi import FastAPI
from whatsapp_webhook import router

app = FastAPI()
app.include_router(router)
