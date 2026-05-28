import os
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw

# Naya Bot Token yahan dalein
TOKEN = "8658574106:AAGwEzPs-ghetLDXVV1YJXqyUhHYHHaYGS4"
# Aapka Render URL (Bina aakhiri slash ke)
WEBHOOK_URL = "https://thumbnail-bot-1.onrender.com"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Base route sirf check karne ke liye ki server chal raha hai ya nahi
@app.route("/")
def webhook():
    bot.remove_webhook()
    # Direct base URL par hi webhook set kar rahe hain bina token ke jhanjhat ke
    status = bot.set_webhook(url=WEBHOOK_URL + '/webhook')
    if status:
        return "Webhook Set Successfully!", 200
    return "Webhook Failed to Set.", 500

# Telegram saare messages isi route par bhejega
@app.route('/webhook', methods=['POST'])
def getMessage():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        return "Invalid Request", 403

# Telegram Bot Commands
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.reply_to(message, "Hi! Mujhe koi bhi text likh kar bhejo, main uska ek thumbnail banner bana dunga.")
    except Exception as e:
        print(f"Error in start command: {e}")

@bot.message_handler(func=lambda message: True)
def create_thumbnail(message):
    text = message.text
    chat_id = message.chat.id
    
    try:
        # 1. Blank image (1280x720)
        img = Image.new('RGB', (1280, 720), color=(20, 20, 35))
        canvas = ImageDraw.Draw(img)
        
        # 2. Draw text without custom font
        canvas.text((100, 320), f"Title: {text}", fill=(255, 215, 0)) 
        
        # 3. Temp path for Linux
        output_path = f"/tmp/thumb_{chat_id}.jpg"
        img.save(output_path)
        
        # 4. Send to user
        with open(output_path, 'rb') as photo:
            bot.send_photo(chat_id, photo)
            
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        print(f"Error creating thumbnail: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
