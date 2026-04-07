import telebot
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8444593771:AAHa-fhc-vT_MXEvNyb91cPem8VEn_dg-4U"
CHANNEL = "@forexAK99"

bot = telebot.TeleBot(TOKEN)

# Database setup
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, refs INTEGER DEFAULT 0, ref_by INTEGER)")
conn.commit()

def add_user(user_id, ref_by=None):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (user_id, refs, ref_by) VALUES (?, 0, ?)", (user_id, ref_by))
        if ref_by:
            cursor.execute("UPDATE users SET refs = refs + 1 WHERE user_id=?", (ref_by,))
        conn.commit()

def get_refs(user_id):
    cursor.execute("SELECT refs FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0

def check_join(user_id):
    try:
        status = bot.get_chat_member(CHANNEL, user_id)
        return status.status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    args = message.text.split()

    ref_by = None
    if len(args) > 1:
        try:
            ref_by = int(args[1])
        except:
            ref_by = None

    add_user(user_id, ref_by)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 Join Channel", url="https://t.me/forexAK99"))
    markup.add(InlineKeyboardButton("✅ Check Status", callback_data="check"))

    bot.send_message(user_id, f"""
🔥 Welcome to Forex Signals Bot

👥 Your Referrals: {get_refs(user_id)}

🎁 Invite 5 friends = VIP Access

🔗 Your Invite Link:
https://t.me/YOUR_BOT_USERNAME?start={user_id}
""", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check(call):
    user_id = call.message.chat.id

    if not check_join(user_id):
        bot.send_message(user_id, "❌ पहले channel join करो")
        return

    refs = get_refs(user_id)

    if refs >= 5:
        bot.send_message(user_id, "🎉 VIP Access Granted 🔥")
    else:
        bot.send_message(user_id, f"❌ You have {refs}/5 referrals")

bot.polling()
