from datetime import timedelta

from pewpewbot.state import State
from pewpewbot.models import Sector, Koline, CodeVerdict
from pewpewbot.code_utils import CODE_VERDICT_TO_MESSAGE


def get_tm_safe(state: State):
    if state and state.game_status and state.game_status.current_level:
        return state.game_status.current_level.tm
    else:
        return None


def default_sector_caption(sector_name: str):
    return f'Название сектора: *{sector_name}*\n'


def default_ko_caption(tm: int):
    return f'Taймер на уровне: *{timedelta(seconds=tm)}*\n'


def sector_default_ko_message(sector: Sector):
    """
    Вьюха списка KO в виде текста
    """
    def get_paged_list(my_list: list, size: int):
        return [my_list[i:i+size] for i in range(0, len(my_list), size)]
    page_size = 20
    code_list = list(code for code in sector.codes if not code.taken)
    pages = get_paged_list(code_list, page_size)

    result = f"{default_sector_caption(sector.name)}```\n"

    page_results = []
    for page in pages:
        page_result = ''
        height = len(page) // 2 if len(page) > 10 else len(page)
        for row_id in range(height):
            page_result += f'{(page[row_id].label + 1):<2} {page[row_id].ko.strip():<3}\t\t'
            if row_id + height < len(page):
                page_result += f'{(page[row_id + height].label + 1):<2} {page[row_id + height].ko.strip():<3}\t\t'
            page_result += '\n'
        page_results.append(page_result)

    return result + '\n\n'.join(page_results) + "```"


def sector_with_tips_ko_message(sector: Sector, tips: list):
    """
    Вьюха списка не взятых KO с подсказками
    """
    result = f"{default_sector_caption(sector.name)}```\n"
    for code_id, code in enumerate(sector.codes):
        tip = tips[code_id] if code_id < len(tips) else 'Not enough tips provided'
        if code.taken:
            continue
        result += "{:<2} {:<3} {}    \n\n".format('{}'.format(code.label + 1), code.ko, tip)

    result += "```"

    return result


def sector_list_ko_view(state: State, ko_caption: str):
    tm = get_tm_safe(state)
    result = default_ko_caption(tm) if tm and not ko_caption else ko_caption
    sector_tips = state.tip if state.tip else [[] for _ in range(len(state.koline.sectors))]
    for sector, sector_tip in zip(state.koline.sectors, sector_tips):
        if sector_tip:
            result += sector_with_tips_ko_message(sector, sector_tip) + "\n"
        else:
            result += sector_default_ko_message(sector) + "\n"
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


def code_update_view(verdict: str, sector_name: str, tm: int, label: int, ko: str):
    return f'{verdict}\nПо сектору: *{sector_name}*\n\u23f0: *{timedelta(seconds=tm)}*, ' + \
           f'\U0001f3f7: *{label + 1}*, \U0001f47b: *{ko}*\n'
