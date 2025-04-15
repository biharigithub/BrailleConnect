# Braille Conversion Utility

# Mapping of English characters to Braille Unicode characters
CHAR_TO_BRAILLE = {
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑',
    'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
    'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
    'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
    'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽',
    'z': '⠵', ' ': '⠀',
    '1': '⠼⠁', '2': '⠼⠃', '3': '⠼⠉', '4': '⠼⠙', '5': '⠼⠑',
    '6': '⠼⠋', '7': '⠼⠛', '8': '⠼⠓', '9': '⠼⠊', '0': '⠼⠚',
    '.': '⠲', ',': '⠂', ';': '⠆', ':': '⠒', '?': '⠦',
    '!': '⠖', '"': '⠦', '\'': '⠄', '(': '⠐⠣', ')': '⠐⠜',
    '-': '⠤', '@': '⠈⠁'
}

# Mapping of Braille Unicode characters to English characters
BRAILLE_TO_CHAR = {v: k for k, v in CHAR_TO_BRAILLE.items()}

def text_to_braille(text):
    """
    Convert English text to Braille characters.
    
    Args:
        text (str): The English text to convert
        
    Returns:
        str: The Braille representation of the text
    """
    result = ""
    
    for char in text.lower():
        braille_char = CHAR_TO_BRAILLE.get(char, char)
        result += braille_char
    
    return result

def braille_to_text(braille):
    """
    Convert Braille characters to English text.
    
    Args:
        braille (str): The Braille text to convert
        
    Returns:
        str: The English representation of the Braille
    """
    result = ""
    i = 0
    
    while i < len(braille):
        # Check for number sign (⠼)
        if braille[i:i+2] == '⠼' and i+1 < len(braille):
            i += 1
            if i < len(braille) and braille[i] in BRAILLE_TO_CHAR:
                result += BRAILLE_TO_CHAR.get(braille[i], braille[i])
        else:
            if braille[i] in BRAILLE_TO_CHAR:
                result += BRAILLE_TO_CHAR.get(braille[i], braille[i])
            else:
                result += braille[i]
        i += 1
    
    return result

def get_detailed_braille_mapping(text):
    """
    Get a detailed mapping of each character to its Braille representation.
    
    Args:
        text (str): The English text to convert
        
    Returns:
        list: A list of dictionaries with 'original' and 'braille' keys
    """
    mapping = []
    
    for char in text.lower():
        if char == ' ':
            mapping.append({
                'original': 'space',
                'braille': '⠀'  # Braille space
            })
        else:
            braille_char = CHAR_TO_BRAILLE.get(char, char)
            mapping.append({
                'original': char,
                'braille': braille_char
            })
    
    return mapping
