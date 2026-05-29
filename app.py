import os
import requests
from flask import Flask, request
from PIL import Image, ImageDraw

# Aapka bilkul naya fresh token yahan set kar diya hai
TOKEN = "8658574106:AAHK-04fYQxC0u1H-ZcOWtxKf8bC_cuKYyY"
WEBHOOK_URL = "https://thumbnail-bot-ljn8.onrender.com"

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
        params = {"url": f"{WEBHOOK_URL}/"}
        res = requests.get(telegram_url, params=params).json()
        if res.get("ok"):
            return "<h1>Thumbnail Bot Live! New Token Active.</h1>", 200
        return f"<h1>Failed: {res.get('description')}</h1>", 500

    if request.method == "POST":
        try:
            data = request.get_json()
            if data and "message" in data:
                message = data["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                if text == "/start":
                    send_message(chat_id, "🔥 Swaraj's Thumbnail Generator Active!\n\nMujhe apna title bhejiye, main Nano Banana style ka banner bana dunga.")
                elif text:
                    send_message(chat_id, f"⚡ '{text}' par premium thumbnail ban raha hai...")
                    create_and_send_thumbnail(chat_id, text)
        except Exception as e:
            print(f"Error in webhook processing: {e}")
        return "OK", 200

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending message: {e}")

def create_and_send_thumbnail(chat_id, text):
    try:
        # 1. Dark Premium Cyber Background (1280x720)
        img = Image.new('RGB', (1280, 720), color=(13, 14, 23))
        canvas = ImageDraw.Draw(img)
        
        # 2. Modern Design Border Grids
        canvas.rectangle([(20, 20), (1260, 700)], outline=(35, 40, 65), width=3)
        canvas.rectangle([(40, 40), (1240, 680)], outline=(25, 30, 50), width=1)

        display_text = text.upper()
        
        # 3. Nano Banana Text Styling (Thick Shadow & Neon Accent)
        shadow_color = (10, 10, 15)
        main_color = (255, 215, 0) # Cyber Yellow

        # Bold overlapping grid for heavy impact font feel
        for offset_x in range(-4, 5, 2):
            for offset_y in range(-4, 5, 2):
                canvas.text((100 + offset_x, 320 + offset_y), f"▶  {display_text}", fill=shadow_color)
                
        # Main neon text overlay
        canvas.text((100, 320), f"▶  {display_text}", fill=main_color)
        canvas.text((1050, 650), "CREATIVE BOT", fill=(65, 75, 105))

        # 4. Save to temporary directory
        output_path = f"/tmp/banana_{chat_id}.jpg"
        img.save(output_path, "JPEG", quality=100)
        
        # 5. Send to user via Telegram API
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        with open(output_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id, 'caption': "✅ Aapka Nano Banana Style Thumbnail Taiyar Hai!"}
            requests.post(url, data=data, files=files)
            
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        send_message(chat_id, f"❌ Generation error: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
