import os
import sys
import re
from uuid import uuid4
from threading import Thread

#from flask import Flask
#app = Flask(__name__)

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import InputTextMessageContent, InlineQueryResultArticle
#from telegram import ReplyKeyboardMarkup
from telegram import ChatAction, ParseMode
from telegram.ext import Updater, Filters
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, InlineQueryHandler, MessageHandler
from telegram.ext import PicklePersistence
from telegram.utils.helpers import escape_markdown

import datetime
from urllib.request import Request, urlopen
import json
from functools import wraps
import ast

import fixit

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s\n',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


ADMINS = os.environ.get('ADMINS')
ADMINS = x = ast.literal_eval(ADMINS)

url0 = 'https://www.fazerfoodco.fi/modules/json/json/Index?costNumber='
l0 = '&language='
f2zer = {
            'abloc':       ['A Bloc',url0 + '3087' + l0],
            'alvari':      ['Alvari',url0 + '0190' + l0],
            'dipoli':      ['Dipoli',url0 + '3101' + l0],
            'silinteri':   ['Silinteri',url0 + '019002' + l0],
            'tuas':        ['TUAS',url0 + '0199' + l0]
            }

url1 = 'https://www.sodexo.fi/ruokalistat/output/daily_json/'
s0dexo = {
            'kvarkki':              ['Kvarkki', url1 + '86' + '/'],
            'tietotekniikantalo':   ['Tietotekniikantalo', url1 + '6754' + '/'],
            'valimo':               ['Valimo', url1 + '220' + '/']
            }

lunch = {
            'en': 'Lunch ',
            'fi': 'Lounas '
        }
closed = {
            'en': 'Closed today',
            'fi': 'Suljettu tanaan'
        }
ch1m = {
            'en': 'Otaniemi student restaurants:',
            'fi': 'Otaniemen opiskeljaravintolat:'
        }
btnm = {
        'en': '< Back',
        'fi': '< Takaisin'
        }
#ch1m = {}

FIRST, SECOND = range(2)
FB = 1

# Wrap functions for admin protection and typing decoration
def restricted(func):
    """
    Wrapper function that restricts certain commands to ADMIN users.
    """
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        print('Accessed by %d' % user_id)
        return func(update, context, *args, **kwargs)
    return wrapped

def typing(func):
    """
    Function wrapper that makes the bot send typing action while processing command.
    """
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)
    return command_func

# Company-specific functions
def load_fazer(key,lan):
    url = f2zer[key][1] + lan
    rq = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(rq) as u:
        data = json.loads(u.read().decode())

    msg = '<a href="%s">%s</a>\n' % (data['RestaurantUrl'],data["RestaurantName"])
    data = data['MenusForDays'][0]
    d = datetime.datetime.strptime(data['Date'],'%Y-%m-%dT%H:%M:%S%z')
    d2 = d.strftime('%d %b %Y')
    msg += '%s\n' % d2
    lt = data['LunchTime']
    if lt is None or lt == 'Closed' or lt == 'Suljettu':
        msg += '%s\n' % closed[lan]
    else:
        msg += '%s%s\n' % (lunch[lan],lt)
        data = fixit.fazer(key, data, lan)
        for x in data['SetMenus']:
            msg+="<b>%s</b>\n" % x["Name"]
            for y in x['Components']:
                msg+="\t\t\t%s\n" % y
    return msg

def load_sodexo(key, lan):
    z = datetime.datetime.today().weekday()
    if z in range(4):
        x = datetime.datetime.today()
        x1 = x.strftime('%Y-%m-%d')
        url = s0dexo[key][1] + x1
        rq = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(rq) as u:
            data = json.loads(u.read().decode())

        meta = data['meta']
        msg = '<a href="%s">%s</a>\n' % (meta['ref_url'],meta["ref_title"])
        data = data['courses']
        y = x.strftime('%d %b %Y')
        msg += '%s\n' % y
        lt = fixit.sodexo(key)
        msg += '%s%s\n' % (lunch[lan],lt)
        ti = 'title_' + lan
        for f in data.values():
            msg+="<b>%s</b>\n" % f['category']
            if f[ti] is None:
                msg+="\t\t\t%s\n" % f['title_fi']
            else:
                msg+="\t\t\t%s\n" % f[ti]
    else:
        msg = '%s\n' % sodexo[key][0]
        msg += '%s\n' % closed[lan]
    return msg
