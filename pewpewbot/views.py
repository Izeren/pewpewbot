from models import Sector, ParsedCode


def sector_default_ko_message(sector: Sector):
    """
    Вьюха списка KO в виде текста
    """
    code_list = list(code for code in sector.codes if not code.taken)
    size = len(code_list)
    rows = 5 if size <= 10 else 10  # Сколько элементов в колонке.
    cols = 2  # Колонок всегда 2
    pages = size // (rows * cols) + 1  # Кол-во страниц

    result = "Название сектора: *{}*\n".format(sector.name)
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


def not_taken_with_tips(sector, tip):
    """
    Вьюха списка не взятых KO с подсказками
    """
    result = "Сектор: *{}*\n".format(sector.name)
    result += "```\n"

    tips = tip.strip().split('\n')
    for code in sector.codes:
        if code.taken:
            continue
        tip = ''
        if code.label < len(tips):
            tip = tips[code.label]
        result += "{:<2} {:<3} {}    \n\n".format('{}'.format(code.label + 1), code.ko, tip)

    result += "```"

    return result
