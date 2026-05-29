import os
import requests
import base64
import time
import threading
from flask import Flask

TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

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
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"Create a professional YouTube thumbnail image for the topic: '{text}'. Make it vibrant, eye-catching with bold visuals."
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseModalities": ["IMAGE", "TEXT"]
            }
        }

        response = requests.post(url, json=payload, timeout=30)
        result = response.json()

        if "candidates" in result:
            parts = result["candidates"][0]["content"]["parts"]
            for part in parts:
                if "inlineData" in part:
                    image_bytes = base64.b64decode(part["inlineData"]["data"])
                    tg_url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
                    requests.post(tg_url, data={"chat_id": chat_id}, files={"photo": ("thumb.jpg", image_bytes, "image/jpeg")})
                    return
            send_text(chat_id, "Image generate nahi hui, dobara try karo.")
        else:
            send_text(chat_id, f"API Error: {str(result)[:200]}")

    except Exception as e:
        send_text(chat_id, f"Error: {str(e)}")

def polling():
    print("Polling start...")
    offset = None
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
                            send_text(chat_id, "🎨 Gemini AI Thumbnail Generator\n\nMujhe apna topic batao, main seedhe real image generate karke bhejunga.")
                        elif text:
                            send_text(chat_id, f"🎨 Gemini AI aapke prompt '{text}' par kaam kar raha hai. Image generate ho rahi hai...")
                            create_and_send_thumbnail(chat_id, text)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    t = threading.Thread(target=polling, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=port)
