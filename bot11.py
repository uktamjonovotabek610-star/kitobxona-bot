import telebot
import json
import os
from telebot import types
from datetime import datetime, timedelta

# ===================== SOZLAMALAR =====================
BOT_TOKEN = "8399444316:AAF6Kp8CSo2MUl6E_gxA2vKrRz0vbQvCh3Y"
ADMIN_ID = 8527140768
KANAL = "@kitobsevarllar"
KARTA = "9680 3501 4864 2357"
KARTA_EGASI = "Otabek Uktamjonov"

bot = telebot.TeleBot(BOT_TOKEN)

# ===================== JSON FAYLLAR =====================
FILES = {
    "kitoblar.json": [],
    "foydalanuvchilar.json": {},
    "buyurtmalar.json": [],
    "promokodlar.json": {}
}

for file_name, default_data in FILES.items():
    if not os.path.exists(file_name):
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)

with open("kitoblar.json", "r", encoding="utf-8") as f:
    kitoblar = json.load(f)

with open("foydalanuvchilar.json", "r", encoding="utf-8") as f:
    foydalanuvchilar = json.load(f)

with open("buyurtmalar.json", "r", encoding="utf-8") as f:
    buyurtmalar = json.load(f)

with open("promokodlar.json", "r", encoding="utf-8") as f:
    promokodlar = json.load(f)

# ===================== SAQLASH =====================
def saqlash_kitoblar():
    with open("kitoblar.json", "w", encoding="utf-8") as f:
        json.dump(kitoblar, f, ensure_ascii=False, indent=4)

def saqlash_foydalanuvchilar():
    with open("foydalanuvchilar.json", "w", encoding="utf-8") as f:
        json.dump(foydalanuvchilar, f, ensure_ascii=False, indent=4)

def saqlash_buyurtmalar():
    with open("buyurtmalar.json", "w", encoding="utf-8") as f:
        json.dump(buyurtmalar, f, ensure_ascii=False, indent=4)

def saqlash_promokodlar():
    with open("promokodlar.json", "w", encoding="utf-8") as f:
        json.dump(promokodlar, f, ensure_ascii=False, indent=4)

# ===================== HOLAT =====================
yangi_kitob = {}
buyurtma_data = {}
chek_kutish = {}
yangi_promo = {}

# ===================== TOP KITOBLAR =====================
def haftalik_top_kitoblar():
    bir_hafta_oldin = datetime.now() - timedelta(days=7)
    kitob_soni = {}
    for b in buyurtmalar:
        if b.get("holat") == "✅ Tasdiqlandi":
            sana = b.get("sana")
            if sana:
                try:
                    buyurtma_sanasi = datetime.fromisoformat(sana)
                    if buyurtma_sanasi >= bir_hafta_oldin:
                        kitob_nomi = b["kitob"]
                        kitob_soni[kitob_nomi] = kitob_soni.get(kitob_nomi, 0) + 1
                except:
                    pass
            else:
                kitob_nomi = b["kitob"]
                kitob_soni[kitob_nomi] = kitob_soni.get(kitob_nomi, 0) + 1
    return sorted(kitob_soni.items(), key=lambda x: x[1], reverse=True)[:5]

# ===================== PROMO KOD TEKSHIRISH =====================
def promo_tekshir(kod, user_id):
    kod = kod.upper().strip()
    if kod not in promokodlar:
        return None, "❌ Promo kod topilmadi!"
    promo = promokodlar[kod]
    foydalanish = promo.get("foydalanganlar", {})
    user_key = str(user_id)
    if foydalanish.get(user_key, 0) >= 3:
        return None, "❌ Siz bu promo kodni 3 marta ishlatgansiz!"
    return promo["chegirma"], f"✅ Promo kod qabul qilindi! {promo['chegirma']}% chegirma!"

def narx_hisob(narx_str, chegirma):
    try:
        narx = float(''.join(filter(lambda x: x.isdigit() or x == '.', narx_str)))
        yangi_narx = narx * (1 - chegirma / 100)
        return f"{int(yangi_narx):,} so'm"
    except:
        return narx_str

# ===================== YORDAMCHI =====================
def azomi(user_id):
    try:
        member = bot.get_chat_member(KANAL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(e)
        return False

def asosiy_menyu(user_id=None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔍 Kitob qidirish", "📋 Barcha kitoblar")
    markup.row("🛒 Buyurtma", "📦 Mening buyurtmalarim")
    markup.row("🏆 Top kitoblar", "📞 Bog'lanish")
    if user_id == ADMIN_ID:
        markup.row("👨‍💼 Admin panel")
    return markup

def admin_menyu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ Kitob qo'shish", "🗑 Kitob o'chirish")
    markup.row("📊 Statistika", "🛒 Buyurtmalar")
    markup.row("🎁 Promo kodlar", "📢 Xabar yuborish")
    markup.row("🔙 Orqaga")
    return markup

def promo_menyu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ Promo kod qo'shish", "🗑 Promo kod o'chirish")
    markup.row("📋 Promo kodlar ro'yxati", "🔙 Orqaga")
    return markup

def kanal_tugma():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Kanalga a'zo bo'lish", url="https://t.me/kitobsevarllar"))
    markup.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="tekshir"))
    return markup

