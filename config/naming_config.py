"""Configuration for filename generation and naming patterns.

This module centralizes all configuration related to how filenames are generated
from CSV data. The IGNORED_CHARACTERS_FOR_NAMING variable controls which characters
are removed from values before they are used in filename construction.
"""

# Characters to ignore/remove when generating filenames from CSV values
# These characters will be stripped from values BEFORE filename sanitization
# 
# Modify this list to change which characters are cleaned during naming.
# The system will automatically adapt without code changes.
#
# Example:
#   - Input value: "[[Minor]]"
#   - Ignored characters: ['[', ']']
#   - After cleaning: "Minor"
#
IGNORED_CHARACTERS_FOR_NAMING = [
    '[',   # Left square bracket
    ']',   # Right square bracket
]
