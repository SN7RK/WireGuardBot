from aiogram import types

REQUEST = '''
<b>Введите название профиля:</b>

Рекомендую использовать название устройства на котором планируется использовать

Например: <i>mobile</i> или <i>notebook</i> или <i>pc</i>

Можно использовать латинские буквы нижнего регистра и цифры а так же знак тире.
'''

REQUEST_SEND = '''
<b>Ваш запрос отправлен админу.</b>

Ожидайте ответа, обычно это занимает пару минут, если админ не спит =).
'''

LINKS = '''
<b>Скачать WireGuard VPN:</b>
'''

LINKS_KEY = types.InlineKeyboardMarkup()
LINKS_KEY.add(types.InlineKeyboardButton(text='🌐 Сайт WireGuard', url='https://www.wireguard.com/install/'))
LINKS_KEY.add(types.InlineKeyboardButton(text='🖥️ Windows x32/x64', url='https://download.wireguard.com/windows-client/wireguard-installer.exe'))
LINKS_KEY.add(types.InlineKeyboardButton(text='🍏 iOS AppStore', url='https://apps.apple.com/us/app/wireguard/id1441195209'))
LINKS_KEY.add(types.InlineKeyboardButton(text='💻 MacOS AppStore', url='https://apps.apple.com/us/app/wireguard/id1451685025?ls=1&mt=12'))
LINKS_KEY.add(types.InlineKeyboardButton(text='🤖 Android GooglePlay', url='https://play.google.com/store/apps/details?id=com.wireguard.android&pli=1'))



