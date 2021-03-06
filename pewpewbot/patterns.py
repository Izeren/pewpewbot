
# File with standard patterns for parsing telegram chat messages

# Default pattern for parsing coordinates from telegram chat
STANDARD_COORDS_PATTERN = r'(\d{2}[\.,]\d{3,})'
# Default pattern for parsing standard dozor code from telegram chat
STANDARD_CODE_PATTERN = r'\d*[dr]\d*[dr]\d*'
# Pattern for command with forced code
FORCED_CODE_PATTERN = r'^/ '
# Pattern for Level Scheme link parsing
SCHEMA_LINK_PATTERN = r'<a href=\"\.\.\/\.\.\/(uploaded.*?)\".*?[с|С][х|Х][е|Е][м|М][а|А].*?<\/a>'

################################################################################
# Current block is for direct bot commands patterns
################################################################################
