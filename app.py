import os
import requests
from flask import Flask, request

TOKEN = "8658574106:AAECNWhaETFOi82yf8FU5Uh42OdvYI2SdxY"
WEBHOOK_URL = "https://thumbnail-bot-ljn8.onrender.com"

# Ab key code mein nahi hai, Render dashboard se load hogi
HF_API_KEY = os.environ.get("HF_API_KEY")

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
            return "<h1>Hugging Face AI Thumbnail Bot Live!</h1>", 200
        return f"<h1>Failed: {res.get('description')}</h1>", 500

    if request.method == "POST":
        try:
            data = request.get_json()
            if data and "message" in data:
                message = data["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                if text == "/start":
                    send_message(chat_id, "🚀 Hugging Face AI Thumbnail Bot Active!\n\nMujhe apna idea bhejiye, main image render karke bhejunga.")
                elif text:
                    send_message(chat_id, f"🎨 Hugging Face AI aapke prompt '{text}' par kaam kar raha hai...")
                    generate_and_send_hf_image(chat_id, text)
        except Exception as e:
            print(f"Webhook Error: {e}")
        return "OK", 200

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def generate_and_send_hf_image(chat_id, user_prompt):
    try:
        if not HF_API_KEY:
            send_message(chat_id, "❌ Error: Hugging Face API Key Render par set nahi hai!")
            return

        enhanced_prompt = f"{user_prompt}, cinematic lighting, highly detailed 3d render, gaming thumbnail background, vivid neon colors, sharp focus, 8k resolution, no text"

        API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {"inputs": enhanced_prompt}

        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            output_path = f"/tmp/hf_thumb_{chat_id}.jpg"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            with open(output_path, 'rb') as photo:
                files = {'photo': photo}
                data = {'chat_id': chat_id, 'caption': f"✅ AI Thumbnail Taiyar!\nPrompt: '{user_prompt}'"}
                requests.post(url, data=data, files=files)
                
            if os.path.exists(output_path):
                os.remove(output_path)
        else:
            send_message(chat_id, f"❌ Hugging Face Error (Status {response.status_code}): {response.text}")
            
    except Exception as e:
        send_message(chat_id, f"❌ Code Error: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
