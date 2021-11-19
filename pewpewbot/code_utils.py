from pewpewbot.models import CodeVerdict

CODE_VERDICT_TO_MESSAGE = {
    CodeVerdict.ACCEPTED.value: "\u2705 Код принят \u2705",
    CodeVerdict.ACCEPTED_NEXT_LEVEL.value: "\U0001F3C6 Взят последний код на уровне \U0001F3C6",
    CodeVerdict.BONUS_ACCEPTED.value: "\u2705 Принят бонусный код \u2705",
    CodeVerdict.BONUS_REPEAT.value: "\U0001F504 Повтор кода к бонусу \U0001F504",
    CodeVerdict.REPEAT.value: "\U0001F504 Повторно введенный код \U0001F504",
    CodeVerdict.COMPOUND_ACCEPTED.value: "\u2705 Принят составной код \u2705",
    CodeVerdict.REJECTED.value: "\u26d4 Неверный код\u26d4",
    CodeVerdict.POSSIBLY_REPEAT.value: "\U0001F504 Повтор кода к спойлеру \U0001F504",
}

GOOD_VERDICTS = {
    CodeVerdict.ACCEPTED.value,
    CodeVerdict.ACCEPTED_NEXT_LEVEL.value,
    CodeVerdict.BONUS_ACCEPTED.value,
    CodeVerdict.COMPOUND_ACCEPTED.value,
}
