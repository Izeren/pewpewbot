import re
import logging

from pewpewbot.models import Koline, Sector

logger = logging.getLogger("parsing")
logger.propagate = False


# This is a separate utils file to prevent circular import of Manager and Utils


def parse_koline_from_string(koline: str) -> Koline:
    koline = koline.replace('null', 'N').strip()
    koline = koline.replace('<span style=\'color:red\'>', 'r')
    koline = koline.replace('</span>', '')
    return Koline(sectors=list(Sector.from_string(raw_sector) for raw_sector in koline.split('<br>') if raw_sector))


def parse_codes_up(question: str) -> int:
    matches = re.findall(r"нужно найти (\d+) верных кодов", question)
    # Ignoring multi sector levels for this functionality
    result = -1
    if matches and len(matches) == 1:
        try:
            result = int(matches[0])
        except Exception as e:
            logger.error(e)
    return result
