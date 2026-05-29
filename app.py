import os
import requests
from flask import Flask, request
# Google Gemini Library
import google.generativeai as genai

# Telegram Configuration
TOKEN = "8658574106:AAHK-04fYQxC0u1H-ZcOWtxKf8bC_cuKYyY"
WEBHOOK_URL = "https://thumbnail-bot-ljn8.onrender.com"

# 🔑 GEMINI API KEY 🔑
# Google AI Studio (aistudio.google.com) se apni free API Key nikal kar yahan dalein
GEMINI_API_KEY = "AIzaSyBFeOH1yQXWsgcoGmp3zwIHzJ8huDwWltk"

app = Flask(__name__)

# Gemini ko configure karein
genai.configure(api_key=GEMINI_API_KEY)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
        params = {"url": f"{WEBHOOK_URL}/"}
        res = requests.get(telegram_url, params=params).json()
        if res.get("ok"):
            return "<h1>Gemini AI Thumbnail Generator Live!</h1>", 200
        return f"<h1>Activation Failed: {res.get('description')}</h1>", 500

    if request.method == "POST":
        try:
            data = request.get_json()
            if data and "message" in data:
                message = data["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                if text == "/start":
                    send_message(chat_id, "🚀 Swaraj's Gemini AI Bot Active!\n\nMujhe koi bhi thumbnail ka scene ya prompt likh kar bhejo (Hindi ya English mein), main seedhe Nano Banana style ki real AI image generate karunga!")
                elif text:
                    send_message(chat_id, f"🎨 Gemini AI aapke prompt '{text}' par kaam kar raha hai. Image generate ho rahi hai, thoda intezar karein...")
                    generate_and_send_gemini_image(chat_id, text)
        except Exception as e:
            print(f"Server Error: {e}")
        return "OK", 200

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def generate_and_send_gemini_image(chat_id, user_prompt):
    try:
        # Step 1: Nano Banana touch dene ke liye prompt ko piche se enhance karte hain
        enhanced_prompt = f"{user_prompt}, cinematic lighting, highly detailed 3D render, gaming thumbnail style, vivid colors, sharp focus, 8k resolution"

        # Step 2: Google ke latest Imagen model ko call karna image generate karne ke liye
        model = genai.GenerativeModel('imagen-3.0-generate-002') 
        result = model.generate_images(
            prompt=enhanced_prompt,
            number_of_images=1,
            aspect_ratio="16:9" # YouTube thumbnail ka standard size ratio
        )

        # Step 3: Generated image ke bytes nikalna
        generated_image = result.images[0]
        image_bytes = generated_image.bytes

        # Step 4: Temporary file save karna taaki Telegram par upload ho sake
        output_path = f"/tmp/gemini_gen_{chat_id}.png"
        with open(output_path, 'wb') as f:
            f.write(image_bytes)
        
        # Step 5: Telegram API ke zariye user ko photo bhejna
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        with open(output_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id, 'caption': f"✅ Gemini AI Generated:\n'{user_prompt}'"}
            requests.post(url, data=data, files=files)
            
        # Step 6: Temporary file delete karna
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        send_message(chat_id, f"❌ Gemini Generation Error: {str(e)}\n\n(Check karein ki aapki API Key sahi hai ya nahi ya billing set hai ya nahi)")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