# Bot commands
# CHOICE conversaton
#@restricted
def start(update, context):
    """
    This is the start of the CHOICE conversation.
    Returns language choice menu and switches conversation to next state.

    Returns:
        FIRST (int): 1st state of the CHOICE conversation.
    """
    msg = 'Choose your language:'
    btns = [
            [
            InlineKeyboardButton('EN', callback_data='en'),
            InlineKeyboardButton('FI', callback_data='fi')
            ]
            ]
    reply_markup = InlineKeyboardMarkup(btns)
    update.message.reply_text(msg, reply_markup=reply_markup)
    context.user_data['lan'] = []
    return FIRST

def choice1(update, context):
    """
    The 1st CHOICE convesation.
    Provides list of student restaurants
    Returns:
        SECOND: 2nd state of the CHOICE conversation, the specific restaurant.
    """
    query = update.callback_query
    bot = context.bot
    cmd = str(query.data)
    if not context.user_data['lan']:
        context.user_data['lan'] = cmd
    lan = context.user_data['lan']

    msg = ch1m[lan]
    try:
        btns = []
        x = [*f2zer.keys()]
        y = [*s0dexo.keys()]
        n = min(len(x),len(y))
        for i in range(n):
            s1 = x[i]
            s2 = y[i]
            btn1 = InlineKeyboardButton(f2zer[s1][0], callback_data=s1)
            btn2 = InlineKeyboardButton(s0dexo[s2][0], callback_data=s2)
            btns.append([btn1,btn2])
        for i in range(n,len(x)):
            s = x[i]
            btn = InlineKeyboardButton(f2zer[s][0], callback_data=s)
            btns.append([btn])
        reply_markup = InlineKeyboardMarkup(btns)
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=msg,
            reply_markup=reply_markup
        )
    except:
        print('Sad panda')
        raise context.error

    return SECOND

def result(update, context):
    """
    The 2nd CHOICE convesation.
    Provides chosen restaurant's lunch time and menu.
    Returns back to restaurant list (FIRST state) on BACK button click.
    Returns:
        FIRST: 1st state of the CHOICE conversation.
    """
    query = update.callback_query
    bot = context.bot
    key = str(query.data)
    lan = context.user_data['lan']
    #datetime.datetime.today().weekday()
    if key in f2zer.keys():
        msg = load_fazer(key,lan)
    elif key in s0dexo.keys():
        msg = load_sodexo(key,lan)
    else:
        msg = []
    #print('Prices: ' + data['MenusForDays'][0]['SetMenus'][i3]['Price'])
    #print(msg)
    btns = []
    s = btnm[lan]
    btnb = InlineKeyboardButton(s,callback_data=lan)
    btns.append([btnb])
    reply_markup = InlineKeyboardMarkup(btns)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=msg,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
        disable_web_page_preview=1
    )
    return FIRST

def help(update, context):
    #print(context.user_data)
    update.message.reply_text("Use /start to use this bot. After that, choose the language and you can navigate the inline menu to your desired restaurant or leave feedback with /fb command")

# FEEDBACK conversation
def fbstart(update, context):
    update.message.reply_text('Please enter your feedback below')
    return FB

def feedback(update, context):
    update.message.reply_text('Thank you for your feedback!')
    context.bot.send_message(chat_id=ADMINS[0], text='FEEDBACK FROM @%s:\n%s' % (update.message.from_user.username , update.message.text))#update.message.text)
    return ConversationHandler.END

