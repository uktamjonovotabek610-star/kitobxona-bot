import telebot

BOT_TOKEN = "8399444316:AAF6Kp8CSo2MUl6E_gxA2vKrRz0vbQvCh3Y"

bot = telebot.TeleBot(BOT_TOKEN)

kitoblar = [
    {
        "nomi": "O'tkan kunlar",
        "muallif": "Abdulla Qodiriy",
        "narx": "25000 som",
        "sahifa": 430,
        "janr": "Roman",
        "mavjud": True
    },
    {
        "nomi": "Mehrobdan chayon",
        "muallif": "Abdulla Qodiriy",
        "narx": "22000 som",
        "sahifa": 380,
        "janr": "Roman",
        "mavjud": True
    },
    {
        "nomi": "Sariq devni minib",
        "muallif": "Xurshid Davron",
        "narx": "18000 som",
        "sahifa": 290,
        "janr": "Fantastika",
        "mavjud": False
    },
]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 
        "Kitobxona botiga xush kelibsiz!\n\nKitob nomini yozing!")

@bot.message_handler(func=lambda m: True)
def kitob_qidir(message):
    sorov = message.text.lower()
    topildi = False
    
    for kitob in kitoblar:
        if sorov in kitob["nomi"].lower():
            mavjud = "Mavjud" if kitob["mavjud"] else "Mavjud emas"
            javob = (
                f"Kitob: {kitob['nomi']}\n"
                f"Muallif: {kitob['muallif']}\n"
                f"Narxi: {kitob['narx']}\n"
                f"Sahifalar: {kitob['sahifa']}\n"
                f"Janr: {kitob['janr']}\n"
                f"Holat: {mavjud}"
            )
            bot.send_message(message.chat.id, javob)
            topildi = True
    
    if not topildi:
        bot.send_message(message.chat.id, "Kitob topilmadi!")

bot.polling()