import os
import requests
import base64
import time
import threading
from flask import Flask

TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("AIzaSyBFeOH1yQXWsgcoGmp3zwIHzJ8huDwWltk")

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    return "OK", 200

def send_text(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def create_and_send_thumbnail(chat_id, text):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={GEMINI_API_KEY}"
        prompt = f"YouTube thumbnail for '{text}', professional, eye-catching, vibrant colors, cinematic lighting, high quality, 16:9 aspect ratio"
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {"sampleCount": 1, "aspectRatio": "16:9"}
        }
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()

        if "predictions" not in result:
            send_text(chat_id, f"Gemini Error: {str(result)[:300]}")
            return

        image_data = result["predictions"][0]["bytesBase64Encoded"]
        image_bytes = base64.b64decode(image_data)

        tg_url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        requests.post(tg_url, data={"chat_id": chat_id}, files={"photo": ("thumb.jpg", image_bytes, "image/jpeg")})

    except Exception as e:
        send_text(chat_id, f"Error: {str(e)}")

def polling():
    print("Polling start...")
    offset = None
    # Webhook delete karo
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true")
    time.sleep(2)

    while True:
        try:
            params = {"timeout": 30, "offset": offset}
            response = requests.get(
                f"https://api.telegram.org/bot{TOKEN}/getUpdates",
                params=params,
                timeout=35
            )
            updates = response.json()

            if updates.get("ok") and updates.get("result"):
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        text = message.get("text", "")
                        if text == "/start":
                            send_text(chat_id, "Hi! Koi bhi topic bhejo, main YouTube thumbnail bana dunga!")
                        elif text:
                            send_text(chat_id, "Thumbnail ban raha hai...")
                            create_and_send_thumbnail(chat_id, text)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)

# Gunicorn ke saath bhi polling start ho
t = threading.Thread(target=polling, daemon=True)
t.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
