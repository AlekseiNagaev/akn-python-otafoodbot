import os
import sys
import re
#from uuid import uuid4
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
import urllib.request
import json
from functools import wraps

import fixi

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s\n',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


ADMINS = os.environ.get('ADMINS')

fazer = 'https://www.fazerfoodco.fi/modules/json/json/Index?costNumber='
lang = '&language='
food = {
            'dipoli':      ['Dipoli',fazer + '3101' + lang],
            'alvari':      ['Alvari',fazer + '0190' + lang],
            'silinteri':   ['Silinteri',fazer + '019002' + lang],
            'abloc':       ['A Bloc',fazer + '3087' + lang],
            'tuas':        ['TUAS',fazer + '0199' + lang]
            }
open = {
            'en': 'Open ',
            'fi': 'Avaa '
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

# Additional functions

def load_food():
    """
    [UNUSED]
    Loads lunch menu from .json file.
    Returns:
        data (json): data from the restaurant
    """
    filename = {
                'Dipoli':       'dipoli',
                'Alvari':       'alvari',
                'Silinteri':    'silinteri',
                'A Bloc':       'abloc',
                'TUAS':         'tuas'
                }
    ext = '.json'
    for key in filename.keys():
        filename[key] += lang
        filename[key] += ext
        with open(filename[key], 'r') as f:
            data = json.load(f)
    return data

def load_fazer(key,lan):
    url = food[key][1] + lan
    with urllib.request.urlopen(url) as url1:
        data = json.loads(url1.read().decode())

    msg = '<a href="%s">%s</a>\n' % (data['RestaurantUrl'],data["RestaurantName"])
    data = data['MenusForDays'][0]
    d = datetime.datetime.strptime(data['Date'],'%Y-%m-%dT%H:%M:%S%z')
    d2 = datetime.datetime.strftime(d,'%d %b %Y')
    msg += '%s\n' % d2
    lt = data['LunchTime']
    if lt is None or lt == 'Closed' or lt == 'Suljettu':
        msg += '%s\n' % closed[lan]
    else:
        msg += '%s %s\n' % (open[lan],lt)
        data = fixi.choice(key, data)
        for x in data['SetMenus']:
            msg+="<b>%s</b>\n" % x["Name"]
            for y in x['Components']:
                msg+="\t\t\t%s\n" % y
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
    lan = context.user_data['lan']
    cmd = str(query.data)
    if lan != cmd:
        context.user_data['lan'] = cmd
        lan = context.user_data['lan']

    msg = ch1m[lan]
    try:
        btns = []
        for key in food.keys():
            s = key
            btn = InlineKeyboardButton(food[key][0], callback_data=s)
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
    #print(url)
    msg = load_fazer(key,lan)
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
    print(context.user_data)
    update.message.reply_text("Use /start to use this bot. After that, you can navigate the inline menu to your desired restaurant or leave feedback with /fb command")

# FEEDBACK conversation
def fbstart(update, context):
    update.message.reply_text('Please enter your feedback below')
    return FB

def feedback(update, context):
    update.message.reply_text('Thank you for your feedback!')
    context.bot.send_message(chat_id=ADMINS[0], text='FEEDBACK FROM %d:\n%s' % (update.message.from_user.id,update.message.text))#update.message.text)
    return ConversationHandler.END

# INLINE
#def inlinequery(update, context):
    #"""Handle the inline query."""
    #query = update.inline_query.query
    #results = [
        #InlineQueryResultArticle(
            #id=uuid4(),
            #title="Caps",
            #input_message_content=InputTextMessageContent(
                #query.upper())),
        #InlineQueryResultArticle(
            #id=uuid4(),
            #title="Bold",
            #input_message_content=InputTextMessageContent(
                #"*{}*".format(escape_markdown(query)),
                #parse_mode=ParseMode.MARKDOWN)),
        #InlineQueryResultArticle(
            #id=uuid4(),
            #title="Italic",
            #input_message_content=InputTextMessageContent(
                #"_{}_".format(escape_markdown(query)),
                #parse_mode=ParseMode.MARKDOWN))]

    #update.inline_query.answer(results)

# OTHER
def lan(update, context):
    query = update.callback_query
    bot = context.bot
    l = context.args[0]
    if l == 'en' or l == 'fi':
        context.user_data['lan'] = l
    update.message.reply_text('Language set to %s' % l)
    m_id =query.message.message_id + 1
    bot.delete_message(
        chat_id=query.message.chat_id,
        message_id=m_id,
        timeout=5
    )

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

@restricted
def plans(update, context):
    update.message.reply_text('Plans:\n')

def fazer(update, context):
    return 1

def sodexo(update, context):
    return 1

def main():
    return 1

if __name__ == '__main__':
    #main()
    TOKEN = os.environ.get('TOKEN')
    NAME = os.environ.get('NAME')
    PORT = PORT = int(os.environ.get('PORT', '8443'))

    print(TOKEN)
    print(NAME)
    print(PORT)
    print(ADMINS)
    persisto = PicklePersistence(filename='persisto')
    updater = Updater(TOKEN,persistence=persisto,use_context=True)
    #print('My PID is:', os.getpid())
    # Get the dispa tcher to register handlers
    dp = updater.dispatcher

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

    conv2 = ConversationHandler(
        entry_points=[CommandHandler('fb', fbstart)],
        states={
            FB: [MessageHandler(Filters.text, feedback)]
        },
        fallbacks=[]
    )
    dp.add_handler(conv2)

    @restricted
    def stop(update, context):
        update.message.reply_text("Shutting down")
        updater.stop()
        sys.exit()

    dp.add_handler(CommandHandler('stop', stop))
    dp.add_handler(CommandHandler('fb', feedback))
    #dp.add_handler(CallbackQueryHandler(button,pattern='^@'))
    dp.add_handler(CommandHandler('help', help))
    #dp.add_handler(InlineQueryHandler(inlinequery))

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    @restricted
    def restart(update, context):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    dp.add_handler(CommandHandler('r', restart))
    dp.add_handler(CommandHandler('lang', lan))
    # log all errors
    dp.add_error_handler(error)
    print('Started webhook')

    updater.start_webhook(listen='0.0.0.0',
                            port=int(PORT),
                            url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
    #print('Started polling')
    #updater.start_polling()
    updater.idle()
