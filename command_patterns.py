import commands_processing
from TgCommand import TgCommand
from patterns import STANDARD_COORDS_PATTERN, STANDARD_CODE_PATTERN


################################################################################
# Current block is for direct bot commands patterns
################################################################################

AUTH_COMMAND = TgCommand('auth', '''
    /auth - авторизация через логин пароль. Использовать так: "/auth login password". 
Используйте этот метод авторизации, если у вас есть отдельный аккаунта для бота.
''', commands_processing.dummy)

PARSE_COORDS_COMMAND = TgCommand('', '''
    Посылает в чат сообщение в формате location, если видит сообщение с координатами(пример: 55.786064, 37.595543), 
если включен режим парсинга координат. Управляется через /set maps on, /set maps of
''', commands_processing.dummy, True, STANDARD_COORDS_PATTERN)

PARSE_CODE_COMMAND = TgCommand('', '''
    Пытается распарсить сообщение как код для движка согласно шаблону. По-умолчанию парсятся стандартные коды, 
содержащие цифры и буквы d/r (по подной букве каждого вида), шаблон можно поменять при помощи комманды /pattern
''', commands_processing.dummy, True, STANDARD_CODE_PATTERN)

COOKIE_COMMAND = TgCommand('cookie', '''
    /cookie - установка авторизационной куки dozorSiteSession. Использовать так: "/cookie KTerByfGopF5dSgFjkl07x8v". 
Используйте этот метод авторизации, если у вас нет отдельного аккаунта для бота и 
вы используйте один аккаунт как для бота, так и в браузере.
''', commands_processing.dummy, False)

KO_COMMAND = TgCommand('ko', '''
    /ko - прислать актуальную табличку с КО в чат. По умолчанию, присылает только невзятые коды. Если есть запиненная
подсказка, то будет приписывать каждому невзятому коду текст подсказки
''', commands_processing.send_ko, False)

IMG_COMMAND = TgCommand('img', '''
    /img - прислать актуальную изображение с КО в чат.
''', commands_processing.dummy, False)

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
''', commands_processing.dummy, True)

PARSE_COMMAND = TgCommand('parse', '''
    /parse - парсинг движка дозора, /parse on, /parse off для переключения режима. /status, чтобы узнать,
парсится ли сейчас движок
''', commands_processing.process_parse, True)

PATTERN_COMMAND = TgCommand('pattern', '''
    /pattern - регулярное выражение для поиска кода. 
Чтобы установить стандартное выражение используйте команду "/pattern standard".
''', commands_processing.process_pattern, False)

PIN_COMMAND = TgCommand('pin', '''
    /pin - устанавливает пин для доступа в игру (если для игры не установлен пин, ничего делать не нужно)
Использовать так: "/pin moscow_captain:123456", где moscow_captain и 123456 - данные, выдаваемые организаторами.
''', commands_processing.dummy, False)

SLEEP_SECONDS_COMMAND = TgCommand('sleep_seconds', '''
''', commands_processing.dummy, False)

STATUS_COMMAND = TgCommand('status', '''
    /status - общая информация о подключении к движку. 
Используйте ее, чтобы понять, авторизованы ли вы и установлен ли пин.
''', commands_processing.dummy, False)

TEST_ERROR_COMMAND = TgCommand('test_error', '''
''', commands_processing.dummy, False)

TYPE_COMMAND = TgCommand('type', '''
    /type - ввод кодов. /type on, /type off -- переключают режим работы. Если режим ввода кодов включен,
бот будет пытаться искать паттерны с кодом в каждом сообщении (по умолчанию ищутся стандартные дозорные коды,
состоящие из букв d, r и цифр, но шаблон можно поменять через команду /pattern 
''', commands_processing.dummy, False)

SET_COMMAND = TgCommand('set', '''
    /set key value, позволяет выставить значение переменной в key value формате, используется например для переключение
режима ввода координат (локация в чат): /set maps on, /set maps off
''', commands_processing.dummy, False)

