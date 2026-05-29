import os
import requests
from flask import Flask, request
# Google Gemini Generative AI Package
import google.generativeai as genai

TOKEN = "8658574106:AAHK-04fYQxC0u1H-ZcOWtxKf8bC_cuKYyY"
WEBHOOK_URL = "https://thumbnail-bot-ljn8.onrender.com"

# Aapki Gemini API Key yahan lagegi
GEMINI_API_KEY = "AIzaSyBFeOH1yQXWsgcoGmp3zwIHzJ8huDwWltk"

app = Flask(__name__)

# API Configuration
genai.configure(api_key=GEMINI_API_KEY)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
        params = {"url": f"{WEBHOOK_URL}/"}
        res = requests.get(telegram_url, params=params).json()
        if res.get("ok"):
            return "<h1>Gemini Imagen Generator Live!</h1>", 200
        return f"<h1>Failed: {res.get('description')}</h1>", 500

    if request.method == "POST":
        try:
            data = request.get_json()
            if data and "message" in data:
                message = data["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                if text == "/start":
                    send_message(chat_id, "🚀 Gemini AI Thumbnail Generator Active!\n\nMujhe apna idea ya scene batao, main seedhe high-quality image render karke bhejunga.")
                elif text:
                    send_message(chat_id, f"🎨 Gemini AI aapke prompt '{text}' par kaam kar raha hai. Image generate ho rahi hai...")
                    generate_and_send_gemini_image(chat_id, text)
        except Exception as e:
            print(f"Webhook Error: {e}")
        return "OK", 200

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def generate_and_send_gemini_image(chat_id, user_prompt):
    try:
        # Prompt enhancement for Gaming/Tech Youtube channels vibe
        enhanced_prompt = f"{user_prompt}, cinematic lighting, 3d render style, vibrant colors, gaming thumbnail accent, sharp focus, 8k resolution"

        # FIXED: Core correct module call for Google Imagen
        model = genai.ImageGenerationModel("imagen-3.0-generate-002")
        
        result = model.generate_images(
            prompt=enhanced_prompt,
            number_of_images=1,
            aspect_ratio="16:9" # Perfect fit for YouTube thumbnail size
        )

        # Extract image content bytes directly
        generated_image = result.images[0]
        image_bytes = generated_image.image.image_bytes

        output_path = f"/tmp/gemini_thumb_{chat_id}.png"
        with open(output_path, 'wb') as f:
            f.write(image_bytes)
        
        # Send photo to Telegram
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        with open(output_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id, 'caption': f"✅ Gemini AI Thumbnail Taiyar!\nPrompt: '{user_prompt}'"}
            requests.post(url, data=data, files=files)
            
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        send_message(chat_id, f"❌ Gemini Generation Error: {str(e)}\n\n(Check kariye ki code up to date hai aur API key perfectly lagayi hai na)")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
