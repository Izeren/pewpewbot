from datetime import timedelta

from State import State
from models import Sector, ParsedCode


def get_tm_safe(state: State):
    if state and state.game_status and state.game_status.current_level:
        return state.game_status.current_level.tm
    else:
        return None

def sector_default_ko_message(sector: Sector, state: State):
    """
    Вьюха списка KO в виде текста
    """
    code_list = list(code for code in sector.codes if not code.taken)
    size = len(code_list)
    rows = 5 if size <= 10 else 10  # Сколько элементов в колонке.
    cols = 2  # Колонок всегда 2
    pages = size // (rows * cols) + 1  # Кол-во страниц

    result = ""
    tm = get_tm_safe(state)
    if tm:
        result += "Taймер на уровне: *{}*\n".format(timedelta(seconds=tm))
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


def not_taken_with_tips(sector, tips, state: State):
    """
    Вьюха списка не взятых KO с подсказками
    """
    result = ""

    tm = get_tm_safe(state)
    if tm:
        result += "Taймер на уровне: *{}*\n".format(timedelta(seconds=tm))

    result += "Сектор: *{}*\n".format(sector.name)
    result += "```\n"

    for code, tip in zip(sector.codes, tips):
        if code.taken:
            continue
        result += "{:<2} {:<3} {}    \n\n".format('{}'.format(code.label + 1), code.ko, tip)

    result += "```"

    return result
