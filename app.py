import os
import requests
import base64
from flask import Flask, request

TOKEN = "8658574106:AAHK-04fYQxC0u1H-ZcOWtxKf8bC_cuKYyY"
WEBHOOK_URL = "https://thumbnail-bot-ljn8.onrender.com"

# ⚠️ Yahan apni asli Gemini Key quotes ke andar paste kijiye
GEMINI_API_KEY = "AIzaSyBFeOH1yQXWsgcoGmp3zwIHzJ8huDwWltk"

app = Flask(__name__)

@app.route("/", methods=["GET", "POST", "HEAD"])
def index():
    if request.method == "HEAD":
        return "OK", 200

    if request.method == "GET":
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
        params = {"url": f"{WEBHOOK_URL}/"}
        res = requests.get(telegram_url, params=params).json()
        if res.get("ok"):
            return "<h1>Gemini Direct API Generator Live!</h1>", 200
        return f"<h1>Failed: {res.get('description')}</h1>", 500

    if request.method == "POST":
        try:
            data = request.get_json()
            if data and "message" in data:
                message = data["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                if text == "/start":
                    send_message(chat_id, "🚀 Gemini AI Thumbnail Generator Active!\n\nMujhe apna topic batao, main seedhe real image generate karke bhejunga.")
                elif text:
                    send_message(chat_id, f"🎨 Gemini AI aapke prompt '{text}' par kaam kar raha hai. Image generate ho rahi hai...")
                    generate_and_send_direct_image(chat_id, text)
        except Exception as e:
            print(f"Webhook Error: {e}")
        return "OK", 200

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def generate_and_send_direct_image(chat_id, user_prompt):
    try:
        # Prompt enhancement for high-quality thumbnail feel
        enhanced_prompt = f"{user_prompt}, cinematic lighting, 3d render style, vibrant colors, gaming thumbnail accent, sharp focus, 8k resolution"

        # FIXED: Core correct REST API endpoint for Gemini Imagen
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:generateImages?key={GEMINI_API_KEY}"
        
        headers = {"Content-Type": "application/json"}
        payload = {
            "prompt": {"text": enhanced_prompt},
            "numberOfImages": 1,
            "outputMimeType": "image/jpeg",
            "aspectRatio": "16:9"
        }

        # Backup try with alternative model name if 404 occurs
        response = requests.post(api_url, json=payload, headers=headers)
        
        # Agar fir bhi 404 aaye toh stable/alpha endpoint track karein
        if response.status_code == 404:
            alt_url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-alpha-002:generateImages?key={GEMINI_API_KEY}"
            response = requests.post(alt_url, json=payload, headers=headers)

        if response.status_code != 200:
            send_message(chat_id, f"❌ Google API Error (Status {response.status_code}): {response.text}")
            return

        res_data = response.json()

        if "generatedImages" in res_data:
            img_b64 = res_data["generatedImages"][0]["image"]["imageBytes"]
            image_bytes = base64.b64decode(img_b64)

            output_path = f"/tmp/gemini_thumb_{chat_id}.jpg"
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
            
            # Send to Telegram
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            with open(output_path, 'rb') as photo:
                files = {'photo': photo}
                data = {'chat_id': chat_id, 'caption': f"✅ Gemini AI Thumbnail Taiyar!\nPrompt: '{user_prompt}'"}
                requests.post(url, data=data, files=files)
                
            if os.path.exists(output_path):
                os.remove(output_path)
        else:
            send_message(chat_id, f"❌ Response Error: {str(res_data)}")
            
    except Exception as e:
        send_message(chat_id, f"❌ Code Error: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
