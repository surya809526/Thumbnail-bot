import os
import requests
from flask import Flask, request

TOKEN = "8658574106:AAECNWhaETFOi82yf8FU5Uh42OdvYI2SdxY"
WEBHOOK_URL = "https://thumbnail-bot-ljn8.onrender.com"

app = Flask(__name__)

def translate_hindi_to_english(text):
    """Yeh function aapki Roman-Hindi ya Shuddh Hindi ko automatic English mein badal dega"""
    try:
        # Using a free translation API endpoint
        api_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={requests.utils.quote(text)}"
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            translated_text = "".join([sentence[0] for sentence in result[0]])
            return translated_text
    except Exception as e:
        print(f"Translation Error: {e}")
    return text  # Fallback to original text if translation fails

@app.route("/", methods=["GET", "POST", "HEAD"])
def index():
    if request.method == "HEAD":
        return "OK", 200

    if request.method == "GET":
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
        params = {"url": f"{WEBHOOK_URL}/"}
        res = requests.get(telegram_url, params=params).json()
        if res.get("ok"):
            return "<h1>Hindi AI Thumbnail Bot Live!</h1>", 200
        return f"<h1>Failed: {res.get('description')}</h1>", 500

    if request.method == "POST":
        try:
            data = request.get_json()
            if data and "message" in data:
                message = data["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                if text == "/start":
                    send_message(chat_id, "🚀 Hindi AI Thumbnail Bot Active!\n\nAap apni aam Hindi/Hinglish mein apna idea likhiye (Jaise: 'ek horror bhoot wali thumbnail bana do'), code use automatic English karke mast photo bhejega!")
                elif text:
                    # 🔄 AUTOMATIC TRANSLATION HAPPENING HERE
                    english_prompt = translate_hindi_to_english(text)
                    
                    # Bot user ko dikhaayega ki usne kya samjha
                    send_message(chat_id, f"🎨 Aapka Idea: '{text}'\n🤖 Translation: '{english_prompt}'\n\nThumbnail render ho raha hai, thoda intezar karein...")
                    
                    generate_and_send_fast_image(chat_id, english_prompt)
        except Exception as e:
            print(f"Webhook Error: {e}")
        return "OK", 200

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def generate_and_send_fast_image(chat_id, english_prompt):
    try:
        # Clean and enhance the translated prompt
        cleaned_prompt = requests.utils.quote(english_prompt)
        enhanced_prompt = f"{cleaned_prompt},cinematic%20lighting,highly%20detailed%203d%20render,gaming%20thumbnail%20background,vibrant%20colors,sharp%20focus,8k,no%20text"

        # Direct stable FLUX model URL via Pollinations
        image_url = f"https://image.pollinations.ai/p/{enhanced_prompt}?width=1280&height=720&model=flux&seed=105"

        # Fetch image bytes directly with a safe 30s timeout
        response = requests.get(image_url, timeout=30)

        if response.status_code == 200:
            output_path = f"/tmp/fast_thumb_{chat_id}.jpg"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # Send to Telegram
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            with open(output_path, 'rb') as photo:
                files = {'photo': photo}
                data = {'chat_id': chat_id, 'caption': f"✅ Aapka AI Thumbnail Taiyar!"}
                requests.post(url, data=data, files=files)
                
            if os.path.exists(output_path):
                os.remove(output_path)
        else:
            send_message(chat_id, f"❌ Engine Busy (Status: {response.status_code}). Kripya thodi der baad dobara try karein.")
            
    except Exception as e:
        send_message(chat_id, f"❌ Generation Error: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
