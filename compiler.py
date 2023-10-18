from enum import Enum
import re
import core
iota = core.iota

class TokenType (Enum):
    NUMBER = iota(True) # Any number
    OP     = iota() # Any operation of the allowed operations (+, -, *, sqrt, ln, cos..)
    EOL    = iota() # End of a line
    EOF    = iota() # End of the file
    # OPEN_PAREN = iota()
    # CLOSE_PAREN = iota()

class Token ():
    pass

def parseSourceFile (content: str, filePath: str) -> list[Token]:
    '''Takes a source file and parses its content to tokens
    Does not check for structure validity,
    only checks for syntax correctness'''
    
    # i want line / char error handling

    def replace (sep: str, tokenType: TokenType, content: list[str] | list[str | Token]) -> list[str | Token] | list[Token]:
        '''Iterates over the content and looks at every str element of it
        and replaces
        every occurrence of sep in that str element with a new Token of tokenType'''
        
        previousWasStr = False
        _ = []
        for section in content:
            if type(section) == str:
                assert not previousWasStr, f"Two consecutive Strings while tokenizing\nSection: {section}\nContent: {content}"
                previousWasStr = True
                section = section.split(sep)
                for index, part in enumerate(section):
                    if index != 0:
                        _.append(Token(tokenType, None))
                    _.append(part)
            else:
                previousWasStr = False
                _.append(section)
        content = _
        return content

    # Parse tokens that are not affected by whitespace or other characters like +, -..

    pass

def lex (content: str, filePath: str) -> any:
    
    pass

def runSourceFile (filePath: str) -> None:
    '''Compiles and runs a source file'''
    content = None
    with open(filePath, 'r') as f:
        content = f.read()
    pass