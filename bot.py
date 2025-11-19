import time
import requests
import telebot
import threading
import os

# === ДАННЫЕ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ===
BOT_TOKEN = os.environ.get("8548746165:AAEUb5fhB_CXBDsvCZWE80NRqOVa6pqM1Cg")
API_KEY = os.environ.get("F76A393AD7354BA04A71E66493D586F8")
TARGET_STEAM_ID = os.environ.get("76561198019556566")
YOUR_TELEGRAM_ID = os.environ.get("819371543")

bot = telebot.TeleBot(BOT_TOKEN)

def get_friend_count():
    url = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={API_KEY}&steamid={TARGET_STEAM_ID}"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        if "friendslist" not in data:
            return 0
        return len(data["friendslist"]["friends"])
    except:
        return None

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Бот работает 24/7 и следит за количеством друзей.")

def monitor():
    last = None
    while True:
        count = get_friend_count()
        if count is not None:
            print("Друзей:", count)

            if last is None:
                last = count

            if count < last:
                bot.send_message(
                    YOUR_TELEGRAM_ID,
                    f"⚠️ Количество друзей уменьшилось: было {last}, стало {count}"
                )

            last = count

        time.sleep(60)

threading.Thread(target=monitor, daemon=True).start()

bot.polling(none_stop=True)
