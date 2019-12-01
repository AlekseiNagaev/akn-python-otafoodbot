def choice(name, data):
    if name == 'abloc':
        data = abloc(data)
    if name == 'alvari':
        data = alvari(data)
    if name == 'dipoli':
        data = dipoli(data)
    if name == 'silinteri':
        data = silinteri(data)
    if name == 'tuas':
        data = tuas(data)
    return data

def del_n(data):
    a = len(data['SetMenus'])
    for i in range(a):
        b = len(data['SetMenus'][i]['Components'])
        for j in range(b):
            data['SetMenus'][i]['Components'][j] = data['SetMenus'][i]['Components'][j].replace('\n','')
    return data

def abloc(data):
    if data['SetMenus'][0]['Name'] is None:
         data['SetMenus'][0]['Name'] = 'Vegetarian Lunch'
    if data['SetMenus'][2]['Name'] == "Chef´s Kitchen Pizza":
        data['SetMenus'][2]['Name'] = "Chef's Kitchen"
    data = del_n(data)
    return data

def alvari(data):
    data = del_n(data)
    return data

def dipoli(data):
    data = del_n(data)
    return data

def silinteri(data):
    data = del_n(data)
    return data

def tuas(data):
    data = del_n(data)
    return data
