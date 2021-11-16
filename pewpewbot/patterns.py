
# File with standard patterns for parsing telegram chat messages

# Default pattern for parsing coordinates from telegram chat
STANDARD_COORDS_PATTERN = r'(\d{2}[\.,]\d{3,})'
# Cyrillic DR pattern. To be automatically mapped into latin DR
CYRILLIC_DR_PATTERN = r'\d*[др]\d*[др]\d*'
# Default pattern for parsing standard dozor code from telegram chat
# supports classic dr codes, cyrillic dr codes and word123 format
STANDARD_CODE_PATTERN = r'\d*[dr]\d*[dr]\d*|\d*[др]\d*[др]\d*|[ёа-я]+[0-9]+'
# Pattern for command with forced code
FORCED_CODE_PATTERN = r'^/ '
# Pattern for Level Scheme link parsing
SCHEMA_LINK_PATTERN = r'<a href=\"\.\.\/\.\.\/(uploaded.*?)\".*?[с|С][х|Х][е|Е][м|М][а|А].*?<\/a>'

################################################################################
# Current block is for direct bot commands patterns
################################################################################
