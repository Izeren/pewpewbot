from models import CodeVerdict

CODE_VERDICT_TO_MESSAGE = {
    CodeVerdict.ACCEPTED.value: "Код принят",
    CodeVerdict.ACCEPTED_NEXT_LEVEL.value: "Взят последний код на уровне",
    CodeVerdict.BONUS_ACCEPTED.value: "Принят бонусный код",
    CodeVerdict.BONUS_REPEAT.value: "Повторно введен бонусный код",
    CodeVerdict.REPEAT.value: "Повторно введенный код",
    CodeVerdict.COMPOUND_ACCEPTED.value: "Принят составной код",
    CodeVerdict.REJECTED.value: "Неверный код",
    CodeVerdict.POSSIBLY_REPEAT.value: "Повторно введен код к спойлеру",
}

GOOD_VERDICTS = {
    CodeVerdict.ACCEPTED.value,
    CodeVerdict.ACCEPTED_NEXT_LEVEL.value,
    CodeVerdict.BONUS_ACCEPTED.value,
    CodeVerdict.COMPOUND_ACCEPTED.value,
}

ACCEPTED_VERDICTS = {
    CodeVerdict.ACCEPTED.value,
    CodeVerdict.BONUS_ACCEPTED.value,
    CodeVerdict.COMPOUND_ACCEPTED.value
}
