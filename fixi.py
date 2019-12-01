def choice(name, data, lan):
    if name == 'abloc':
        data = abloc(data, lan)
    if name == 'alvari':
        data = alvari(data, lan)
    if name == 'dipoli':
        data = dipoli(data, lan)
    if name == 'silinteri':
        data = silinteri(data, lan)
    if name == 'tuas':
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
    data['SetMenus'][0]['Name'] = 'Vegetarian Lunch'
    data['SetMenus'][1]['Name'] = 'Lunch 1'
    data['SetMenus'][2]['Name'] = 'Lunch 2'
    data['SetMenus'][3]['Name'] = 'Fresh Bufee'
    data['SetMenus'][4]['Name'] = 'Special'
    data['SetMenus'][5]['Name'] = 'Dessert'
    data = del_n(data)
    return data
