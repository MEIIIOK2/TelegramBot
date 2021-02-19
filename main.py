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

def checkuser(id):
    inlist = False
    for user in users:
        if user[0] == id:
            inlist = True
    return inlist
def forwardtoeveryone(cid,mid,admid=None,markup=None,adminmessage=None,sendtoadmin = False):
    realusers = []
    for user in users:

        if user[1] == cid:
            try:
                bot.forward_message(user[0], user[1], mid)
                bot.send_message(user[0], 'Нажмите после выполнения', reply_markup=markup)
                realusers.append(user)
            except:
                pass
    if adminmessage !=None:
        msg_id = bot.send_message(admid, adminmessage)
        msg_id = msg_id.message_id
        taskslist.append([admid, realusers, msg_id])



@bot.message_handler(commands=['start','help','register','i','p'])
def send_message(message):
    markup = types.InlineKeyboardMarkup()
    itembtndone = types.InlineKeyboardButton('Написать', url='telegram.me/Notification_handler_bot')
    markup.add(itembtndone)
    if message.text =='/help'.lower():
        bot.reply_to(message,'Для того чтобы начать пользоваться ботом:\n'
                             '1)Напишите в чат команду /register\n'
                             '2)Перейдите по ссылке в диалог с ботом и нажмите "Start"\n'
                             'Для создания объявления введите /i а затем текст объявления\n'
                             'ВАЖНО: чтобы бот смог вам написать, ЗАПУСТИТЕ ЕГО (2 пункт)')
    if str(message.text).startswith('/register'.lower()):
        chat_id = message.chat.id
        user_id = message.from_user.id
        user_name = message.text[9:]
        #/register имя фамилия
        usr = [user_id,chat_id,user_name,False]
        if usr in users:
            bot.reply_to(message, 'Вы уже зарегистрированы')
        else:
            users.append(usr)
            bot.reply_to(message, 'Успешная регистрация!')
            bot.send_message(usr[1],'Обязательно напишите боту чтобы он смог отправить вам сообщение',reply_markup=markup)
            with open('data.pickle', "wb") as f:
                pickle.dump(users, f)

    if str(message.text).lower().startswith('/p'):

        if checkuser(message.from_user.id):
            message_id = message.id-1
            chat_id = message.chat.id
            messgetoadmin = "Скоро здесь появится статистика выполнения заданий"
            admin_id = message.from_user.id
            forwardtoeveryone(chat_id,message_id,admin_id,messgetoadmin)
        else:
            bot.reply_to(message,'Вы не зарегистрированы. Используйте команду /register')

    msg = str(message.text)
    if msg.lower().startswith('/i'):
        sender_id = message.from_user.id

        if checkuser(sender_id):
            markup = types.InlineKeyboardMarkup()
            chat_id = message.chat.id
            admin_id = message.from_user.id
            message_id = message.message_id
            itembtndone = types.InlineKeyboardButton('Выполнено', callback_data=f'return-{len(taskslist)}')
            markup.add(itembtndone)
            forwardtoeveryone(chat_id,message_id,admin_id,markup)

        else:
            bot.reply_to(message,'Вы не зарегистрированы. Используйте команду /register')

@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data

    if data.startswith('return-'):
        taskid = int(data[7:])


        admin_id = int(taskslist[taskid][0])
        msg_id = taskslist[taskid][2]

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


        #msg = bot.send_message(admin_id,done+notdone)
        bot.edit_message_text(done+notdone,admin_id,msg_id)
        if  query.from_user.id != admin_id:
            bot.send_message(query.from_user.id,"Ваш ответ принят")

bot.polling()


