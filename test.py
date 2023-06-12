import locale
from datetime import datetime, timedelta

locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))
text = '9 июня, 22:00'
nyear = datetime.now().year
print(nyear)

a = datetime.now()
print(a.strftime("%d %B %Y %c"))
mdict = {
    'янв': '01',
    'фев': '02',
    'мар': '03',
    'апр': '04',
    'май': '05',
    'июн': '06',
    'июл': '07',
    'авг': '08',
    'сен': '09',
    'окт': '10',
    'ноя': '11',
    'дек': '12'
}
d = f'0{text.split()[0]}'[-2:]
m = mdict[text.split()[1][:3]]
y = datetime.now().year
t = text.split()[-1]

nd = ' '.join(map(str, [d, m, y, t]))
print(nd)

tt = datetime.strptime(nd, "%d %m %Y %H:%M")
print(tt)

print(datetime.now() - timedelta(days=1))
