import os
import logging
import telegram as tlg
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater, MessageHandler, CommandHandler#, CallbackContext
import datetime
import urllib.request, json

com1 = {
            'dipoli':      'Dipoli',
            'alvari':      'Alvari',
            'silinteri':   'Silinteri',
            'abloc':       'A Bloc',
            'tuas':        'TUAS'
            }

def start(update, context):
    print('Start')
    msg = 'Choose a Fazer student restaurant:'

    def load_food(choice,lang):
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

    try:
        btns = []
        i = 0
        for key in com1.keys():
            str = '/' + key
            btn = InlineKeyboardButton(com1[key], callback_data=str)
            btns.append([btn])
            i += 1
        reply_markup = InlineKeyboardMarkup(btns)
        update.message.reply_text(msg, reply_markup=reply_markup)
    except:
        print('Sad panda')

def jsfood(choice, lang):

    x = 0#datetime.datetime.today().weekday()
    url0 = 'https://www.fazerfoodco.fi/modules/json/json/Index?costNumber='
    restaurants = {
                'Dipoli':       '3101',
                'Alvari':       '0190',
                'Silinteri':    '019002',
                'A Bloc':       '3087',
                'TUAS':         '0199'
                }
    language = {
                'en': 'en',
                'fi': 'fi'
                }
    url = url0 + restaurants[choice] + '&language=' + language[lang]
    #print(url)
    with urllib.request.urlopen(url) as url1:
        data = json.loads(url1.read().decode())
    #return data

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():

    token = str(os.environ['TOKEN'])
    chat_id = str(os.environ['CHID'])
    #bot = tlg.Bot(token)
    print('Intiation')

    #bot.send_message(chat_id=chat_id, text=msg)


    #i1 = 'TUAS' # replace with message to bot with command
    #data = get_food(i1,'en')
    #print(data["RestaurantName"])
    #date = datetime.datetime.strptime(data['MenusForDays'][0]['Date'],'%Y-%m-%dT%H:%M:%S%z')
    #date2 = datetime.datetime.strftime(date,'%d %b %Y')
    #print(date2)
    #print('Open ' + data['MenusForDays'][0]['LunchTime'])
    #i3 = 0
    #print('Choice %d' % i3)
    #for y in data['MenusForDays'][0]['SetMenus'][i3]['Components']: print(y)
    #print('Prices: ' + data['MenusForDays'][0]['SetMenus'][i3]['Price'])
    #com2 = {}
    #
    updater = Updater(str(os.environ['TOKEN']),use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    cmd1 = []
    for key in com1.keys(): cmd1.append(key)
    dp.add_handler(CommandHandler(cmd1, start))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    print('Start polling')
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
