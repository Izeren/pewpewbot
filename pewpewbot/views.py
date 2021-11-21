from datetime import timedelta

from pewpewbot.state import State
from pewpewbot.models import Sector, Koline, CodeVerdict
from pewpewbot.code_utils import CODE_VERDICT_TO_MESSAGE


def get_tm_safe(state: State):
    if state and state.game_status and state.game_status.current_level:
        return state.game_status.current_level.tm
    else:
        return None


def sector_default_ko_message(sector: Sector, state: State, ko_caption: str):
    """
    Вьюха списка KO в виде текста
    """
    code_list = list(code for code in sector.codes if not code.taken)
    size = len(code_list)
    rows = 5 if size <= 10 else 10  # Сколько элементов в колонке.
    cols = 2  # Колонок всегда 2
    pages = size // (rows * cols) + 1  # Кол-во страниц

    tm = get_tm_safe(state)
    if tm and not ko_caption:
        result = "Taймер на уровне: *{}*\n".format(timedelta(seconds=tm))
    else:
        result = ko_caption
    result += "Название сектора: *{}*\n".format(sector.name)

    result += "```\n"

    for page_index, page in enumerate(range(pages)):  # Номер страницы
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                code_index = page * rows * cols + rows * col + row
                if code_index >= size:
                    continue
                code = code_list[code_index]
                result += "{:<2} {:<3}  {}    ".format(
                    '{}'.format(code.label + 1),
                    code.ko.strip(),
                    'V' if code.taken else ' ',
                )
            result += '\n'

        if page_index != pages - 1:
            result += '\n\n'

    result += "```"

    return result


def not_taken_with_tips(sector: Sector, tips: list):
    """
    Вьюха списка не взятых KO с подсказками
    """
    result = ""

    result += "Сектор: *{}*\n".format(sector.name)
    result += "```\n"

    for code_id, code in enumerate(sector.codes):
        tip = tips[code_id] if code_id < len(tips) else 'Not enough tips provided'
        if code.taken:
            continue
        result += "{:<2} {:<3} {}    \n\n".format('{}'.format(code.label + 1), code.ko, tip)

    result += "```"

    return result


def not_taken_with_tips_for_sector_list(state: State, ko_caption: str):
    tm = get_tm_safe(state)
    if tm and not ko_caption:
        result = "Taймер на уровне: *{}*\n".format(timedelta(seconds=tm))
    else:
        result = ko_caption
    for sector, sector_tip in zip(state.koline.sectors, state.tip):
        if sector_tip:
            result += not_taken_with_tips(sector, sector_tip) + "\n"
        else:
            result += sector_default_ko_message(sector, state, ko_caption) + "\n"
    return result


def get_sectors_list(koline: Koline) -> str:
    """
    :param koline: принимает экземпляр класса Koline
    :return: сообщение с пронумерованным списком секторов
    """
    message = ""
    for sector_id, sector in enumerate(koline.sectors):
        message += f"{sector_id}: *{sector.name}*\n"
    return message


def code_verdict_view(verdict_value: CodeVerdict, code: str) -> str:
    """
    :param verdict_value: Вердикт движка
    :param code: Текст пробитого кода
    :return: Форматированный вердикт для отправленного кода
    """
    return f"{CODE_VERDICT_TO_MESSAGE[verdict_value]}\n*{code}*"


def try_send_code_view(code: str):
    return f'Пытаюсь пробить код: *{code}*'


def code_update_view(verdict: str, tm: int, label: int, ko: str):
    return f'{verdict}\n\u23f0: *{timedelta(seconds=tm)}*, ' + \
           f'\U0001f3f7: *{label + 1}*, \U0001f47b: *{ko}*\n'
