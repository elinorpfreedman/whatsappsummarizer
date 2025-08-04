from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import datetime

# Replace with your local FastAPI endpoint
STORE_ENDPOINT = "http://localhost:8002/store"  # Adjust if your message_storage_service uses another port

# Set up the browser
options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=selenium")
options.add_argument("--profile-directory=Default")  # So you can stay logged into WhatsApp
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Go to WhatsApp Web
driver.get("https://web.whatsapp.com")
input("👀 Scan the QR code and then press Enter...")

# --- Select chat ---
target_chat = "Karisseñior👴🏼 (🦘🦎🦍)"

# Search and click
search_box = driver.find_element(By.XPATH, '//div[@title="Search input textbox"]')
search_box.click()
search_box.send_keys(target_chat)
time.sleep(2)

chat = driver.find_element(By.XPATH, f'//span[@title="{target_chat}"]')
chat.click()

# --- Scrape messages (you can improve this later with loops or state tracking) ---
messages = driver.find_elements(By.XPATH, '//div[contains(@class,"message-in")]')
for msg in messages[-5:]:  # Just scrape the last 5 messages to start
    try:
        text_element = msg.find_element(By.XPATH, './/span[@class="selectable-text copyable-text"]')
        text = text_element.text
        timestamp = datetime.datetime.now().isoformat()
        sender = "Someone"  # You can try to parse the sender from the message
        chat_name = target_chat

        print(f"📩 {text}")

        # Send to storage service
        res = requests.post(STORE_ENDPOINT, json={
            "timestamp": timestamp,
            "sender": sender,
            "text": text,
            "chat_name": chat_name
        })
        print(f"✅ Stored: {res.status_code}")
    except Exception as e:
        print("⚠️ Failed to process message:", e)
