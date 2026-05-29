import os
import requests
import base64
import threading
from flask import Flask, request

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

app = Flask(__name__)

# =========================
# HOME ROUTE
# =========================
@app.route("/")
def home():
    return "Thumbnail Bot Running 🚀", 200

# =========================
# SEND TEXT MESSAGE
# =========================
def send_text(chat_id, text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    requests.post(url, json=payload)

# =========================
# SEND PHOTO
# =========================
def send_photo(chat_id, image_bytes):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    files = {
        "photo": ("thumbnail.png", image_bytes)
    }

    data = {
        "chat_id": chat_id
    }

    requests.post(url, files=files, data=data)

# =========================
# GENERATE THUMBNAIL
# =========================
def create_and_send_thumbnail(chat_id, prompt_text):

    try:

        send_text(chat_id, "🎨 Thumbnail generate ho rahi hai...")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-preview-image-generation:generateContent?key={GEMINI_API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"""
Create a cinematic YouTube thumbnail.

Topic: {prompt_text}

Style:
- Ultra HD
- Viral YouTube Thumbnail
- Eye Catching
- Dramatic Lighting
- Big Bold Text
- Modern Design
- Vibrant Colors
"""
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"]
            }
        }

        response = requests.post(url, json=payload)

        result = response.json()

        print(result)

        candidates = result.get("candidates", [])

        if not candidates:
            send_text(chat_id, "❌ Thumbnail generate nahi hui")
            return

        parts = candidates[0]["content"]["parts"]

        image_found = False

        for part in parts:

            inline_data = part.get("inlineData")

            if inline_data:

                image_data = inline_data.get("data")

                if image_data:

                    image_bytes = base64.b64decode(image_data)

                    send_photo(chat_id, image_bytes)

                    image_found = True
                    break

        if not image_found:
            send_text(chat_id, "❌ Image response nahi mila")

    except Exception as e:

        print("ERROR:", e)

        send_text(chat_id, f"❌ Error: {str(e)}")

# =========================
# WEBHOOK
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():

    try:

        data = request.json

        print(data)

        if "message" in data:

            message = data["message"]

            chat_id = message["chat"]["id"]

            text = message.get("text", "")

            if text == "/start":

                welcome = """
🔥 Welcome To Thumbnail Bot

Koi bhi topic bhejo.

Example:
- Mahabharat War
- Gaming
- Tech
- Motivation

AI thumbnail generate ho jayegi 🚀
"""

                send_text(chat_id, welcome)

            else:

                threading.Thread(
                    target=create_and_send_thumbnail,
                    args=(chat_id, text)
                ).start()

        return "OK", 200

    except Exception as e:

        print(e)

        return "ERROR", 500

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
