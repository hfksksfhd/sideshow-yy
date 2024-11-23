import telebot
import requests


token = "7359155336:AAGgGmBYhxayasITJMBVX3f1VvSKc6YjCKU"

sudo_id = "6392238598"
ch = '@MU_E6'
bot = telebot.TeleBot(token)

def us(user_id):
    try:
        url = f"https://api.telegram.org/bot{token}/getChatMember?chat_id={ch}&user_id={user_id}"
        req = requests.get(url)
        print("Response from getChatMember:", req.text)
        if 'member' in req.text or 'creator' in req.text or 'administrator' in req.text:
            return True
        else:
            return False
    except Exception as e:
        print(f"خطأ أثناء التحقق من العضوية: {e}")
        return False


def send_request(service_id, link, quantity, api_key):
    data = {
        'key': api_key,
        'action': 'add',
        'service': service_id,
        'link': link,
        'quantity': quantity,
    }
    try:
        response = requests.post('https://kd1s.com/api/v2', data=data)
        print(f"Request response: {response.text}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error in sending request: {e}")
        return None

def send_request_to_both(service_id, link, quantity, api_keys):
    results = []
    for api_key in api_keys:
        response = send_request(service_id, link, quantity, api_key)
        results.append(response)
    return results


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id == sudo_id or us(user_id):

        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            telebot.types.InlineKeyboardButton("مشاهدات تيليجرام", callback_data="views_telegram"),
            telebot.types.InlineKeyboardButton("لايكات تيكتوك", callback_data="likes_tiktok"),
            telebot.types.InlineKeyboardButton("مشاهدات فيديو تيكتوك", callback_data="views_tiktok"),
            telebot.types.InlineKeyboardButton("حفظ فيديو تيكتوك", callback_data="save_tiktok"),
            telebot.types.InlineKeyboardButton("مشاهدات ريلز انستا", callback_data="views_instagram"),
            telebot.types.InlineKeyboardButton("لايكات ريلز انستا", callback_data="likes_instagram"),
            telebot.types.InlineKeyboardButton("أعضاء تيليجرام", callback_data="members_telegram"),
            telebot.types.InlineKeyboardButton("مبرمج البوت", url="t.me/jwifeh")
        )
        bot.send_message(message.chat.id, "اهلا بك عزيزي اختر ماتريد من رشق مجاني", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"🚸| عذرا عزيزي\n🔰| عليك الاشتراك في القناة لتتمكن من استخدام البوت.\n\n- مــعرف القـناة : {ch}\n‼️| اشترك ثم أرسل /start")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "views_telegram":
        bot.send_message(call.message.chat.id, "أرسل رابط المنشور للحصول على مشاهدات (100):")
        bot.register_next_step_handler(call.message, lambda msg: process_request(msg, '8577', 100, "مشاهدات تيليجرام"))
    elif call.data == "likes_tiktok":
        bot.send_message(call.message.chat.id, "أرسل رابط الفيديو للحصول على لايكات (22):")
        bot.register_next_step_handler(call.message, lambda msg: process_request(msg, '13643', 11, "لايكات تيكتوك"))
    elif call.data == "views_tiktok":
        bot.send_message(call.message.chat.id, "أرسل رابط الفيديو للحصول على مشاهدات (200):")
        bot.register_next_step_handler(call.message, lambda msg: process_request(msg, '13577', 100, "مشاهدات فيديو تيكتوك"))
    elif call.data == "save_tiktok":
        bot.send_message(call.message.chat.id, "أرسل رابط الفيديو للحصول على حفظات (10):")
        bot.register_next_step_handler(call.message, lambda msg: process_request(msg, '13634', 10, "حفظ فيديو تيكتوك"))
    elif call.data == "views_instagram":
        bot.send_message(call.message.chat.id, "أرسل رابط الفيديو للحصول على مشاهدات (100):")
        bot.register_next_step_handler(call.message, lambda msg: process_request(msg, '13578', 100, "مشاهدات ريلز انستا"))
    elif call.data == "likes_instagram":
        bot.send_message(call.message.chat.id, "أرسل رابط الفيديو للحصول على لايكات (10):")
        bot.register_next_step_handler(call.message, lambda msg: process_request(msg, '13584', 10, "لايكات ريلز انستا"))
    elif call.data == "members_telegram":
        bot.send_message(call.message.chat.id, "أرسل رابط القناة أو الجروب للحصول على أعضاء (10):")
        bot.register_next_step_handler(call.message, lambda msg: process_request(msg, '13631', 10, "أعضاء تيليجرام"))

def process_request(message, service_id, quantity, service_name):
    link = message.text
    api_keys = ["44c80938efd247633881b1c0051b3ec0"]
    responses = send_request_to_both(service_id, link, quantity, api_keys)
    
    for response in responses:
        if response:
            if "error" in response:
                if "link_duplicate" in response["error"]:
                    bot.send_message(message.chat.id, f"طلب مكرر بالفعل قيد التنفيذ لـ {service_name}!")
                elif "not_enough_funds" in response["error"]:
                    bot.send_message(message.chat.id, f"رصيد غير كافي لتنفيذ طلب {service_name}.")
                else:
                    bot.send_message(message.chat.id, f"حدث خطأ أثناء تنفيذ طلب {service_name}: {response['error']}")
            elif "order" in response:
                bot.send_message(message.chat.id, f"تم إضافة {service_name} بنجاح من حساب!")
        else:
            bot.send_message(message.chat.id, "حدث خطأ أثناء إرسال الطلب!")


bot.polling()