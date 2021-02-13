from pewpewbot import commands_processing
from pewpewbot.TgCommand import TgCommand
from pewpewbot.patterns import STANDARD_COORDS_PATTERN, STANDARD_CODE_PATTERN


################################################################################
# Current block is for direct bot commands patterns
################################################################################

START_COMMAND = TgCommand(['start', 'help'], '''
    /start или /help - вывести справку
''', commands_processing.help, True)

AUTH_COMMAND = TgCommand('auth', '''
    /auth - авторизация через логин пароль. Использовать так: "/auth login password". 
Используйте этот метод авторизации, если у вас есть отдельный аккаунта для бота.
''', commands_processing.login, True)

COOKIE_COMMAND = TgCommand('cookie', '''
    /cookie - установка авторизационной куки dozorSiteSession. Использовать так: "/cookie KTerByfGopF5dSgFjkl07x8v". 
Используйте этот метод авторизации, если у вас нет отдельного аккаунта для бота и 
вы используйте один аккаунт как для бота, так и в браузере.
''', commands_processing.dummy, False)

KO_COMMAND = TgCommand('ko', '''
    /ko - прислать актуальную табличку с КО в чат. По умолчанию, присылает только невзятые коды. Если есть запиненная
подсказка, то будет приписывать каждому невзятому коду текст подсказки
''', commands_processing.send_ko, True)

IMG_COMMAND = TgCommand('img', '''
    /img - прислать актуальный скриншот штабного дока, если штаб ведет трансляцию
''', commands_processing.img, True)

LINK_COMMAND = TgCommand('link', '''
    /link - позволяет запинить сообщение, например ссылки на чаты, ссылку в движок и т.д. 
Для настройки используйте команду "/link <ссылка>", 
для вывода актуальной ссылки - просто "/link".
''', commands_processing.process_link, True)

TIP_COMMAND = TgCommand('tip', '''
    /tip - позволяет запинить подсказку для кодов. Подсказка на каждый код должна быть на отдельной строке, а порядок
подсказок должен соответствовать коду. (секторы пока не поддерживаются). Если в запине есть подсказка, команда ko
будет выводить список не взятых кодов вместе с подсказкой на код
''', commands_processing.process_tip, True)

GET_CHAT_ID_COMMAND = TgCommand('get_chat_id', '''
    /get_chat_id - возвращает айди чата из которого был запрос к боту, нужно, чтобы пинить чаты, в которые бот будет
делать рассылку об уровнях
''', commands_processing.process_get_chat_id, True)

PARSE_COMMAND = TgCommand('parse', '''
    /parse - парсинг движка дозора, /parse on, /parse off для переключения режима. /status, чтобы узнать,
парсится ли сейчас движок
''', commands_processing.process_parse, True)

HEAD_DOC_COMMAND = TgCommand('head_doc', '''
    /head_doc - трансляция штабного дока, /head_doc on, /head_doc off для переключения режима
''', commands_processing.process_head_doc, True)

MAPS_COMMAND = TgCommand('maps', '''
    /maps - включает парсинг координат из чата. Когда парсинг включен, бот будет присылать локацию в ответ на координаты,
/maps on, /maps off для переключения режима. /status, чтобы узнать, парсится ли сейчас движок
''', commands_processing.process_maps, True)

PATTERN_COMMAND = TgCommand('pattern', '''
    /pattern - регулярное выражение для поиска кода. 
Чтобы установить стандартное выражение используйте команду "/pattern standard".
''', commands_processing.process_pattern, True)

SLEEP_SECONDS_COMMAND = TgCommand('sleep_seconds', '''
''', commands_processing.dummy, False)

STATUS_COMMAND = TgCommand('status', '''
    /status - общая информация о подключении к движку. 
Используйте ее, чтобы понять, авторизованы ли вы и установлен ли пин.
''', commands_processing.get_bot_status, True)

TEST_ERROR_COMMAND = TgCommand('test_error', '''
''', commands_processing.dummy, False)

TYPE_COMMAND = TgCommand('type', '''
    /type - ввод кодов. /type on, /type off -- переключают режим работы. Если режим ввода кодов включен,
бот будет пытаться искать паттерны с кодом в каждом сообщении (по умолчанию ищутся стандартные дозорные коды,
состоящие из букв d, r и цифр, но шаблон можно поменять через команду /pattern 
''', commands_processing.process_type, True)

SET_COMMAND = TgCommand('set', '''
    /set key value, позволяет выставить значение переменной в key value формате, работает аналогично link, но позволяет
указывать настраиваемые ключи
''', commands_processing.set_state_key_value, True)

ST_COMMAND = TgCommand('st', '''
    /st позволяет зафорсить апдейт статуса бота (для дебага, с выводом в чат)
''', commands_processing.update_level, True)

FORCE_CODE_COMMAND = TgCommand('', '''
    Используйте "/ code" или ".code" чтобы пробить код без проверки регулярного выражения 
''', commands_processing.process_code, True, pattern=r'/ ')
