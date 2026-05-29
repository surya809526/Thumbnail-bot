import os
import requests
from flask import Flask, request

TOKEN = "8658574106:AAECNWhaETFOi82yf8FU5Uh42OdvYI2SdxY"
WEBHOOK_URL = "https://thumbnail-bot-ljn8.onrender.com"

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
            return "<h1>Super Fast AI Thumbnail Bot Live!</h1>", 200
        return f"<h1>Failed: {res.get('description')}</h1>", 500

    if request.method == "POST":
        try:
            data = request.get_json()
            if data and "message" in data:
                message = data["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                if text == "/start":
                    send_message(chat_id, "🚀 AI Thumbnail Bot Active!\nMujhe apna idea bhejiye, main image render karke bhejunga.")
                elif text:
                    send_message(chat_id, f"🎨 '{text}' par ultra-fast thumbnail render ho raha hai...")
                    generate_and_send_fast_image(chat_id, text)
        except Exception as e:
            print(f"Webhook Error: {e}")
        return "OK", 200

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def generate_and_send_fast_image(chat_id, user_prompt):
    try:
        # Prompt clean and boost for cinematic look
        cleaned_prompt = requests.utils.quote(user_prompt)
        enhanced_prompt = f"{cleaned_prompt},cinematic%20lighting,highly%20detailed%203d%20render,gaming%20thumbnail%20background,vibrant%20colors,sharp%20focus,8k,no%20text"

        # Direct stable FLUX model URL via Pollinations (Zero authentication / Zero DNS lag)
        image_url = f"https://image.pollinations.ai/p/{enhanced_prompt}?width=1280&height=720&model=flux&seed=100"

        # Fetch image bytes directly
        response = requests.get(image_url, timeout=30)

        if response.status_code == 200:
            output_path = f"/tmp/fast_thumb_{chat_id}.jpg"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # Send to Telegram
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            with open(output_path, 'rb') as photo:
                files = {'photo': photo}
                data = {'chat_id': chat_id, 'caption': f"✅ AI Thumbnail Taiyar!\nPrompt: '{user_prompt}'"}
                requests.post(url, data=data, files=files)
                
            if os.path.exists(output_path):
                os.remove(output_path)
        else:
            send_message(chat_id, f"❌ Engine Status Error: {response.status_code}")
            
    except Exception as e:
        send_message(chat_id, f"❌ Generation Error: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
