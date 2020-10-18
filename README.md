# Телеграм бот команды Пиу-Пиу
Используется для игры в дозор в качестве прокси к движку: http://classic.dzzzr.ru
Основной функционал бота:
1. Отправлять коды из телеграмм чата в движок (автопарсинг по шаблону или отправка через '/ code'|'.code' без проверки шаблона)
2. Информировать полевых игроков о "не взятых" кодах
3. Для простых уровней на "тупопилево" показывать подсказки по "не взятым" кодам
4. Информировать команду о начале нового уровня
5. Сообщать о появлении новых подсказок и по возможности парсить парсить подсказки, чтобы сообщать подсказки только по не взятым кодам (уже можно руками установить подсказки для одного сектора, предстоит сделать автопарсинг для заданий с множественными секторами)
6. Автоматически парсить координаты из чата (слать в ответ локацию). Может быть удобно для пересылки координат парковки на уровне.


Результат вывода команды help или start:


/start или /help - вывести справку

    /auth - авторизация через логин пароль. Использовать так: "/auth login password". 
Используйте этот метод авторизации, если у вас есть отдельный аккаунта для бота.

    /ko - прислать актуальную табличку с КО в чат. По умолчанию, присылает только невзятые коды. Если есть запиненная
подсказка, то будет приписывать каждому невзятому коду текст подсказки

    /link - позволяет запинить сообщение, например ссылки на чаты, ссылку в движок и т.д. 
Для настройки используйте команду "/link <ссылка>", 
для вывода актуальной ссылки - просто "/link".

    /tip - позволяет запинить подсказку для кодов. Подсказка на каждый код должна быть на отдельной строке, а порядок
подсказок должен соответствовать коду. (секторы пока не поддерживаются). Если в запине есть подсказка, команда ko
будет выводить список не взятых кодов вместе с подсказкой на код

    /get_chat_id - возвращает айди чата из которого был запрос к боту, нужно, чтобы пинить чаты, в которые бот будет
делать рассылку об уровнях

    /parse - парсинг движка дозора, /parse on, /parse off для переключения режима. /status, чтобы узнать,
парсится ли сейчас движок

    /maps - включает парсинг координат из чата. Когда парсинг включен, бот будет присылать локацию в ответ на координаты,
/maps on, /maps off для переключения режима. /status, чтобы узнать, парсится ли сейчас движок

    /pattern - регулярное выражение для поиска кода. 
Чтобы установить стандартное выражение используйте команду "/pattern standard".

    /status - общая информация о подключении к движку. 
Используйте ее, чтобы понять, авторизованы ли вы и установлен ли пин.

    /type - ввод кодов. /type on, /type off -- переключают режим работы. Если режим ввода кодов включен,
бот будет пытаться искать паттерны с кодом в каждом сообщении (по умолчанию ищутся стандартные дозорные коды,
состоящие из букв d, r и цифр, но шаблон можно поменять через команду /pattern 

    /set key value, позволяет выставить значение переменной в key value формате, работает аналогично link, но позволяет
указывать настраиваемые ключи

    /st позволяет зафорсить апдейт статуса бота (для дебага, с выводом в чат)

    Используйте "/ code" или ".code" чтобы пробить код без проверки регулярного выражения
