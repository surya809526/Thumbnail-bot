import os
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw

# Bot Token setup
TOKEN = "8839027706:AAHlA1D-FnOvJw_Az-XA9uLul5dB1JYKKCo"
# Render ka URL deploy hone ke baad milega, abhi ise aise hi chhod dein
WEBHOOK_URL = "https://thumbnail-bot-ljn8.onrender.com"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    if WEBHOOK_URL:
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL + '/' + TOKEN)
        return "Webhook Set Successfully!", 200
    return "Bot URL not configured yet.", 200

# Telegram Bot Commands
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi! Mujhe koi bhi text likh kar bhejo, main uska ek cinematic thumbnail banner bana dunga.")

@bot.message_handler(func=lambda message: True)
def create_thumbnail(message):
    text = message.text
    chat_id = message.chat.id
    
    # 1. Ek blank image banayein (1280x720 - YouTube Thumbnail Size)
    img = Image.new('RGB', (1280, 720), color=(20, 20, 35))
    canvas = ImageDraw.Draw(img)
    
    # 2. Text add karein (Default font use hoga)
    canvas.text((80, 320), text, fill=(255, 215, 0)) # Gold color text
    
    # 3. Image save karein
    output_path = f"thumb_{chat_id}.jpg"
    img.save(output_path)
    
    # 4. User ko photo bhejein
    with open(output_path, 'rb') as photo:
        bot.send_photo(chat_id, photo)
        
    # File delete karein takki memory full na ho
    os.remove(output_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