# INLINE
def inlinequery(update, context):
    """Handle the inline query."""
    query = update.inline_query.query
    lan = context.user_data['lan']
    results = []
    # InlineQueryResultArticle(id=uuid4(), title="Bold", input_message_content=InputTextMessageContent("*{}*".format(escape_markdown(query)),parse_mode=ParseMode.MARKDOWN))
    for x in f2zer.keys():
        s = load_fazer(x,lan)
        #sr = InlineQueryResultArticle(id=uuid4(), title=f2zer[x][0], input_message_content=s)                                                                    )
        results.append(InlineQueryResultArticle(id=uuid4(), title=f2zer[x][0], input_message_content=InputTextMessageContent(message_text=s,parse_mode=ParseMode.HTML,disable_web_page_preview=True)))
    for x in s0dexo.keys():
        s = load_sodexo(x,lan)
        #r = InlineQueryResultArticle(id=uuid4(), title=s0dexo[x][0],input_message_content=s)
        results.append(InlineQueryResultArticle(id=uuid4(), title=s0dexo[x][0],input_message_content=InputTextMessageContent(message_text=s,parse_mode=ParseMode.HTML,disable_web_page_preview=True)))
    update.inline_query.answer(results)

# OTHER
def language(update, context):
    query = update.callback_query
    bot = context.bot
    if context.args:
        l = context.args[0]
        if l == 'en' or l == 'fi':
            context.user_data['lan'] = l
    else:
        l = 'en'
        context.user_data['lan'] = l
    update.message.reply_text('Language set to %s' % l)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    raise context.error

@restricted
def plans(update, context):
    update.message.reply_text('Plans:\n')

def fazer(update, context):
    #query = update.callback_query
    #bot = context.bot
    lan = context.user_data['lan']
    #print('fazer executed
    key = (update.message.text).split('/')[1]
    print(key)
    msg = load_fazer(key,lan)
    update.message.reply_text(msg,parse_mode=ParseMode.HTML,disable_web_page_preview=1)

def sodexo(update, context):
    #query = update.callback_query
    #bot = context.bot
    lan = context.user_data['lan']
    key = (update.message.text).split('/')[1]
    print(key)
    #print('sodexo executed')
    msg = load_sodexo(key,lan)
    update.message.reply_text(msg,parse_mode=ParseMode.HTML,disable_web_page_preview=1)

def main():
    return 1

if __name__ == '__main__':
    #main()
    TOKEN = os.environ.get('TOKEN')
    NAME = os.environ.get('NAME')
    PORT = PORT = int(os.environ.get('PORT', '8443'))
    ISSERVER = int(os.environ.get('ISSERVER', '0'))
    persisto = PicklePersistence(filename='persisto')
    updater = Updater(TOKEN,persistence=persisto,use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # main conversation handler
    conv1 = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [CallbackQueryHandler(choice1)],
            SECOND: [CallbackQueryHandler(result)]
        },
        fallbacks=[CommandHandler('start', start)],
        persistent=True,
        name='choices'
    )
    dp.add_handler(conv1)

    # Fb conversaton handler
    conv2 = ConversationHandler(
        entry_points=[CommandHandler('fb', fbstart)],
        states={
            FB: [MessageHandler(Filters.text, feedback)]
        },
        fallbacks=[]
    )
    dp.add_handler(conv2)

    # Command handlersfor restaurants
    fz = []
    for x in f2zer.keys():
        fz.append(x)
    dp.add_handler(CommandHandler(fz, fazer))
    sx = []
    for x in s0dexo.keys():
        sx.append(x)
    dp.add_handler(CommandHandler(sx, sodexo))

    @restricted
    def stop(update, context):
        update.message.reply_text("Shutting down")
        updater.stop()
        sys.exit()

    dp.add_handler(CommandHandler('stop', stop))
    #dp.add_handler(CommandHandler('fb', feedback))
    #dp.add_handler(CallbackQueryHandler(button,pattern='^@'))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(InlineQueryHandler(inlinequery))

    @restricted
    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    @restricted
    def restart(update, context):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    dp.add_handler(CommandHandler('r', restart))
    dp.add_handler(CommandHandler('lang', language))
    # log all errors
    dp.add_error_handler(error)

    if ISSERVER:
        print('Starting webhook')
        updater.start_webhook(listen='0.0.0.0',
                                port=int(PORT),
                                url_path=TOKEN)
        updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
    else:
        print('Starting polling')
        updater.start_polling()

    updater.idle()
