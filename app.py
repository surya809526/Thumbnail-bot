import os
import requests
import base64
from flask import Flask, request
from PIL import Image, ImageDraw, ImageFont
import io

TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://thumbnail-bot-1.onrender.com")
GEMINI_API_KEY = os.environ.get("AIzaSyBFeOH1yQXWsgcoGmp3zwIHzJ8huDwWltk")

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!", 200

@app.route("/setup")
def setup_webhook():
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    params = {"url": f"{WEBHOOK_URL}/webhook"}
    response = requests.get(telegram_url, params=params).json()
    if response.get("ok"):
        return "Webhook Set Successfully!", 200
    return f"Webhook Failed: {response.get('description')}", 500

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if data and "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        if text == "/start":
            send_text(chat_id, "Hi! Koi bhi topic bhejo, main ek YouTube thumbnail bana dunga! 🎨")
        elif text:
            send_text(chat_id, "⏳ Thumbnail ban raha hai, thoda wait karo...")
            create_and_send_thumbnail(chat_id, text)
    return "OK", 200

def send_text(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def create_and_send_thumbnail(chat_id, text):
    try:
        # Gemini image generation API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={GEMINI_API_KEY}"
        
        prompt = f"YouTube thumbnail for '{text}', professional, eye-catching, bold text, vibrant colors, cinematic lighting, high quality, 16:9 aspect ratio"
        
        payload = {
            "instances": [
                {"prompt": prompt}
            ],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "16:9"
            }
        }
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        # Image extract karo
        image_data = result["predictions"][0]["bytesBase64Encoded"]
        image_bytes = base64.b64decode(image_data)
        
        # Telegram pe bhejo
        tg_url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        requests.post(tg_url, data={"chat_id": chat_id}, files={"photo": ("thumb.jpg", image_bytes, "image/jpeg")})

    except Exception as e:
        send_text(chat_id, f"❌ Error: {str(e)}")
        send_text(chat_id, "Gemini API issue hai, thodi der baad try karo.")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
