import telebot
import creds
from telebot import types
import pickle
bot = telebot.TeleBot(creds.key)
users=[]
taskslist=[]
try:
    with open('data.pickle', "rb") as f:
        users = pickle.load(f)
    with open('taskslist.pickle', "rb") as f:
        taskslist = pickle.load(f)
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
        user_name = message.from_user.first_name
        usr = [user_id,chat_id,user_name,False]
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
            itembtndone = types.InlineKeyboardButton('Выполнено', callback_data=f'return-{len(taskslist)}')
            markup.add(itembtndone)
            realusers=[]
            for user in users:

                if user[1] ==chat_id:
                    try:
                        bot.forward_message(user[0],user[1],message_id)
                        bot.send_message(user[0],'Нажмите после выполнения',reply_markup=markup)
                        realusers.append(user)
                    except:
                        pass
            msg_id = bot.send_message(admin_id,"Скоро здесь появится статистика выполнения заданий")
            print(msg_id)
            msg_id = msg_id.message_id
            print(msg_id)
            taskslist.append([admin_id,realusers,msg_id])

        else:
            bot.reply_to(message,'Вы не зарегистрированы. Используйте команду /register')

@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data

    if data.startswith('return-'):
        taskid = int(data[7:])


        admin_id = int(taskslist[taskid][0])
        msg_id = taskslist[taskid][2]
        print(taskslist)
        userslist=taskslist[taskid][1]

        thisuser=query.from_user.id
        done='Выполнили задание: \n'
        notdone='Не выполнили задание:\n'

        for user in userslist:
            if user[0] == thisuser:
                user[3] =True
            if user[3]:
                done+=user[2]+'\n'
            else:
                notdone+=user[2]+'\n'
        taskslist[taskid][1] = userslist
        with open('taskslist.pickle', "wb") as f:
            pickle.dump(taskslist,f)
        bot.edit_message_reply_markup(query.from_user.id,query.message.id)
        print(len(taskslist))
        print(msg_id)
        #msg = bot.send_message(admin_id,done+notdone)
        bot.edit_message_text(done+notdone,admin_id,msg_id)

        bot.send_message(query.from_user.id,"Ваш ответ принят")

bot.polling()