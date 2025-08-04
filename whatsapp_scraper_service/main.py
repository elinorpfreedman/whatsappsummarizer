from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import tempfile
import requests
import time

options = Options()
options.add_argument("--headless=new")  # required in latest Chrome
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Create unique Chrome user profile dir
user_data_dir = tempfile.mkdtemp()
options.add_argument(f"--user-data-dir={user_data_dir}")

driver = webdriver.Chrome(options=options)

try:
    print("Opening WhatsApp Web...")
    driver.get("https://web.whatsapp.com")

    # Wait for manual QR scan via VNC or X display
    print("Scan the QR code in the VNC window.")
    input("Press Enter once logged in...")

    print("✅ Logged in! Starting message scraping loop.")
    while True:
        messages = driver.find_elements(By.CLASS_NAME, "_21Ahp")  # This may need updating later
        for message in messages:
            text = message.text.strip()
            if text:
                print("📤 Sending:", text)
                try:
                    response = requests.post(
                        "http://message_storage_service:8002/messages", 
                        json={"text": text}
                    )
                    print(f"✅ Sent: {response.status_code}")
                except Exception as e:
                    print(f"❌ Failed to send message: {e}")
        time.sleep(10)

finally:
    driver.quit()
