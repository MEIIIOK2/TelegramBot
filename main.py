import telebot
import creds
from telebot import types
import pickle
bot = telebot.TeleBot(creds.key)
users=[]
try:
    with open('data.pickle', "rb") as f:
        users = pickle.load(f)
except:
    pass
print(len(users))

@bot.message_handler(commands=['start','help','register','i'])
def send_message(message):
    markup = types.InlineKeyboardMarkup()
    itembtndone = types.InlineKeyboardButton('Написать', url='telegram.me/Notification_handler_bot')
    markup.add(itembtndone)
    if message.text =='/help':
        bot.reply_to(message,'Для того чтобы начать пользоваться ботом:\n'
                             '1)Напишите в чат команду /register\n'
                             '2)Перейдите по ссылке в диалог с ботом и нажмите "Start"\n'
                             'Для создания объявления введите /i а затем текст объявления\n'
                             'ВАЖНО: чтобы бот смог вам написать, ЗАПУСТИТЕ ЕГО (2 пункт)')
    if message.text =='/register':
        chat_id = message.chat.id
        user_id = message.from_user.id
        usr = [user_id,chat_id]
        if usr in users:
            bot.reply_to(message, 'Вы уже зарегистрированы')
        else:
            users.append(usr)
            bot.reply_to(message, 'Успешная регистрация!')
            bot.send_message(usr[1],'Обязательно напишите боту чтобы он смог отправить вам сообщение',reply_markup=markup)
            with open('data.pickle', "wb") as f:
                pickle.dump(users, f)
        for usr in users:
            print(usr)

    msg = str(message.text)
    if msg.startswith('/i'):
        sender_id = message.from_user.id
        inlist = False
        for user in users:
            if user[0] == sender_id:
                inlist = True
        if inlist:
            markup = types.InlineKeyboardMarkup()
            chat_id = message.chat.id
            admin_id = message.from_user.id
            message_id = message.message_id
            itembtndone = types.InlineKeyboardButton('Выполнено', callback_data=f'return-{admin_id}')
            markup.add(itembtndone)
            for user in users:
                user.append(admin_id)
                if user[1] ==chat_id:
                    try:
                        bot.forward_message(user[0],user[1],message_id)
                        bot.send_message(user[0],'Нажмите после выполнения',reply_markup=markup)
                    except:
                        pass
        else:
            bot.reply_to(message,'Вы не зарегистрированы. Используйте команду /register')

@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
   data = query.data

   if data.startswith('return-'):
       chat_id = int(data[7:])


       bot.send_message(chat_id,f'{query.from_user.first_name} Выполнил задание')
       bot.send_message(query.from_user.id,"Спасибо!")





bot.polling()