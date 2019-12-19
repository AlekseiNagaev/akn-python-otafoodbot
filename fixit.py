def fazer(key, data, lan):
    if key == 'abloc':
        data = abloc(data, lan)
    if key == 'alvari':
        data = alvari(data, lan)
    if key == 'dipoli':
        data = dipoli(data, lan)
    if key == 'silinteri':
        data = silinteri(data, lan)
    if key == 'tuas':
        data = tuas(data, lan)
    return data

def del_n(data):
    a = len(data['SetMenus'])
    for i in range(a):
        b = len(data['SetMenus'][i]['Components'])
        for j in range(b):
            data['SetMenus'][i]['Components'][j] = data['SetMenus'][i]['Components'][j].replace('\n','')
    return data

def abloc(data, lan):
    if lan == 'en':
        if data['SetMenus'][0]['Name'] is None:
             data['SetMenus'][0]['Name'] = 'Vegetarian Lunch'
        if data['SetMenus'][2]['Name'] == "Chef´s Kitchen Pizza":
            data['SetMenus'][2]['Name'] = "Chef's Kitchen"
    data = del_n(data)
    return data

def alvari(data, lan):
    data = del_n(data)
    return data

def dipoli(data, lan):
    data = del_n(data)
    return data

def silinteri(data, lan):
    data = del_n(data)
    return data

def tuas(data, lan):
    rpl = {
            0: 'Vegetarian Lunch',
            1: 'Lunch 1',
            2: 'Lunch 2',
            3: 'Fresh Bufee',
            4: 'Special',
            5: 'Dessert'
    }
    for i in range(len(data['SetMenus'])):
        data['SetMenus'][i]['Name'] = rpl[i]
    data = del_n(data)
    return data

def sodexo(key):
    if key == 'kvarkki':
        lt = '10.30 - 14.00'
    if key == 'tietotekniikantalo':
        lt = '11.00 - 15.00'
    if key == 'valimo':
        lt = '10.30 - 14.30'
    return lt
