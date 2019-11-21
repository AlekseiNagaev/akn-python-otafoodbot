import telegram as tlg
import urllib.request, json, datetime
filename = {
            'Dipoli':       'dipoli',
            'Alvari':       'alvari',
            'Silinteri':    'silinteri',
            'A Bloc':       'abloc',
            'TUAS':         'tuas'
            }
ext = '.json'
for key in filename.keys(): filename[key] += ext
#print(filename)
x = 0#datetime.datetime.today().weekday()
print(x)
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
url = {}
i2 = 'en'
for key in restaurants.keys():  url[key] = url0 + restaurants[key] + '&language=' + language[i2]
#print(url)
data = {}
if not x:
    for key in url.keys():
        with urllib.request.urlopen(url[key]) as url1:
            data[key]= json.loads(url1.read().decode())
            with open(filename[key], 'w') as f:
                json.dump(data[key], f)
else:
    for key in filename.keys():
        with open(filename[key], 'r') as f:
            data[key] = json.load(f)

i1 = 'TUAS'
print(data[i1]["RestaurantName"])
date = datetime.datetime.strptime(data[i1]['MenusForDays'][x]['Date'],'%Y-%m-%dT%H:%M:%S%z')
date2 = datetime.datetime.strftime(date,'%d %b %Y')
print(date2)
print('Open ' + data[i1]['MenusForDays'][x]['LunchTime'])
i3 = 0
print('Choice %d' % i3)
for y in data[i1]['MenusForDays'][x]['SetMenus'][i3]['Components']: print(y)
print('Prices: ' + data[i1]['MenusForDays'][x]['SetMenus'][i3]['Price'])

msg = ''
for key in filename.keys(): msg = msg + key + '\n'
token = '560292623:AAFxD5Ucsdy2O71bh2SWaKIgTT7tqzCS0Ok'
bot = tlg.Bot(token)
chat_id = '156097768'
##bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
bot.send_message(chat_id=chat_id, text=msg)
