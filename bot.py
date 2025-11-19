import time
import requests
import telebot
import threading
import os
from flask import Flask

# ========== ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_KEY = os.environ.get("STEAM_API_KEY")
TARGET_STEAM_ID = os.environ.get("TARGET_STEAM_ID")
YOUR_TELEGRAM_ID = os.environ.get("TELEGRAM_ID")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден. Проверь Environment Variables на Render!")

bot = telebot.TeleBot(BOT_TOKEN)

# ========== ФЕЙКОВЫЙ ВЕБ-СЕРВЕР ДЛЯ RENDER ==========
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ========== ФУНКЦИЯ ПРОВЕРКИ ДРУЗЕЙ ==========
def get_friend_count():
    url = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={API_KEY}&steamid={TARGET_STEAM_ID}"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        if "friendslist" not in data:
            return 0
        return len(data["friendslist"]["friends"])
    except Exception as e:
        print("Ошибка Steam API:", e)
        return None

# ========== ОБРАБОТЧИК START ==========
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Бот отслеживает количество друзей 24/7.")

# ========== МОНИТОРИНГ ==========
def monitor():
    last_count = None
    while True:
        count = get_friend_count()
        if count is not None:
            print("Друзей:", count)

            if last_count is None:
                last_count = count

            if count < last_count:
                bot.send_message(
                    YOUR_TELEGRAM_ID,
                    f"⚠️ У пользователя стало меньше друзей: было {last_count}, стало {count}"
                )

            last_count = count

        time.sleep(60)

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    threading.Thread(target=monitor, daemon=True).start()
    bot.polling(none_stop=True)
