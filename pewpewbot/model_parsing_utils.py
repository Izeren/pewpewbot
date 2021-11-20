from pewpewbot.models import Koline, Sector

# This is a separate utils file to prevent circular import of Manager and Utils


def parse_koline_from_string(koline: str) -> Koline:
    koline = koline.replace('null', 'N').strip()
    koline = koline.replace('<span style=\'color:red\'>', 'r')
    koline = koline.replace('</span>', '')
    return Koline(sectors=list(Sector.from_string(raw_sector) for raw_sector in koline.split('<br>') if raw_sector))
