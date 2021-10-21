from pewpewbot import commands_processing
from pewpewbot.TgCommand import TgCommand, TgCommandManager
from pewpewbot.patterns import STANDARD_COORDS_PATTERN, STANDARD_CODE_PATTERN

COMMAND_MANAGER = TgCommandManager()

################################################################################
# Current block is for direct bot commands patterns
################################################################################

COMMAND_MANAGER.add_commands(
    TgCommand(
        names=["start", "help"],
        help_text="""
        /start или /help - вывести справку
        """,
        awaitable_action_method=COMMAND_MANAGER.process_help,
        enabled=True,
    ),
    TgCommand(
        names="auth",
        help_text="""
        /auth - авторизация через логин пароль. Использовать так: "/auth login password". 
        Используйте этот метод авторизации, если у вас есть отдельный аккаунта для бота.
        """,
        awaitable_action_method=commands_processing.login,
        enabled=True,
    ),
    TgCommand(
        names="cookie",
        help_text="""
        /cookie - установка авторизационной куки dozorSiteSession. Использовать так: "/cookie KTerByfGopF5dSgFjkl07x8v". 
        Используйте этот метод авторизации, если у вас нет отдельного аккаунта для бота и 
        вы используйте один аккаунт как для бота, так и в браузере.
        """,
        awaitable_action_method=commands_processing.dummy,
        enabled=False,
    ),
    TgCommand(
        names="ko",
        help_text="""
        /ko - прислать актуальную табличку с КО в чат. По умолчанию, присылает только невзятые коды. Если есть запиненная
        подсказка, то будет приписывать каждому невзятому коду текст подсказки
        """,
        awaitable_action_method=commands_processing.send_ko,
        enabled=True,
    ),
    TgCommand(
        names="img",
        help_text="""
        /img - прислать актуальный скриншот штабного дока, если штаб ведет трансляцию
        """,
        awaitable_action_method=commands_processing.img,
        enabled=True,
    ),
    TgCommand(
        names="link",
        help_text="""
        /link - позволяет запинить сообщение, например ссылки на чаты, ссылку в движок и т.д. 
        Для настройки используйте команду "/link <ссылка>", 
        для вывода актуальной ссылки - просто "/link".
        """,
        awaitable_action_method=commands_processing.process_link,
        enabled=True,
    ),
    TgCommand(
        names="tip",
        help_text="""
        /tip - позволяет запинить подсказку для кодов. Подсказка на каждый код должна быть на отдельной строке, а порядок
        подсказок должен соответствовать коду. (секторы пока не поддерживаются). Если в запине есть подсказка, команда ko
        будет выводить список не взятых кодов вместе с подсказкой на код
        """,
        awaitable_action_method=commands_processing.process_tip,
        enabled=True,
    ),
    TgCommand(
        names="get_chat_id",
        help_text="""
        /get_chat_id - возвращает айди чата из которого был запрос к боту, нужно, чтобы пинить чаты, в которые бот будет
        делать рассылку об уровнях
        """,
        awaitable_action_method=commands_processing.process_get_chat_id,
        enabled=True,
    ),
    TgCommand(
        names="pin_chat",
        help_text="""
        /pin_chat - используется с одним из аргументов: main, code, debug. Устанавливает chat_id из которого было 
        отправлено сообщение и ставит в соответствие необходимому параметру: main_chat_id/code_chat_id/debug_chat_id
        """,
        awaitable_action_method=commands_processing.pin_chat,
        enabled=True,
    ),
    TgCommand(
        names="parse",
        help_text="""
        /parse - парсинг движка дозора, /parse on, /parse off для переключения режима. /status, чтобы узнать,
        парсится ли сейчас движок
        """,
        awaitable_action_method=commands_processing.process_parse,
        enabled=True,
    ),
    TgCommand(
        names="maps",
        help_text="""
        /maps - включает парсинг координат из чата. Когда парсинг включен, бот будет присылать локацию в ответ на координаты,
        /maps on, /maps off для переключения режима. /status, чтобы узнать, парсится ли сейчас движок
        """,
        awaitable_action_method=commands_processing.process_maps,
        enabled=True,
    ),
    TgCommand(
        names="pattern",
        help_text="""
        /pattern - регулярное выражение для поиска кода. 
        Чтобы установить стандартное выражение используйте команду "/pattern standard".
        """,
        awaitable_action_method=commands_processing.process_pattern,
        enabled=True,
    ),
    TgCommand(
        names="sleep_seconds",
        help_text="",
        awaitable_action_method=commands_processing.dummy,
        enabled=False,
    ),
    TgCommand(
        names="status",
        help_text="""
        /status - общая информация о подключении к движку. 
        Используйте ее, чтобы понять, авторизованы ли вы и установлен ли пин.
        """,
        awaitable_action_method=commands_processing.get_bot_status,
        enabled=True,
    ),
    TgCommand(
        names="task",
        help_text="/task - текст задания текущего уровня (автоматически присылается при выдаче нового уровня)",
        awaitable_action_method=commands_processing.task,
        enabled=True,
    ),
    TgCommand(
        names="test_error",
        help_text="",
        awaitable_action_method=commands_processing.dummy,
        enabled=False,
    ),
    TgCommand(
        names="type",
        help_text="""
        /type - ввод кодов. /type on, /type off -- переключают режим работы. Если режим ввода кодов включен,
        бот будет пытаться искать паттерны с кодом в каждом сообщении (по умолчанию ищутся стандартные дозорные коды,
        состоящие из букв d, r и цифр, но шаблон можно поменять через команду /pattern 
        """,
        awaitable_action_method=commands_processing.process_type,
        enabled=True,
    ),
    TgCommand(
        names="set",
        help_text="""
        /set key value, позволяет выставить значение переменной в key value формате, работает аналогично link, но позволяет
        указывать настраиваемые ключи
        """,
        awaitable_action_method=commands_processing.set_state_key_value,
        enabled=True,
    ),
    TgCommand(
        names="reset",
        help_text="""
        /reset позволяет сбросить все параметры статуса бота в стандартные значения. Для сброса конкретного параметра
        нужно использовать /reset key. 
        """,
        awaitable_action_method=commands_processing.reset_to_default,
        enabled=True,
    ),
    TgCommand(
        names="get_params",
        help_text="""
        /get_params позволяет узнать все текущие установленные параметры
        """,
        awaitable_action_method=commands_processing.get_all_params,
        enabled=True,
    ),
    TgCommand(
        names="st",
        help_text="""
        /st позволяет зафорсить апдейт статуса бота (для дебага, с выводом в чат)
        """,
        awaitable_action_method=commands_processing.update_level,
        enabled=True,
    ),
    TgCommand(
        names="version",
        help_text="""
        /version позволяет узнать текущую версию бота
        """,
        awaitable_action_method=commands_processing.get_version,
        enabled=True,
    ),
    TgCommand(
        names="",
        help_text="""
        Используйте "/ code" или ".code" чтобы пробить код без проверки регулярного выражения 
        """,
        awaitable_action_method=commands_processing.process_code,
        enabled=True,
        pattern=r"/ ",
    ),
    TgCommand(
        names="",
        help_text="""
        Используйте "/sectors", чтобы получить пронумерованный список секторов
    """,
        awaitable_action_method=commands_processing.list_sectors,
        enabled=True,
        pattern=r"/sectors",
    ),
)
