import os
import sys
import re
from uuid import uuid4
from threading import Thread
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
import urllib.request, json
from functools import wraps
from configparser import ConfigParser
import fixi
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s\n',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

parser = ConfigParser()
parser.read('config.ini')
TOKEN = parser.get('TOKENS', 'TOKEN')#str(os.environ['TOKEN'])
ADMINS = [int(parser.get('TOKENS', 'ADMINS'))]#[int(os.environ['USERID'])]

fazer = 'https://www.fazerfoodco.fi/modules/json/json/Index?costNumber='
lan = '&language='
food = {
            'dipoli':      ['Dipoli',fazer + '3101' + lan],
            'alvari':      ['Alvari',fazer + '0190' + lan],
            'silinteri':   ['Silinteri',fazer + '019002' + lan],
            'abloc':       ['A Bloc',fazer + '3087' + lan],
            'tuas':        ['TUAS',fazer + '0199' + lan]
            }

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

def load_fazer_en(name):
    url = food[name][1] + 'en'
    with urllib.request.urlopen(url) as url1:
        data = json.loads(url1.read().decode())

    msg = '<a href="%s">%s</a>\n' % (data['RestaurantUrl'],data["RestaurantName"])
    data = data['MenusForDays'][0]
    d = datetime.datetime.strptime(data['Date'],'%Y-%m-%dT%H:%M:%S%z')
    d2 = datetime.datetime.strftime(d,'%d %b %Y')
    msg += '%s\n' % d2
    lt = data['LunchTime']
    if lt is None or lt is 'Closed':
        msg += 'Closed today\n'
    else:
        msg += 'Open %s\n' % lt
        data = fixi.choice(name, data)
        for x in data['SetMenus']:
            msg+="<b>%s</b>\n" % x["Name"]
            for y in x['Components']:
                msg+="\t\t\t%s\n" % y
    return msg
# Bot commands
# CHOICE conversaton
@restricted
def start(update, context):
    """
    Starts conversation with the bot.
    This is 0th state of the CHOICE conversation.
    Returns language choice menu and switches conversation to next state.

    Returns:
        FIRST: 1st state of the CHOICE conversation
    """
    msg = 'Choose your language:'
    btns = [
            [
            InlineKeyboardButton('EN', callback_data='en')#,
            #InlineKeyboardButton('FI', callback_data='fi')
            ]
            ]
    reply_markup = InlineKeyboardMarkup(btns)
    update.message.reply_text(msg, reply_markup=reply_markup)
    return FIRST

def ch1_en(update, context):
    """
    EN version of the 1st CHOICE convesation.
    Provides list of student restaurant choices
    Returns:
        SECOND: 2nd state of the CHOICE conversation.
    """
    query = update.callback_query
    bot = context.bot
    cmd = str(query.data)
    print(cmd)
    context.user_data['lan'] = cmd
    msg = 'Otaniemi student restaurants:'
    try:
        btns = []
        for key in food.keys():
            s = 'en@' + key
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

def js_en(update, context):
    """
    EN version of the 2nd CHOICE convesation.
    Provides chosen restaurant's lunch time and menu.
    Returns back to restaurant list (FIRST state) on BACK button click.
    Returns:
        FIRST: 1st state of the CHOICE conversation.
    """
    query = update.callback_query
    bot = context.bot
    cmd = str(query.data)
    name = re.split('@',cmd)[1]
     #datetime.datetime.today().weekday()
    #print(url)
    msg = load_fazer_en(name)
    #print('Prices: ' + data['MenusForDays'][0]['SetMenus'][i3]['Price'])

    #print(msg)
    btns = []
    btnb = InlineKeyboardButton('Back', callback_data='en')
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

def ch1_fi(update, context):
    query = update.callback_query
    bot = context.bot
    msg = 'Otaniemen opiskeljaravintolat:'
    try:
        btns = []
        for key in food.keys():
            str = 'fi@' + key
            btn = InlineKeyboardButton(food[key][0], callback_data=str)
            btns.append([btn])
        reply_markup = InlineKeyboardMarkup(btns)
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=msg,
            reply_markup=reply_markup,
            disable_web_page_preview=1
        )
    except:
        print('Sad panda')
    return SECOND

#@typing
def js_fi(update, context):
    query = update.callback_query
    bot = context.bot
    cmd = str(query.data)
    s = re.split('@',cmd)[1]
    x = 0#datetime.datetime.today().weekday()
    url = food[s][1] + 'fi'
    with urllib.request.urlopen(url) as url1:
        data = json.loads(url1.read().decode())

    btns = []

    msg = '<a href="%s">%s</a>\n' % (data['RestaurantUrl'],data["RestaurantName"])
    #print(msg)
    d = datetime.datetime.strptime(data['MenusForDays'][0]['Date'],'%Y-%m-%dT%H:%M:%S%z')
    d2 = datetime.datetime.strftime(d,'%d %b %Y')
    msg += '%s\n' % d2
    #print(msg)
    lt = data['MenusForDays'][0]['LunchTime']
    if lt is None or lt is 'Closed':
        msg += 'Suljettu tanaan\n'
    else:
        msg += 'Avaa %s\n' % lt
        for x in data['MenusForDays'][0]['SetMenus']:
            for y in x['Components']:
                print(y)

    btnb = InlineKeyboardButton('Back', callback_data='fi')
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
def inlinequery(update, context):
    """Handle the inline query."""
    query = update.inline_query.query
    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="Caps",
            input_message_content=InputTextMessageContent(
                query.upper())),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Bold",
            input_message_content=InputTextMessageContent(
                "*{}*".format(escape_markdown(query)),
                parse_mode=ParseMode.MARKDOWN)),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Italic",
            input_message_content=InputTextMessageContent(
                "_{}_".format(escape_markdown(query)),
                parse_mode=ParseMode.MARKDOWN))]

    update.inline_query.answer(results)

# OTHER
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
    persisto = PicklePersistence(filename='persisto')
    updater = Updater(TOKEN,persistence=persisto,use_context=True)
    #print('My PID is:', os.getpid())
    # Get the dispa tcher to register handlers
    dp = updater.dispatcher

    conv1 = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [CallbackQueryHandler(ch1_en, pattern='^en'),
                    CallbackQueryHandler(ch1_fi, pattern='^fi')],
            SECOND: [CallbackQueryHandler(js_en, pattern='^en@'),
                    CallbackQueryHandler(js_fi, pattern='^fi@')]
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
    dp.add_handler(InlineQueryHandler(inlinequery))

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    @restricted
    def restart(update, context):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    dp.add_handler(CommandHandler('r', restart))
    # log all errors
    dp.add_error_handler(error)
    print('Start polling')
    updater.start_polling()
    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