def kitoblar_inline(maqsad="buyurtma", sahifa=0):
    markup = types.InlineKeyboardMarkup(row_width=1)
    boshlanish = sahifa * 5
    oxiri = boshlanish + 5
    joriy_kitoblar = kitoblar[boshlanish:oxiri]
    for i, k in enumerate(joriy_kitoblar, boshlanish + 1):
        holat = "✅" if k["mavjud"] else "❌"
        if maqsad == "buyurtma":
            if k["mavjud"]:
                tugma_text = f"{i}. {k['nomi']} — {k['narx']} {holat}"
                callback = f"buyurtma_kitob_{i-1}"
            else:
                tugma_text = f"{i}. {k['nomi']} — {k['narx']} {holat}"
                callback = "mavjud_emas"
        else:
            tugma_text = f"{i}. {k['nomi']}"
            callback = f"ochir_kitob_{i-1}"
        markup.add(types.InlineKeyboardButton(tugma_text, callback_data=callback))
    nav_tugmalar = []
    if sahifa > 0:
        nav_tugmalar.append(types.InlineKeyboardButton("⬅️ Oldingi", callback_data=f"sahifa_{maqsad}_{sahifa-1}"))
    if oxiri < len(kitoblar):
        nav_tugmalar.append(types.InlineKeyboardButton("Keyingi ➡️", callback_data=f"sahifa_{maqsad}_{sahifa+1}"))
    if nav_tugmalar:
        markup.row(*nav_tugmalar)
    markup.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data="bekor_qilish"))
    return markup

def kitob_detail_markup(kitob_index):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛒 Buyurtma qilish", callback_data=f"buyurtma_kitob_{kitob_index}"))
    return markup

def buyurtma_holat_markup(buyurtma_index):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🚚 Yo'lda", callback_data=f"holat_yolda_{buyurtma_index}"),
        types.InlineKeyboardButton("📦 Yetkazildi", callback_data=f"holat_yetkazildi_{buyurtma_index}")
    )
    return markup

