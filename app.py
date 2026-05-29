import os
import requests
from flask import Flask, request
from PIL import Image, ImageDraw, ImageFont

TOKEN = "8658574106:AAHK-04fYQxC0u1H-ZcOWtxKf8bC_cuKYyY"
# Aapka naya Render URL yahan set kar diya hai
WEBHOOK_URL = "https://thumbnail-bot-ljn8.onrender.com"

app = Flask(__name__)

# Premium Bold Font Download karne ka jugaad taaki text Nano Banana jaisa bada dikhe
FONT_PATH = "/tmp/bold_font.ttf"
def download_font():
    if not os.path.exists(FONT_PATH):
        try:
            # Internet se ek heavy impact/bold font download kar rahe hain
            font_url = "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf"
            r = requests.get(font_url, stream=True)
            with open(FONT_PATH, 'wb') as f:
                for chunk in r.iter_content(chunk_size=128):
                    f.write(chunk)
        except Exception as e:
            print(f"Font download error: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
        params = {"url": f"{WEBHOOK_URL}/"}
        res = requests.get(telegram_url, params=params).json()
        if res.get("ok"):
            return "<h1>Thumbnail Bot Live on New URL!</h1>", 200
        return f"<h1>Activation Failed: {res.get('description')}</h1>", 500

    if request.method == "POST":
        try:
            data = request.get_json()
            if data and "message" in data:
                message = data["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                if text == "/start":
                    send_message(chat_id, "🔥 New Server Active!\nMujhe apna title bhejiye, main Nano Banana style ka premium thumbnail bana dunga.")
                elif text:
                    send_message(chat_id, f"⚡ '{text}' par high-quality thumbnail ban raha hai...")
                    create_and_send_thumbnail(chat_id, text)
        except Exception as e:
            print(f"Error: {e}")
        return "OK", 200

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def create_and_send_thumbnail(chat_id, text):
    try:
        download_font()
        
        # 1. Dark Cyber Background (1280x720 HD)
        img = Image.new('RGB', (1280, 720), color=(10, 11, 18))
        canvas = ImageDraw.Draw(img)
        
        # 2. Tech Borders
        canvas.rectangle([(20, 20), (1260, 700)], outline=(30, 35, 55), width=3)
        canvas.rectangle([(30, 30), (1250, 690)], outline=(18, 22, 35), width=1)

        # 3. Font Load Configuration (Size = 75 for extreme boldness)
        if os.path.exists(FONT_PATH):
            font = ImageFont.truetype(FONT_PATH, 75)
            watermark_font = ImageFont.truetype(FONT_PATH, 22)
        else:
            font = ImageFont.load_default()
            watermark_font = ImageFont.load_default()

        display_text = text.upper()
        
        # Text wrapping adjustments (Agar text lamba ho toh thoda adjust karein)
        x, y = 100, 300

        # Colors for Nano Banana Look
        shadow_color = (0, 0, 0)       # Deep Black Shadow
        glow_color = (0, 229, 255)     # Neon Cyan Glow
        main_color = (255, 235, 59)    # Bright Yellow

        # 4. HACK: Neon Glow Effect (Cyan border overlay behind text)
        for dx in range(-6, 7, 2):
            for dy in range(-6, 7, 2):
                canvas.text((x + dx, y + dy), display_text, fill=glow_color, font=font)

        # 5. HACK: Solid Black 3D Shadow (Thick border over glow)
        for dx in range(-3, 4, 1):
            for dy in range(-3, 4, 1):
                canvas.text((x + dx, y + dy), display_text, fill=shadow_color, font=font)

        # 6. Main Text Overlay (Yellow Center)
        canvas.text((x, y), display_text, fill=main_color, font=font)
        
        # Premium Watermark
        canvas.text((1050, 650), "CREATIVE BOT", fill=(50, 60, 90), font=watermark_font)

        # 7. Temporary Save
        output_path = f"/tmp/banana_{chat_id}.jpg"
        img.save(output_path, "JPEG", quality=100)
        
        # 8. Send to Telegram
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        with open(output_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id, 'caption': "✅ Aapka Nano Banana Style 3D Thumbnail Taiyar Hai!"}
            requests.post(url, data=data, files=files)
            
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        send_message(chat_id, f"❌ Design Error: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
