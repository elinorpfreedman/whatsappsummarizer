from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Dict
import os
import datetime
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

messages = []

class Message(BaseModel):
    timestamp: datetime.datetime
    sender: str
    text: str
    chat_name: str

@app.post("/store_message")
async def store_message(msg: Message):
    messages.append(msg)
    logging.info(f"📥 Stored message from {msg.sender} in {msg.chat_name}")
    return {"status": "stored"}


@app.get("/messages")
async def get_messages(chat_name: str = None):
    if chat_name:
        return [msg for msg in messages if msg.chat_name == chat_name]
    return messages

@app.get("/group/{group_name}")
async def get_group_messages(group_name: str):
    return {"messages": stored_messages.get(group_name, [])}
