import os
import requests
from flask import Flask, request
from PIL import Image, ImageDraw

# Ekdum sahi aur full token lagaya hai variable ke sath
TOKEN = "8658574106:AAGwEZPs-ghetLDXVV1YJXqyUhHYHHaYGS4"
WEBHOOK_URL = "https://thumbnail-bot-1.onrender.com"

app = Flask(__name__)

@app.route("/")
def setup_webhook():
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    params = {"url": f"{WEBHOOK_URL}/webhook"}
    response = requests.get(telegram_url, params=params).json()
    if response.get("ok"):
        return "Webhook Set Successfully Via Telegram API!", 200
    return f"Webhook Failed: {response.get('description')}", 500

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if data and "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if text == "/start":
            send_text(chat_id, "Hi Swaraj! Mujhe koi bhi text likh kar bhejo, main uska ek thumbnail banner bana dunga.")
        elif text:
            create_and_send_thumbnail(chat_id, text)
            
    return "OK", 200

def send_text(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def create_and_send_thumbnail(chat_id, text):
    try:
        img = Image.new('RGB', (1280, 720), color=(20, 20, 35))
        canvas = ImageDraw.Draw(img)
        canvas.text((100, 320), f"Title: {text}", fill=(255, 215, 0))
        
        output_path = f"/tmp/thumb_{chat_id}.jpg"
        img.save(output_path)
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        with open(output_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id}
            requests.post(url, data=data, files=files)
            
        if os.path.exists(output_path):
            os.remove(output_path)
    except Exception as e:
        send_text(chat_id, f"Error: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
