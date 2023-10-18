from enum import Enum
import re
from core import INSTRUCTION_SET, evaluateOP


def iota (reset: bool= False) -> int:
    """Defines constants"""
    if reset:
        iota.counter = -1
    iota.counter += 1
    return iota.counter
iota.counter = -1


class TokenType (Enum):
    NUMBER = iota(True) # Any number
    OP     = iota() # Any operation of the allowed operations (+, -, *..)
    EOL    = iota() # End of a line (Could also be EOF)
    # OPEN_PAREN = iota()
    # CLOSE_PAREN = iota()

class Token ():
    def __init__(self, tokenType: TokenType, lexeme: str | float, filePath: str, line_index: int, char_index: int) -> None:
        self.type = tokenType
        self.lexeme = lexeme
        self.file = filePath
        self.line = line_index +1
        self.char = char_index +1
    
    def __repr__(self) -> str:
        return '{' +f"{self.type}:{self.lexeme}" +'}'


def parseSourceFile (content: str, filePath: str) -> list[Token]:
    '''Takes a source file and parses its content to tokens
    Does not check for structure validity,
    only checks for syntax correctness'''
    
    NUMBER_PERIOD = '.'
    tokens = []
    
    for line_index, line in enumerate(content.splitlines()):
        i = 0
        while i < len(line):
            char = line[i]
            
            if char in INSTRUCTION_SET:
                tokens.append(Token(TokenType.OP, char, filePath, line_index, i))
                i += 1
            
            elif char.isdigit():
                number = char
                j = i +1
                while j < len(line) and (line[j].isdigit() or line[j] == NUMBER_PERIOD):
                    number += line[j]
                    j += 1
                try:
                    number = float(number)
                except ValueError:
                    raise Exception(f"PARSING ERROR: Couldn't parse this number: `{number}`\nFile {filePath}:{line_index +1}:{i +1}")
                tokens.append(Token(TokenType.NUMBER, number, filePath, line_index, i))
                i = j
            
            elif char.isspace():
                i += 1
            
            else:
                raise Exception(f"PARSING ERROR: Unexpected char: `{char}`\nFile {filePath}:{line_index +1}:{i +1}")
        
        tokens.append(Token(TokenType.EOL, None, filePath, line_index, len(line)))
    
    return tokens

def lex (content: str, filePath: str) -> any:
    
    pass

def runSourceFile (filePath: str) -> None:
    '''Compiles and runs a source file'''
    content = None
    with open(filePath, 'r') as f:
        content = f.read()
    print(parseSourceFile(content, filePath))
    pass