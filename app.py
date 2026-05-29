import os
import requests
from flask import Flask, request
from PIL import Image, ImageDraw, ImageFont

TOKEN = "8658574106:AAHK-04fYQxC0u1H-ZcOWtxKf8bC_cuKYyY"
WEBHOOK_URL = "https://thumbnail-bot-1.onrender.com"

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
        params = {"url": f"{WEBHOOK_URL}/"}
        res = requests.get(telegram_url, params=params).json()
        if res.get("ok"):
            return "<h1>Thumbnail Bot Webhook Connected!</h1>", 200
        return f"<h1>Failed: {res.get('description')}</h1>", 500

    if request.method == "POST":
        data = request.get_json()
        if data and "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")

            if text == "/start":
                send_message(chat_id, "🔥 Swaraj's Thumbnail Generator Active!\n\nMujhe apna title bhejiye, main Nano Banana style ka premium thumbnail bana dunga.")
            elif text:
                # User ko update bhein
                send_message(chat_id, f"⚡ '{text}' par Nano Banana style thumbnail ban raha hai...")
                create_and_send_thumbnail(chat_id, text)
        return "OK", 200

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def create_and_send_thumbnail(chat_id, text):
    try:
        # 1. Premium Dark Background (1280x720 HD)
        # Nano Banana style dark bluish-grey cyber vibe color
        img = Image.new('RGB', (1280, 720), color=(13, 14, 23))
        canvas = ImageDraw.Draw(img)
        
        # 2. Border Lines/Design Grids (For modern premium feel)
        canvas.rectangle([(20, 20), (1260, 700)], outline=(35, 40, 65), width=3)
        canvas.rectangle([(40, 40), (1240, 680)], outline=(25, 30, 50), width=1)

        # 3. Text Formatting (Uppercase for heavy impact)
        display_text = text.upper()
        
        # 4. Built-in font optimization for Linux/Render environment
        try:
            # Agar system default heavy font use karna chahein
            font = ImageFont.load_default()
        except:
            font = None

        # 5. Drawing Drop Shadow Effect (Peeche dark blur effect dene ke liye)
        shadow_offset = 6
        shadow_color = (10, 10, 15)
        
        # Multiple offsets to create a solid bold background text overlay without custom fonts
        for dx in range(-6, 7, 2):
            for dy in range(-6, 7, 2):
                canvas.text((100 + dx, 320 + dy), display_text, fill=shadow_color, font=font, font_size=75)

        # 6. Neon Accents & Main Glow Text (Nano Banana Yellow/Cyan Hybrid look)
        # Main text overlay in striking Cyber Yellow
        canvas.text((100, 320), display_text, fill=(255, 215, 0), font=font, font_size=75)

        # 7. Add a subtle premium watermark at bottom right
        canvas.text((1080, 650), "CREATIVE BOT", fill=(75, 85, 120), font=font, font_size=20)

        # 8. Temporary Save
        output_path = f"/tmp/banana_{chat_id}.jpg"
        img.save(output_path, "JPEG", quality=100)
        
        # 9. Send to user via Telegram API
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        with open(output_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id, 'caption': "✅ Aapka Thumbnail Taiyar Hai!"}
            requests.post(url, data=data, files=files)
            
        # 10. Clean up space
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        send_message(chat_id, f"❌ Thumbnail generation failed: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