# ===================== START =====================
@bot.message_handler(commands=['start'])
def start(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    foydalanuvchilar[str(message.chat.id)] = message.from_user.first_name
    saqlash_foydalanuvchilar()
    if azomi(message.chat.id):
        try:
            with open("rasm.jpg", "rb") as rasm:
                bot.send_photo(message.chat.id, rasm,
                    caption="📚 Kitobxona botiga xush kelibsiz!",
                    reply_markup=asosiy_menyu(message.chat.id))
        except:
            bot.send_message(message.chat.id,
                "📚 Kitobxona botiga xush kelibsiz!",
                reply_markup=asosiy_menyu(message.chat.id))
    else:
        bot.send_message(message.chat.id,
            "❌ Avval kanalga a'zo bo'ling!",
            reply_markup=kanal_tugma())

# ===================== KANAL =====================
@bot.callback_query_handler(func=lambda c: c.data == "tekshir")
def tekshir(call):
    if azomi(call.message.chat.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ Xush kelibsiz!", reply_markup=asosiy_menyu(call.message.chat.id))
    else:
        bot.answer_callback_query(call.id, "❌ Hali a'zo bo'lmadingiz!")

# ===================== BARCHA KITOBLAR =====================
@bot.message_handler(func=lambda m: m.text == "📋 Barcha kitoblar")
def barcha_kitoblar(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    if not kitoblar:
        bot.send_message(message.chat.id, "❌ Hozircha kitob mavjud emas!")
        return
    text = "📚 <b>Barcha kitoblar:</b>\n\n"
    for i, k in enumerate(kitoblar, 1):
        holat = "✅ Mavjud" if k["mavjud"] else "❌ Mavjud emas"
        text += f"{i}. <b>{k['nomi']}</b>\n   ✍️ {k['muallif']} | 💰 {k['narx']} | {holat}\n\n"
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# ===================== TOP KITOBLAR =====================
@bot.message_handler(func=lambda m: m.text == "🏆 Top kitoblar")
def top_kitoblar(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    top = haftalik_top_kitoblar()
    if not top:
        bot.send_message(message.chat.id, "📊 Hozircha haftalik top kitoblar yo'q!\n\nBirinchi bo'lib buyurtma bering! 😊")
        return
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    text = "🏆 <b>Haftalik top kitoblar:</b>\n\n"
    for i, (kitob_nomi, soni) in enumerate(top):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        text += f"{medal} <b>{kitob_nomi}</b>\n   📦 {soni} ta buyurtma\n\n"
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# ===================== MENING BUYURTMALARIM =====================
@bot.message_handler(func=lambda m: m.text == "📦 Mening buyurtmalarim")
def mening_buyurtmalarim(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    user_id = message.chat.id
    mening = [b for b in buyurtmalar if b.get("user_id") == user_id]
    if not mening:
        bot.send_message(message.chat.id,
            "📦 Sizda hozircha buyurtma yo'q!\n\n🛒 Buyurtma berish uchun — <b>Buyurtma</b> tugmasini bosing!",
            parse_mode="HTML")
        return
    text = "📦 <b>Mening buyurtmalarim:</b>\n\n"
    for i, b in enumerate(mening, 1):
        text += (
            f"<b>#{i}</b>\n"
            f"📚 {b['kitob']}\n"
            f"💰 {b.get('narx', 'Noma\'lum')}\n"
            f"📌 {b.get('holat', '⏳ Kutilmoqda')}\n"
            f"━━━━━━━━━━━━\n"
        )
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# ===================== KITOB QIDIRISH =====================
@bot.message_handler(func=lambda m: m.text == "🔍 Kitob qidirish")
def qidirish(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    msg = bot.send_message(message.chat.id, "🔍 Kitob nomini yozing:")
    bot.register_next_step_handler(msg, qidir)

def qidir(message):
    if message.text in ["🔍 Kitob qidirish", "📋 Barcha kitoblar", "🛒 Buyurtma",
                        "📞 Bog'lanish", "👨‍💼 Admin panel", "🔙 Orqaga",
                        "🏆 Top kitoblar", "📦 Mening buyurtmalarim"]:
        bot.process_new_messages([message])
        return
    sorov = message.text.lower()
    topildi = False
    for i, kitob in enumerate(kitoblar):
        if sorov in kitob["nomi"].lower() or sorov in kitob["muallif"].lower():
            topildi = True
            holat = "✅ Mavjud" if kitob["mavjud"] else "❌ Mavjud emas"
            text = (
                f"📚 <b>{kitob['nomi']}</b>\n\n"
                f"✍️ Muallif: {kitob['muallif']}\n"
                f"💰 Narx: {kitob['narx']}\n"
                f"📄 Sahifa: {kitob['sahifa']}\n"
                f"🎭 Janr: {kitob['janr']}\n"
                f"📦 Holat: {holat}"
            )
            if kitob["mavjud"]:
                bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=kitob_detail_markup(i))
            else:
                bot.send_message(message.chat.id, text, parse_mode="HTML")
    if not topildi:
        bot.send_message(message.chat.id, "❌ Kitob topilmadi! Boshqa so'z bilan qidiring.")

# ===================== BUYURTMA =====================
@bot.message_handler(func=lambda m: m.text == "🛒 Buyurtma")
def buyurtma(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    if not azomi(message.chat.id):
        bot.send_message(message.chat.id, "❌ Avval kanalga a'zo bo'ling!", reply_markup=kanal_tugma())
        return
    if not kitoblar:
        bot.send_message(message.chat.id, "❌ Hozircha kitob mavjud emas!")
        return
    bot.send_message(message.chat.id,
        "📚 <b>Kitob tanlang:</b>\n\n✅ — mavjud | ❌ — mavjud emas",
        parse_mode="HTML",
        reply_markup=kitoblar_inline(maqsad="buyurtma", sahifa=0))

@bot.callback_query_handler(func=lambda c: c.data.startswith("sahifa_"))
def sahifa_almashtir(call):
    parts = call.data.split("_")
    maqsad = parts[1]
    sahifa = int(parts[2])
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
        reply_markup=kitoblar_inline(maqsad=maqsad, sahifa=sahifa))
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "mavjud_emas")
def mavjud_emas(call):
    bot.answer_callback_query(call.id, "❌ Bu kitob hozircha mavjud emas!", show_alert=True)

@bot.callback_query_handler(func=lambda c: c.data == "bekor_qilish")
def bekor_qilish(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "❌ Bekor qilindi!")

@bot.callback_query_handler(func=lambda c: c.data.startswith("buyurtma_kitob_"))
def buyurtma_kitob_tanlandi(call):
    index = int(call.data.split("_")[-1])
    if index < 0 or index >= len(kitoblar):
        bot.answer_callback_query(call.id, "❌ Kitob topilmadi!")
        return
    kitob = kitoblar[index]
    if not kitob["mavjud"]:
        bot.answer_callback_query(call.id, "❌ Bu kitob mavjud emas!", show_alert=True)
        return
    buyurtma_data[call.message.chat.id] = {"kitob": kitob["nomi"], "narx": kitob["narx"], "asl_narx": kitob["narx"]}
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, f"✅ '{kitob['nomi']}' tanlandi!")
    text = (
        f"✅ Tanlangan kitob: <b>{kitob['nomi']}</b>\n"
        f"💰 Narx: <b>{kitob['narx']}</b>\n\n"
        f"👤 Ism familiyangizni yozing:"
    )
    msg = bot.send_message(call.message.chat.id, text, parse_mode="HTML")
    bot.register_next_step_handler(msg, buyurtma_ism)

def buyurtma_ism(message):
    if message.text in ["🔍 Kitob qidirish", "📋 Barcha kitoblar", "🛒 Buyurtma",
                        "📞 Bog'lanish", "👨‍💼 Admin panel", "🔙 Orqaga",
                        "🏆 Top kitoblar", "📦 Mening buyurtmalarim"]:
        bot.process_new_messages([message])
        return
    if message.chat.id not in buyurtma_data:
        bot.send_message(message.chat.id, "❌ Xatolik! Qaytadan boshlang.", reply_markup=asosiy_menyu(message.chat.id))
        return
    buyurtma_data[message.chat.id]["ism"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📞 Telefon yuborish", request_contact=True))
    msg = bot.send_message(message.chat.id, "📞 Telefon raqamingizni yuboring:", reply_markup=markup)
    bot.register_next_step_handler(msg, buyurtma_tel)

def buyurtma_tel(message):
    if message.chat.id not in buyurtma_data:
        bot.send_message(message.chat.id, "❌ Xatolik! Qaytadan boshlang.", reply_markup=asosiy_menyu(message.chat.id))
        return
    if message.contact:
        telefon = message.contact.phone_number
    else:
        if message.text in ["🔍 Kitob qidirish", "📋 Barcha kitoblar", "🛒 Buyurtma",
                            "📞 Bog'lanish", "👨‍💼 Admin panel", "🔙 Orqaga",
                            "🏆 Top kitoblar", "📦 Mening buyurtmalarim"]:
            bot.process_new_messages([message])
            return
        telefon = message.text
    buyurtma_data[message.chat.id]["telefon"] = telefon
    msg = bot.send_message(message.chat.id, "📍 Manzilingizni yozing:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, buyurtma_manzil)

def buyurtma_manzil(message):
    if message.text in ["🔍 Kitob qidirish", "📋 Barcha kitoblar", "🛒 Buyurtma",
                        "📞 Bog'lanish", "👨‍💼 Admin panel", "🔙 Orqaga",
                        "🏆 Top kitoblar", "📦 Mening buyurtmalarim"]:
        bot.process_new_messages([message])
        return
    if message.chat.id not in buyurtma_data:
        bot.send_message(message.chat.id, "❌ Xatolik! Qaytadan boshlang.", reply_markup=asosiy_menyu(message.chat.id))
        return
    buyurtma_data[message.chat.id]["manzil"] = message.text

    # Promo kod so'rash
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("⏭ Promo kodsiz davom etish")
    msg = bot.send_message(message.chat.id,
        "🎁 Promo kodingiz bormi? Yozing yoki o'tkazib yuboring:",
        reply_markup=markup)
    bot.register_next_step_handler(msg, buyurtma_promo)

def buyurtma_promo(message):
    if message.text in ["🔍 Kitob qidirish", "📋 Barcha kitoblar", "🛒 Buyurtma",
                        "📞 Bog'lanish", "👨‍💼 Admin panel", "🔙 Orqaga",
                        "🏆 Top kitoblar", "📦 Mening buyurtmalarim"]:
        bot.process_new_messages([message])
        return
    if message.chat.id not in buyurtma_data:
        bot.send_message(message.chat.id, "❌ Xatolik! Qaytadan boshlang.", reply_markup=asosiy_menyu(message.chat.id))
        return

    data = buyurtma_data[message.chat.id]
    chegirma_text = ""

    if message.text != "⏭ Promo kodsiz davom etish":
        chegirma, xabar = promo_tekshir(message.text, message.chat.id)
        if chegirma:
            asl_narx = data["asl_narx"]
            yangi_narx = narx_hisob(asl_narx, chegirma)
            data["narx"] = yangi_narx
            data["promo_kod"] = message.text.upper().strip()
            data["chegirma"] = chegirma

            # Foydalanish sonini yangilash
            kod = message.text.upper().strip()
            if "foydalanganlar" not in promokodlar[kod]:
                promokodlar[kod]["foydalanganlar"] = {}
            user_key = str(message.chat.id)
            promokodlar[kod]["foydalanganlar"][user_key] = promokodlar[kod]["foydalanganlar"].get(user_key, 0) + 1
            saqlash_promokodlar()

            chegirma_text = f"🎁 Promo kod: {kod} (-{chegirma}%)\n💰 Chegirmali narx: <b>{yangi_narx}</b>\n"
            bot.send_message(message.chat.id, xabar, reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.send_message(message.chat.id, xabar, reply_markup=types.ReplyKeyboardRemove())

    # Buyurtmani yakunlash
    buyurtmalar.append({
        "ism": data["ism"],
        "telefon": data["telefon"],
        "manzil": data["manzil"],
        "kitob": data["kitob"],
        "narx": data.get("narx", data["asl_narx"]),
        "asl_narx": data["asl_narx"],
        "promo_kod": data.get("promo_kod", ""),
        "user_id": message.chat.id,
        "holat": "⏳ To'lov kutilmoqda",
        "sana": datetime.now().isoformat()
    })
    saqlash_buyurtmalar()
    buyurtma_index = len(buyurtmalar) - 1

    text = (
        f"✅ <b>Buyurtma qabul qilindi!</b>\n\n"
        f"📚 Kitob: <b>{data['kitob']}</b>\n"
        f"💰 Narx: <b>{data.get('narx', data['asl_narx'])}</b>\n"
        f"{chegirma_text}"
        f"👤 Ism: {data['ism']}\n"
        f"📞 Telefon: {data['telefon']}\n"
        f"📍 Manzil: {data['manzil']}\n"
        f"📌 Holat: ⏳ To'lov kutilmoqda\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💳 <b>To'lov uchun:</b>\n"
        f"Karta: <code>{KARTA}</code>\n"
        f"Egasi: {KARTA_EGASI}\n\n"
        f"💡 To'lovdan so'ng chek rasmini yuboring!"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📸 Chek yuborish", callback_data=f"chek_{buyurtma_index}"))
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")

    promo_info = f"\n🎁 Promo kod: {data.get('promo_kod', 'Yo\'q')}" if data.get("promo_kod") else ""
    bot.send_message(ADMIN_ID,
        f"🛒 <b>YANGI BUYURTMA #{buyurtma_index + 1}</b>\n\n"
        f"📚 Kitob: {data['kitob']}\n"
        f"💰 Narx: {data.get('narx', data['asl_narx'])}{promo_info}\n"
        f"👤 Ism: {data['ism']}\n"
        f"📞 Telefon: {data['telefon']}\n"
        f"📍 Manzil: {data['manzil']}\n"
        f"📌 Holat: ⏳ To'lov kutilmoqda",
        parse_mode="HTML")

    if message.chat.id in buyurtma_data:
        del buyurtma_data[message.chat.id]

# ===================== CHEK =====================
@bot.callback_query_handler(func=lambda c: c.data.startswith("chek_"))
def chek_yuborish(call):
    buyurtma_index = int(call.data.split("_")[1])
    chek_kutish[call.message.chat.id] = buyurtma_index
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "📸 To'lov chekini (rasmini) yuboring:")
    bot.register_next_step_handler(msg, chek_qabul)

def chek_qabul(message):
    if message.photo:
        buyurtma_index = chek_kutish.get(message.chat.id)
        if buyurtma_index is not None:
            b = buyurtmalar[buyurtma_index]
            caption = (
                f"📸 <b>YANGI CHEK #{buyurtma_index + 1}</b>\n\n"
                f"📚 Kitob: {b['kitob']}\n"
                f"💰 Narx: {b.get('narx', 'Noma\'lum')}\n"
                f"👤 Ism: {b['ism']}\n"
                f"📞 Telefon: {b['telefon']}"
            )
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"tasdiq_{buyurtma_index}_{message.chat.id}"),
                types.InlineKeyboardButton("❌ Bekor qilish", callback_data=f"bekor_{buyurtma_index}_{message.chat.id}")
            )
            bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=markup, parse_mode="HTML")
            bot.send_message(message.chat.id, "✅ Chek yuborildi! Admin tekshirmoqda...", reply_markup=asosiy_menyu(message.chat.id))
            if message.chat.id in chek_kutish:
                del chek_kutish[message.chat.id]
    else:
        bot.send_message(message.chat.id, "❌ Iltimos, rasm yuboring!")
        msg = bot.send_message(message.chat.id, "📸 To'lov chekini qaytadan yuboring:")
        buyurtma_index = chek_kutish.get(message.chat.id)
        if buyurtma_index is not None:
            bot.register_next_step_handler(msg, chek_qabul)

# ===================== ADMIN: TASDIQLASH =====================
@bot.callback_query_handler(func=lambda c: c.data.startswith("tasdiq_"))
def buyurtma_tasdiq(call):
    if call.message.chat.id != ADMIN_ID:
        return
    parts = call.data.split("_")
    buyurtma_index = int(parts[1])
    user_id = int(parts[2])
    buyurtmalar[buyurtma_index]["holat"] = "✅ Tasdiqlandi"
    saqlash_buyurtmalar()
    bot.answer_callback_query(call.id, "✅ Tasdiqlandi!")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(user_id,
        f"✅ <b>Buyurtmangiz tasdiqlandi!</b>\n\n"
        f"📚 Kitob: {buyurtmalar[buyurtma_index]['kitob']}\n"
        f"📌 Holat: ✅ Tasdiqlandi\n\n"
        f"Tez orada yo'lga chiqariladi! 🚀",
        parse_mode="HTML")
    bot.send_message(ADMIN_ID,
        f"📦 <b>#{buyurtma_index + 1} buyurtma holati:</b>\n\n"
        f"📚 {buyurtmalar[buyurtma_index]['kitob']}\n"
        f"👤 {buyurtmalar[buyurtma_index]['ism']}\n"
        f"📌 Holat: ✅ Tasdiqlandi",
        parse_mode="HTML",
        reply_markup=buyurtma_holat_markup(buyurtma_index))

# ===================== ADMIN: BEKOR =====================
@bot.callback_query_handler(func=lambda c: c.data.startswith("bekor_"))
def buyurtma_bekor(call):
    if call.message.chat.id != ADMIN_ID:
        return
    parts = call.data.split("_")
    buyurtma_index = int(parts[1])
    user_id = int(parts[2])
    buyurtmalar[buyurtma_index]["holat"] = "❌ Bekor qilindi"
    saqlash_buyurtmalar()
    bot.answer_callback_query(call.id, "❌ Bekor qilindi!")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(user_id,
        f"❌ <b>Buyurtmangiz bekor qilindi!</b>\n\n"
        f"📚 Kitob: {buyurtmalar[buyurtma_index]['kitob']}\n"
        f"Sabab: To'lov tasdiqlanmadi!\n\n"
        f"Muammo bo'lsa admin bilan bog'laning: @ota_176",
        parse_mode="HTML")

# ===================== HOLAT: YO'LDA =====================
@bot.callback_query_handler(func=lambda c: c.data.startswith("holat_yolda_"))
def holat_yolda(call):
    if call.message.chat.id != ADMIN_ID:
        return
    buyurtma_index = int(call.data.split("_")[-1])
    buyurtmalar[buyurtma_index]["holat"] = "🚚 Yo'lda"
    saqlash_buyurtmalar()
    bot.answer_callback_query(call.id, "🚚 Yo'lda!")
    user_id = buyurtmalar[buyurtma_index]["user_id"]
    bot.send_message(user_id,
        f"🚚 <b>Buyurtmangiz yo'lda!</b>\n\n"
        f"📚 Kitob: {buyurtmalar[buyurtma_index]['kitob']}\n"
        f"📌 Holat: 🚚 Yo'lda\n\n"
        f"Tez orada yetib boradi! 😊",
        parse_mode="HTML")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📦 Yetkazildi", callback_data=f"holat_yetkazildi_{buyurtma_index}"))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)

# ===================== HOLAT: YETKAZILDI =====================
@bot.callback_query_handler(func=lambda c: c.data.startswith("holat_yetkazildi_"))
def holat_yetkazildi(call):
    if call.message.chat.id != ADMIN_ID:
        return
    buyurtma_index = int(call.data.split("_")[-1])
    buyurtmalar[buyurtma_index]["holat"] = "📦 Yetkazildi"
    saqlash_buyurtmalar()
    bot.answer_callback_query(call.id, "📦 Yetkazildi!")
    user_id = buyurtmalar[buyurtma_index]["user_id"]
    bot.send_message(user_id,
        f"📦 <b>Buyurtmangiz yetkazildi!</b>\n\n"
        f"📚 Kitob: {buyurtmalar[buyurtma_index]['kitob']}\n"
        f"📌 Holat: 📦 Yetkazildi\n\n"
        f"Xarid uchun rahmat! 😊❤️",
        parse_mode="HTML")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(ADMIN_ID,
        f"✅ <b>#{buyurtma_index + 1} buyurtma yetkazildi!</b>\n\n"
        f"📚 {buyurtmalar[buyurtma_index]['kitob']}\n"
        f"👤 {buyurtmalar[buyurtma_index]['ism']}",
        parse_mode="HTML")

# ===================== BOG'LANISH =====================
@bot.message_handler(func=lambda m: m.text == "📞 Bog'lanish")
def boglanish(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.send_message(message.chat.id, "📞 <b>Bog'lanish:</b>\n\nAdmin: @ota_176", parse_mode="HTML")

# ===================== ADMIN PANEL =====================
@bot.message_handler(func=lambda m: m.text == "👨‍💼 Admin panel")
def admin_panel(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    if message.chat.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "👨‍💼 Admin panel", reply_markup=admin_menyu())

# ===================== PROMO KODLAR =====================
@bot.message_handler(func=lambda m: m.text == "🎁 Promo kodlar")
def promo_kodlar(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    if message.chat.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "🎁 Promo kodlar", reply_markup=promo_menyu())

@bot.message_handler(func=lambda m: m.text == "📋 Promo kodlar ro'yxati")
def promo_royxat(message):
    if message.chat.id != ADMIN_ID:
        return
    if not promokodlar:
        bot.send_message(message.chat.id, "❌ Hozircha promo kod yo'q!")
        return
    text = "🎁 <b>Promo kodlar:</b>\n\n"
    for kod, info in promokodlar.items():
        jami = sum(info.get("foydalanganlar", {}).values())
        text += f"🔑 <b>{kod}</b> — {info['chegirma']}% chegirma\n   👥 {jami} marta ishlatilgan\n\n"
    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "➕ Promo kod qo'shish")
def promo_qoshish(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    if message.chat.id != ADMIN_ID:
        return
    msg = bot.send_message(message.chat.id, "🔑 Promo kod nomini yozing (masalan: KITOB10):")
    bot.register_next_step_handler(msg, promo_nomi)

def promo_nomi(message):
    if message.text in ["➕ Promo kod qo'shish", "🗑 Promo kod o'chirish",
                        "📋 Promo kodlar ro'yxati", "🔙 Orqaga"]:
        bot.process_new_messages([message])
        return
    yangi_promo[message.chat.id] = {"kod": message.text.upper().strip()}
    msg = bot.send_message(message.chat.id, "💰 Chegirma foizini yozing (masalan: 10):")
    bot.register_next_step_handler(msg, promo_chegirma)

def promo_chegirma(message):
    if message.text in ["➕ Promo kod qo'shish", "🗑 Promo kod o'chirish",
                        "📋 Promo kodlar ro'yxati", "🔙 Orqaga"]:
        bot.process_new_messages([message])
        return
    try:
        chegirma = int(message.text)
        if chegirma < 1 or chegirma > 100:
            bot.send_message(message.chat.id, "❌ 1 dan 100 gacha son yozing!")
            return
        kod = yangi_promo[message.chat.id]["kod"]
        promokodlar[kod] = {
            "chegirma": chegirma,
            "foydalanganlar": {}
        }
        saqlash_promokodlar()
        bot.send_message(message.chat.id,
            f"✅ <b>Promo kod qo'shildi!</b>\n\n"
            f"🔑 Kod: <b>{kod}</b>\n"
            f"💰 Chegirma: <b>{chegirma}%</b>",
            parse_mode="HTML",
            reply_markup=promo_menyu())
        if message.chat.id in yangi_promo:
            del yangi_promo[message.chat.id]
    except:
        bot.send_message(message.chat.id, "❌ Raqam yozing!")

@bot.message_handler(func=lambda m: m.text == "🗑 Promo kod o'chirish")
def promo_ochirish(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    if message.chat.id != ADMIN_ID:
        return
    if not promokodlar:
        bot.send_message(message.chat.id, "❌ Promo kod yo'q!")
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for kod in promokodlar:
        markup.add(types.InlineKeyboardButton(f"🗑 {kod}", callback_data=f"promo_ochir_{kod}"))
    markup.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data="bekor_qilish"))
    bot.send_message(message.chat.id, "🗑 O'chirmoqchi bo'lgan promo kodni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("promo_ochir_"))
def promo_ochir_callback(call):
    if call.message.chat.id != ADMIN_ID:
        return
    kod = call.data.replace("promo_ochir_", "")
    if kod in promokodlar:
        del promokodlar[kod]
        saqlash_promokodlar()
        bot.edit_message_text(f"✅ <b>'{kod}'</b> promo kod o'chirildi!",
            call.message.chat.id, call.message.message_id, parse_mode="HTML")
        bot.answer_callback_query(call.id, "✅ O'chirildi!")
    else:
        bot.answer_callback_query(call.id, "❌ Topilmadi!")

# ===================== KITOB QO'SHISH =====================
@bot.message_handler(func=lambda m: m.text == "➕ Kitob qo'shish")
def kitob_qoshish(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    if message.chat.id != ADMIN_ID:
        return
    yangi_kitob[message.chat.id] = {}
    msg = bot.send_message(message.chat.id, "📚 Kitob nomini yozing:")
    bot.register_next_step_handler(msg, kitob_nomi)

def kitob_nomi(message):
    if message.text in ["➕ Kitob qo'shish", "🗑 Kitob o'chirish", "📊 Statistika",
                        "🛒 Buyurtmalar", "📢 Xabar yuborish", "🔙 Orqaga", "🎁 Promo kodlar"]:
        bot.process_new_messages([message])
        return
    yangi_kitob[message.chat.id]["nomi"] = message.text
    msg = bot.send_message(message.chat.id, "✍️ Muallif:")
    bot.register_next_step_handler(msg, kitob_muallif)

def kitob_muallif(message):
    if message.text in ["➕ Kitob qo'shish", "🗑 Kitob o'chirish", "📊 Statistika",
                        "🛒 Buyurtmalar", "📢 Xabar yuborish", "🔙 Orqaga", "🎁 Promo kodlar"]:
        bot.process_new_messages([message])
        return
    yangi_kitob[message.chat.id]["muallif"] = message.text
    msg = bot.send_message(message.chat.id, "💰 Narx:")
    bot.register_next_step_handler(msg, kitob_narx)

def kitob_narx(message):
    if message.text in ["➕ Kitob qo'shish", "🗑 Kitob o'chirish", "📊 Statistika",
                        "🛒 Buyurtmalar", "📢 Xabar yuborish", "🔙 Orqaga", "🎁 Promo kodlar"]:
        bot.process_new_messages([message])
        return
    yangi_kitob[message.chat.id]["narx"] = message.text
    msg = bot.send_message(message.chat.id, "📄 Sahifa soni:")
    bot.register_next_step_handler(msg, kitob_sahifa)

def kitob_sahifa(message):
    if message.text in ["➕ Kitob qo'shish", "🗑 Kitob o'chirish", "📊 Statistika",
                        "🛒 Buyurtmalar", "📢 Xabar yuborish", "🔙 Orqaga", "🎁 Promo kodlar"]:
        bot.process_new_messages([message])
        return
    yangi_kitob[message.chat.id]["sahifa"] = message.text
    msg = bot.send_message(message.chat.id, "🎭 Janr:")
    bot.register_next_step_handler(msg, kitob_janr)

def kitob_janr(message):
    if message.text in ["➕ Kitob qo'shish", "🗑 Kitob o'chirish", "📊 Statistika",
                        "🛒 Buyurtmalar", "📢 Xabar yuborish", "🔙 Orqaga", "🎁 Promo kodlar"]:
        bot.process_new_messages([message])
        return
    yangi_kitob[message.chat.id]["janr"] = message.text
    yangi_kitob[message.chat.id]["mavjud"] = True
    kitoblar.append(yangi_kitob[message.chat.id].copy())
    saqlash_kitoblar()
    k = yangi_kitob[message.chat.id]
    bot.send_message(message.chat.id,
        f"✅ <b>Kitob qo'shildi!</b>\n\n"
        f"📚 {k['nomi']}\n"
        f"✍️ {k['muallif']}\n"
        f"💰 {k['narx']}\n"
        f"📄 {k['sahifa']} sahifa\n"
        f"🎭 {k['janr']}",
        parse_mode="HTML",
        reply_markup=admin_menyu())
    if message.chat.id in yangi_kitob:
        del yangi_kitob[message.chat.id]

# ===================== KITOB O'CHIRISH =====================
@bot.message_handler(func=lambda m: m.text == "🗑 Kitob o'chirish")
def kitob_ochirish(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    if message.chat.id != ADMIN_ID:
        return
    if not kitoblar:
        bot.send_message(message.chat.id, "❌ Kitob yo'q!")
        return
    bot.send_message(message.chat.id,
        "🗑 <b>O'chirmoqchi bo'lgan kitobni tanlang:</b>",
        parse_mode="HTML",
        reply_markup=kitoblar_inline(maqsad="ochirish", sahifa=0))

@bot.callback_query_handler(func=lambda c: c.data.startswith("ochir_kitob_"))
def ochirish_callback(call):
    if call.message.chat.id != ADMIN_ID:
        return
    index = int(call.data.split("_")[-1])
    if index < 0 or index >= len(kitoblar):
        bot.answer_callback_query(call.id, "❌ Kitob topilmadi!")
        return
    nom = kitoblar[index]["nomi"]
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Ha, o'chir", callback_data=f"ochir_tasdiqlandi_{index}"),
        types.InlineKeyboardButton("❌ Bekor", callback_data="bekor_qilish")
    )
    bot.edit_message_text(
        f"⚠️ <b>'{nom}'</b> kitobini o'chirishni tasdiqlaysizmi?",
        call.message.chat.id, call.message.message_id,
        parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("ochir_tasdiqlandi_"))
def ochirish_tasdiqlandi(call):
    if call.message.chat.id != ADMIN_ID:
        return
    index = int(call.data.split("_")[-1])
    if index < 0 or index >= len(kitoblar):
        bot.answer_callback_query(call.id, "❌ Kitob topilmadi!")
        return
    nom = kitoblar[index]["nomi"]
    kitoblar.pop(index)
    saqlash_kitoblar()
    bot.edit_message_text(f"✅ <b>'{nom}'</b> o'chirildi!",
        call.message.chat.id, call.message.message_id, parse_mode="HTML")
    bot.answer_callback_query(call.id, "✅ O'chirildi!")

# ===================== ADMIN: BUYURTMALAR =====================
@bot.message_handler(func=lambda m: m.text == "🛒 Buyurtmalar")
def admin_buyurtmalar(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    if message.chat.id != ADMIN_ID:
        return
    if not buyurtmalar:
        bot.send_message(message.chat.id, "❌ Hozircha buyurtma yo'q!")
        return
    text = "🛒 <b>Buyurtmalar:</b>\n\n"
    for i, b in enumerate(buyurtmalar, 1):
        text += (
            f"<b>#{i}</b> — {b['ism']}\n"
            f"📚 {b['kitob']} | 💰 {b.get('narx', '-')}\n"
            f"📞 {b['telefon']}\n"
            f"📍 {b.get('manzil', '-')}\n"
            f"📌 {b.get('holat', 'Kutilmoqda')}\n"
            f"━━━━━━━━━━━━\n"
        )
    if len(text) > 4000:
        for i in range(0, len(text), 4000):
            bot.send_message(message.chat.id, text[i:i+4000], parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, text, parse_mode="HTML")

# ===================== STATISTIKA =====================
@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def statistika(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    if message.chat.id != ADMIN_ID:
        return
    tasdiqlangan = sum(1 for b in buyurtmalar if b.get("holat") == "✅ Tasdiqlandi")
    yolda = sum(1 for b in buyurtmalar if b.get("holat") == "🚚 Yo'lda")
    yetkazildi = sum(1 for b in buyurtmalar if b.get("holat") == "📦 Yetkazildi")
    kutilmoqda = sum(1 for b in buyurtmalar if "kutilmoqda" in b.get("holat", "").lower())
    bekor = sum(1 for b in buyurtmalar if b.get("holat") == "❌ Bekor qilindi")
    top = haftalik_top_kitoblar()
    top_text = ""
    if top:
        for i, (nom, soni) in enumerate(top[:3], 1):
            top_text += f"{i}. {nom} — {soni} ta\n"
    else:
        top_text = "Hozircha yo'q"

    text = (
        f"📊 <b>Statistika:</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{len(foydalanuvchilar)}</b>\n"
        f"📚 Kitoblar: <b>{len(kitoblar)}</b>\n"
        f"🛒 Jami buyurtmalar: <b>{len(buyurtmalar)}</b>\n"
        f"🎁 Promo kodlar: <b>{len(promokodlar)}</b>\n\n"
        f"⏳ Kutilmoqda: <b>{kutilmoqda}</b>\n"
        f"✅ Tasdiqlangan: <b>{tasdiqlangan}</b>\n"
        f"🚚 Yo'lda: <b>{yolda}</b>\n"
        f"📦 Yetkazildi: <b>{yetkazildi}</b>\n"
        f"❌ Bekor qilingan: <b>{bekor}</b>\n\n"
        f"🏆 <b>Haftalik top:</b>\n{top_text}"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# ===================== XABAR YUBORISH =====================
@bot.message_handler(func=lambda m: m.text == "📢 Xabar yuborish")
def xabar(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    if message.chat.id != ADMIN_ID:
        return
    msg = bot.send_message(message.chat.id, "📢 Xabar yozing:")
    bot.register_next_step_handler(msg, xabar_yubor)

def xabar_yubor(message):
    count = 0
    xato = 0
    for user_id in foydalanuvchilar:
        try:
            bot.send_message(int(user_id), f"📢 <b>Yangilik:</b>\n\n{message.text}", parse_mode="HTML")
            count += 1
        except:
            xato += 1
    bot.send_message(message.chat.id,
        f"✅ Yuborildi: <b>{count}</b> ta\n❌ Xato: <b>{xato}</b> ta",
        parse_mode="HTML")

# ===================== ORQAGA =====================
@bot.message_handler(func=lambda m: m.text == "🔙 Orqaga")
def orqaga(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.send_message(message.chat.id, "🏠 Asosiy menyu", reply_markup=asosiy_menyu(message.chat.id))

print("✅ Bot ishga tushdi...")
bot.infinity_polling(skip_pending=True)