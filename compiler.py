from __future__ import annotations

if __name__ == '__main__':
    raise Exception('The compiler should not be run directly')

import os
from core import OP_SET, Instruction
from typing import Type
from enum import Enum, auto
from numbers import Number


class Token ():
    class Type (Enum):
        '''Token types'''
        NUMBER        = auto() # Any number
        OP            = auto() # Any operation of the allowed operations from the set of instruction (+, -, *..)
        EOL           = auto() # End of a line
        OPEN_PAREN    = auto() # Opening parenthesis `(`
        CLOSE_PAREN   = auto() # Closing parenthesis `)`
        IDENTIFIER    = auto() # Any identifier; variable, function name ext.. Can only have letters, `_` and numbers but can only start with the first two; _fOo10
        ASSIGN_OP     = auto() # The assigning operation, `=`
        DEF_KW        = auto() # The `def` keyword to declare functions
        OPEN_CURLY    = auto() # Opening curly brackets `{`
        CLOSE_CURLY   = auto() # Closing curly brackets `}`
        COMMA         = auto() # The `,` that separates the params, args or list elements
        SEMICOLON     = auto() # `;` to end expressions (not required)
        BOC           = auto() # Beginning of Content (It's Content and not File because the include keyword basically just copies and pastes the content of the included file in the one including it, and so its not a single file being parsed rather some content)
        EOC           = auto() # End of Content # This one is not used really
        EXT_KW        = auto() # The `ext` keyword to assign to external variables, the one in the parent scope recursively
        RET_KW        = auto() # The `ret` keyword to return values
        UNARY_ALS     = auto() # Unary aliases. They start with $
        BINARY_ALS    = auto() # Binary aliases. They start with @
        OPEN_BRACKET  = auto() # Opening bracket `[`
        CLOSE_BRACKET = auto() # Closing bracket `]`
        
        @property
        def lexeme (self) -> str:
            '''Returns the lexeme for Token.Types that have a fixed lexeme'''
            if self == Token.Type.EOL:
                return '\n' # Fuck Windows' new lines
            elif self == Token.Type.OPEN_PAREN:
                return '('
            elif self == Token.Type.CLOSE_PAREN:
                return ')'
            elif self == Token.Type.ASSIGN_OP:
                return '='
            elif self == Token.Type.DEF_KW:
                return 'def'
            elif self == Token.Type.OPEN_CURLY:
                return '{'
            elif self == Token.Type.CLOSE_CURLY:
                return '}'
            elif self == Token.Type.COMMA:
                return ','
            elif self == Token.Type.SEMICOLON:
                return ';'
            elif self == Token.Type.EXT_KW:
                return 'ext'
            elif self == Token.Type.RET_KW:
                return 'ret'
            elif self == Token.Type.OPEN_BRACKET:
                return '['
            elif self == Token.Type.CLOSE_BRACKET:
                return ']'
            else:
                assert False, f"Tried getting the lexeme of a Token.Type that isn't fixed"
    
    def __init__(self, tokenType: Token.Type, lexeme: str | Number, line: str, span: int, file_path: str, line_index: int, char_index: int, synthesized: bool=False) -> None:
        '''`line`: the actual line, the string in which this Token exists\n
        `span`: the length of the Token in the line\n
        `synthesized`: refers to whether the token was created by the compiler
        '''
        self.type = tokenType
        self.lexeme = lexeme
        self.line = line
        self.span = span
        self.file = file_path
        self.line_number = line_index +1
        self.char_number = char_index +1
        self.synthesized = synthesized
    
    def location(self) -> str:
        return f"File `{self.file}`, line: {self.line_number}, column: {self.char_number}"
    
    def pointOut(self) -> str:
        return f"{self.line[:self.char_number -1]}>>>{self.line[self.char_number -1 : self.char_number -1 +self.span]}<<<{self.line[self.char_number -1 +self.span:]}"
    
    def getSynthesizedInfo(self) -> tuple:
        '''Returns the info to be passed
        to the constructor for Tokens
        that are synthesized because of
        this `self` token'''
        return (self.line, 0, self.file, self.line_number -1, self.char_number -1, True)
    
    def isValueToken (self) -> bool:
        '''Whether this Token is a value element token or not'''
        return self.type in [Token.Type.IDENTIFIER, Token.Type.NUMBER]
    
    def __eq__(self, other: object) -> bool:
        '''Two Tokens are equal if they are of the same `type` and
        have the same `lexeme`. Location is ignored'''
        if isinstance(other, self.__class__):
            return self.type == other.type and self.lexeme == other.lexeme
        else:
            return False
    
    def __hash__(self) -> int:
        '''Hash based on the `type` and the `lexeme`'''
        return hash((self.type, self.lexeme))
    
    def __str__(self) -> str:
        return self.line[self.char_number -1 : self.char_number -1 +self.span]
    
    def __repr__(self) -> str:
        return str(self.lexeme)

def parseSourceFile (file_path: str) -> list[Token]:
    '''Takes a source file and parses its content to tokens
    Does not check for structure validity,
    only checks for content correctness\n
    Also handles includes'''
    
    def parsingError (message: str, temp_token: Token) -> None:
        '''Raises a parsing error exception'''
        assert type(temp_token) == Token, f"Not a Token"
        message = "❌ PARSING ERROR: " +message +f"\n{temp_token.pointOut()}\n{temp_token.location()}"
        raise Exception(message)
    
    def resolveFile (file_path: str, main_file_path: str) -> tuple[str, str] | None:
        '''Given a files' relative path, it would return its
        content and its absolute path, or None if it was not found.\n
        First tries to find it relative to the `main_file_path`. If
        it fails looks for it in the libraries dir next to the compiler.
        If it failed still and the file path does not end with
        the Malang file extension, it adds it and tries again.'''
        
        def safeRead (file_path: str) -> str | None:
            '''Reads content the file if it exists,
            or `None` if it doesn't'''
            try:
                with open(file_path, 'r') as f:
                    return f.read()
            # except FileNotFoundError: # Any error instead
            except Exception:
                return None
        
        FILE_EXT = '.mlg'
        STD_LIBS_DIR = 'std_libs'
        original_file_path = file_path
        
        while True:
            main_file_dir = os.path.dirname(main_file_path) # Check relative to the main file first
            file_path = os.path.join(main_file_dir, original_file_path)
            content = safeRead(file_path)
            if content is None: # Otherwise check in the libs dir
                file_path = os.path.join(STD_LIBS_DIR, original_file_path)
                content = safeRead(file_path)
            
            if content is not None:
                return (content, os.path.abspath(file_path))
            elif not original_file_path.endswith(FILE_EXT):
                original_file_path += FILE_EXT
            else:
                return None
    
    def parse (content: str, file_path: str, main: bool, main_file_path: str, includes: set[str]) -> list[Token]:
        '''The functions that actually parses the file\n
        `content`: content to parse\n
        `file_path`: the file path of this content. To
        be able to create tokens\n
        `main`: specifies whether this is the main file being
        parsed to know whether or not to include the BOC and EOC
        tokens\n
        `main_file_path`: the main file path, in order
        to resolve includes\n
        `includes`: a set containing all the absolute path
        of all the included files so far'''
        
        def readString (line: str, starter_index: int, file_path: str, line_index: int) -> tuple[str, int]:
            '''Reads the String that starts from `start_index`
            and continues until it ends (if it started with `'` then
            until the next `'`, same for `"`) while taking into
            consideration escape characters, and returns
            it (without the quotes) along side
            where to continue which is where it ends +1\n
            `file_path` and `line_index` are there just in case
            we need to raise a parsingError exception'''
            i = starter_index # For ease of reference
            starter = line[i]
            assert starter in ['"', "'"], f"Unknown starter {starter}"
            
            ESCAPE_DICT = {
                'n': '\n',
                't': '\t',
                'r': '\r',
                'b': '\b',
                'a': '\a',
                '0': '\0',
                '\\': '\\',
                '"': '"',
                "'": "'"
            }
            
            string = ''
            i += 1
            while i < len(line):
                char = line[i]
                
                if char == starter:
                    return string, i +1
                
                elif char == '\\':
                    if len(line) <= i +1:
                        temp_token = Token(None, char, line, 1, file_path, line_index, i)
                        parsingError(f"Invalid escape character. There should be something after `\`", temp_token)
                    if line[i +1] not in ESCAPE_DICT:
                        temp_token = Token(None, line[i:i +2], line, 2, file_path, line_index, i)
                        parsingError(f"Unknown escape character", temp_token)
                    string += ESCAPE_DICT[line[i +1]]
                    i += 2
                
                else:
                    string += char
                    i += 1
            
            temp_token = Token(None, starter, line, 1, file_path, line_index, starter_index)
            message = "Unterminated string literal" if starter == '"' else "Unterminated character literal"
            parsingError(message, temp_token)
        
        NUMBER_PERIOD = '.' # 3.14
        NUMBER_SEP    = '_' # 100_00
        
        content = content.splitlines() # Returns an empty list in case of empty content
        tokens = []
        
        if main:
            line = '' if len(content) == 0 else content[0]
            tokens.append(Token(Token.Type.BOC, None, line, 0, file_path, 0, 0))
        
        for line_index, line in enumerate(content):
            i = 0
            while i < len(line):
                char = line[i]
                
                if char.isdigit() or (char == '-' and i +1 < len(line) and line[i +1].isdigit()): # Handles negative numbers too
                    number = char
                    j = i +1
                    while j < len(line) and (line[j].isdigit() or line[j] == NUMBER_PERIOD or line[j] == NUMBER_SEP):
                        number += line[j]
                        j += 1
                    try:
                        original = number
                        number = float(original) # If it passes this part then it's a number
                        try:
                            number = int(original) # Just check if it's an int (Casting won't work as that floats are limited) 
                        except ValueError:
                            pass
                    except ValueError:
                        temp_token = Token(None, number, line, j -i, file_path, line_index, i)
                        parsingError(f"Couldn't parse this number: `{number}`", temp_token)
                    tokens.append(Token(Token.Type.NUMBER, number, line, j -i, file_path, line_index, i))
                    i = j
                
                elif char in OP_SET.getSymbols(): # Should be after number to handle negative numbers
                    if char == OP_SET.IDIV.symbol[0] and i +1 < len(line) and line[i +1] == OP_SET.IDIV.symbol[1]: # Handles `//`
                        char = line[i : i +2]
                    tokens.append(Token(Token.Type.OP, char, line, len(char), file_path, line_index, i))
                    i += len(char)
                
                elif char == Token.Type.OPEN_PAREN.lexeme:
                    tokens.append(Token(Token.Type.OPEN_PAREN, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char == Token.Type.CLOSE_PAREN.lexeme:
                    tokens.append(Token(Token.Type.CLOSE_PAREN, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char == '_' or char.isalpha(): # An identifier, a keyword or include
                    identifier = char
                    j = i +1
                    while j < len(line) and (line[j].isalpha() or line[j].isdigit() or line[j] == '_'):
                        identifier += line[j]
                        j += 1
                    
                    tokenType = None
                    if identifier == Token.Type.DEF_KW.lexeme:
                        tokenType = Token.Type.DEF_KW
                    
                    elif identifier == Token.Type.EXT_KW.lexeme:
                        tokenType = Token.Type.EXT_KW
                    
                    elif identifier == Token.Type.RET_KW.lexeme:
                        tokenType = Token.Type.RET_KW
                    
                    elif identifier == 'include':
                        included_file_path = line[j +1:]
                        result = resolveFile(included_file_path, main_file_path)
                        if result is None:
                            temp_token = Token(None, line[i :], line, len(line) -i, file_path, line_index, i)
                            raise Exception(f"❌ NO SUCH FILE: Couldn't locate this file `{included_file_path}` that you wanted to include\n{temp_token.pointOut()}\n{temp_token.location()}")
                        included_file_content, included_file_abs_path = result
                        if included_file_abs_path not in includes:
                            includes.add(included_file_abs_path)
                            tokens.extend(parse(included_file_content, included_file_path, False, main_file_path, includes))
                        break
                    
                    else:
                        tokenType = Token.Type.IDENTIFIER
                    
                    tokens.append(Token(tokenType, identifier, line, j -i, file_path, line_index, i))
                    i = j
                
                elif char == Token.Type.OPEN_CURLY.lexeme:
                    tokens.append(Token(Token.Type.OPEN_CURLY, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char == Token.Type.CLOSE_CURLY.lexeme:
                    tokens.append(Token(Token.Type.CLOSE_CURLY, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char == Token.Type.ASSIGN_OP.lexeme:
                    tokens.append(Token(Token.Type.ASSIGN_OP, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char == Token.Type.COMMA.lexeme:
                    tokens.append(Token(Token.Type.COMMA, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char == Token.Type.SEMICOLON.lexeme:
                    tokens.append(Token(Token.Type.SEMICOLON, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char in ['$', '@']:
                    alias = ''
                    j = i +1
                    while j < len(line) and not line[j].isspace():
                        alias += line[j]
                        j += 1
                    tokenType = Token.Type.UNARY_ALS if char == '$' else Token.Type.BINARY_ALS
                    tokens.append(Token(tokenType, alias, line, j -i, file_path, line_index, i))
                    i = j
                
                elif char == Token.Type.OPEN_BRACKET.lexeme:
                    tokens.append(Token(Token.Type.OPEN_BRACKET, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char == Token.Type.CLOSE_BRACKET.lexeme:
                    tokens.append(Token(Token.Type.CLOSE_BRACKET, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char == '"':
                    string, j = readString(line, i, file_path, line_index)
                    tokens.append(Token(Token.Type.OPEN_BRACKET, Token.Type.OPEN_BRACKET.lexeme, line, 1, file_path, line_index, i, True))
                    for ci, c in enumerate(string):
                        tokens.append(Token(Token.Type.NUMBER, ord(c), line, 1, file_path, line_index, i +ci +1, True))
                        tokens.append(Token(Token.Type.COMMA, Token.Type.COMMA.lexeme, line, 1, file_path, line_index, i +ci +1, True))
                    tokens.append(Token(Token.Type.CLOSE_BRACKET, Token.Type.CLOSE_BRACKET.lexeme, line, 1, file_path, line_index, j -1, True))
                    i = j
                
                elif char == "'":
                    string, j = readString(line, i, file_path, line_index)
                    if len(string) != 1:
                        temp_token = Token(None, string, line, j -i, file_path, line_index, i)
                        parsingError(f"Single quotations must contain one single character", temp_token)
                    tokens.append(Token(Token.Type.NUMBER, ord(string), line, j -i, file_path, line_index, i))
                    i = j
                
                elif char == '#':
                    # A line comment, go to the next line
                    break
                
                elif char.isspace():
                    i += 1
                
                else:
                    temp_token = Token(None, char, line, len(char), file_path, line_index, i)
                    parsingError(f"Unexpected char: `{char}`", temp_token)
            
            tokens.append(Token(Token.Type.EOL, Token.Type.EOL.lexeme, line, 1, file_path, line_index, len(line)))
        
        if main:
            line = '' if len(content) == 0 else content[-1]
            tokens.append(Token(Token.Type.EOC, None, line, 0, file_path, len(content), len(line)))
        
        return tokens
    
    result = resolveFile(file_path, file_path)
    if result is None:
        raise Exception(f"❌ FILE DOES NOT EXISTS: `{file_path}`")
    content, abs_path = result
    includes = {abs_path}
    return parse(content, file_path, True, file_path, includes)


class Node():
    class Type (Enum):
        '''Node types'''
        ROOT        = auto() # Root node of the content. Will only contain instruction nodes. Only 1 exists.
        VAR_ASSIGN  = auto() # Assigning to a variable
        OP          = auto() # Any operation of the allowed operations from the set of instruction (+, -, *..)
        ORDER_PAREN = auto() # Order parenthesis. They can only contain a value element
        FUNC_DEF    = auto() # Function definition. Can have nested functions. Functions overloading is allowed
        FUNC_CALL   = auto() # Function call
        ANON_FUNC   = auto() # Anonymous function
        RETURN      = auto() # Return to return from scopes, either a value in front of it or the return variable
    
    def __init__(self, nodeType: Node.Type, **components) -> None:
        ''' The components that each nodeType has:\n
        - `ROOT`:
            - `boc`: the beginning of content Token
            - `content`: a list of the instruction nodes
            - `eoc`: the end of content Token
        - `VAR_ASSIGN`:
            - `var`: an identifier token representing the variable getting assigned to
            - `ext`: a boolean stating whether this variable is a local or external one
            - `value`: a value element representing the assigned value
        - `OP`:
            - `op`: the op token representing the operation being performed
            - `l_value`: a value element representing the left value of the operation
            - `r_value`: a value element representing the right value of the operation
        - `ORDER_PAREN`:
            - `value`: a value element representing their content
        - `FUNC_DEF`:
            - `func`: an identifier token representing the function being defined
            - `has_als`: a boolean indicating whether this function has an alias
            - `als`: a Token.UNARY_ALS or Token.BINARY_ALS depending on the
            number of `params` that represents the alias of this function. Exists
            if and only if `has_als` is `True`
            - `params`: a list of identifier tokens representing the parameters
            - `body`: a list of nodes (another AST, but without the root node) 
            representing the body of the function. It
            can contain any other node, including another Node.FUNC_DEF
        - `FUNC_CALL`:
            - `with_als`: a boolean indicating whether this function call is done
            trough an alias or trough an identifier
            - `func`: an identifier token representing the function being called, exists
            if and only if `with_als` is `False`
            - `als`: a Token.UNARY_ALS or Token.BINARY_ALS representing the alias
            that this function is referring to with this call, exists if and
            only if `with_als` is `True`
            - `args`: a list of value elements representing the arguments
        - `ANON_FUNC`:
            - `starter`: an open curly bracket representing the start of the anonymous function
            - `body`: a list of nodes (another AST, but without the root node) 
            representing the body of the anonymous function. It
            can contain any other node, including another Node.ANON_FUNC
        - `RETURN`:
            - `has_value`: a boolean indicating whether this return has a value that
            it should return or if it should return the return variable
            - `value`: a value element that would be returned, if and only if `has_value`
            is `True`
        '''
        self.type = nodeType
        self.components = components
    
    def isValueNode (self) -> bool:
        '''Whether this Node is a value element node or not'''
        return self.type in [Node.Type.OP, Node.Type.ORDER_PAREN, Node.Type.FUNC_CALL, Node.Type.ANON_FUNC]
    
    def isInstructionNode (self) -> bool:
        '''Whether this Node is an instruction node or not\n
        Instruction nodes are the only Nodes that can start new instructions'''
        if self.type == Node.Type.FUNC_CALL:
            return self.components['with_als'] == False
        return self.type in [Node.Type.VAR_ASSIGN, Node.Type.FUNC_DEF, Node.Type.ANON_FUNC, Node.Type.RETURN]
    
    def __repr__(self) -> str:
        return f"{self.type}\n\t=> {self.components}"

def isValueElement (element: Token | Node) -> bool:
    '''Checks if the element is a value element\n
    A value element means a Token or a Node that can return
    or is a value.'''
    
    if type(element) == Token:
        return element.isValueToken()
    elif type(element) == Node:
        return element.isValueNode()
    else:
        assert False, f"Passed something other than Token or Node, {element}"

def constructAST (tokens: list[Token]) -> Node:
    '''Takes tokens and returns a root node\n
    Does not check for the validity of the
    code  like referencing a none existing variable or function,
    only checks the validity of the structure / syntax'''
    
    def syntaxError (message: str, token: Token) -> None:
        '''Raises a syntax error exception'''
        assert type(token) == Token, f"Not a Token"
        message = "❌ SYNTAX ERROR: " +message +f"\n{token.pointOut()}\n{token.location()}"
        raise Exception(message)
    
    def findEnclosingToken (tokens: list[Token], opening_tokenType: Token.Type, enclosing_tokenType: Token.Type, search_from: int, required: Token | None) -> int | None:
        '''Returns the index of the enclosing token starting from `search_from`.
        This handles nested tokens such as ((())) for example\n
        `tokens`: normally, a list of all the tokens\n
        `required`: should have the opening token, the
        one whose enclosing token you want to find,
        if you want this function to raise a SyntaxError if 
        its closing token was not found. Or `None` if you
        don't care if it's not found'''
        
        depth = 1
        while search_from < len(tokens):
            tokenType = tokens[search_from].type
            if tokenType == opening_tokenType:
                depth += 1
            elif tokenType == enclosing_tokenType:
                depth -= 1
                if depth == 0:
                    return search_from
            search_from += 1
        if required is not None:
            syntaxError(f"The enclosing element for this one is missing.", required)
        return None
    
    def isNextToken (tokens: list[Token], tokenType: Token.Type, start_from: int, required: tuple[str, Token] | None) -> int | None:
        '''Checks if the next token, from `start_from`, is `tokenType`, while skipping over
        Token.EOLs. If it is return its index, otherwise `None`\n
        `required`: if it's required that the next token be `tokenType`
        then this should be a tuple containing a message as well
        as a token to raise a SyntaxError exception with. If it's
        not required then give it `None`'''
        
        while start_from < len(tokens):
            if tokens[start_from].type == tokenType:
                return start_from
            elif tokens[start_from].type == Token.Type.EOL:
                start_from += 1
            else:
                break
        if required is not None:
            syntaxError(*required)
        else:
            return None
    
    def processValueExpression (tokens: list[Token], parent_token: Token, start_index: int, skip_eols: bool, accepts_semicolons: bool, accepts_comas: bool) -> tuple[Node | Token, int]:
        '''Processes a value expression and return a value element
        representing it as well as from where to continue\n
        Whether a value expression can have certain
        terminators vary, so
        the parameters specify how to handle it\n
        `tokens`: normally, the list of all the tokens\n
        `parent_token`: the token that "wants" this value expression. To raise a SyntaxError with in case of an error\n
        `start_index`: from where to start processing\n
        `skip_eols`: skip EOLs or terminate when encountered\n
        `accepts_semicolons`: can a semicolon be in this value expression?\n
        `accepts_comas`: can a coma be in this value expression?\n'''
        
        def nextSingletonValue (tokens: list[Token], parent_token: Token, start_index: int, skip_eols: bool) -> tuple[Node | Token, int]:
            '''Returns the immediate next singleton
            value starting from `start_index` along side the index
            on which to continue.\n
            Check the function below to see what a singleton value is
            `tokens`: normally, a list of all the tokens\n
            `parent_token`: the token that "wants" this singleton value. To raise a SyntaxError with in case of an error\n
            `start_index`: from where to start\n
            `skip_eols`: whether to skip EOLs until you find a value or not, meaning one should be
            the immediate next'''
            
            def isSingletonValue (value: Node | Token) -> bool:
                '''A singleton value is a value element that exists on it's own. The
                only value elements that are an exception to this are Node.OP and 
                Node.FUNC_CALL['als'] == Token.BINARY_ALS, as they require
                two value elements, one before and one after\n'''
                opNode = type(value) == Node and value.type == Node.Type.OP
                binaryFuncCall = type(value) == Node and value.type == Node.Type.FUNC_CALL and value.components['with_als'] and value.components['als'] == Token.Type.BINARY_ALS
                return isValueElement(value) and not opNode and not binaryFuncCall
            
            i = start_index # Just for ease of reference
            
            if skip_eols:
                while i < len(tokens) and tokens[i].type == Token.Type.EOL:
                    i += 1
            
            singleton_value_element = None
            if i < len(tokens):
                token = tokens[i]
                tokenType = token.type
                
                if tokenType == Token.Type.NUMBER: # Token.NUMBER
                    singleton_value_element = token
                    i += 1
                
                elif tokenType == Token.Type.IDENTIFIER: # A variable or a Node.FUNC_CALL['with_als'] == False
                    if i +1 < len(tokens) and tokens[i +1].type == Token.Type.OPEN_PAREN: # Node.FUNC_CALL['with_als'] == False
                        singleton_value_element, i = processFuncCall(tokens, token, i +1)
                    
                    else: # A variable
                        singleton_value_element = token
                        i += 1
                
                elif tokenType == Token.Type.OPEN_PAREN: # Node.ORDER_PAREN
                    close_paren = findEnclosingToken(tokens, Token.Type.OPEN_PAREN, Token.Type.CLOSE_PAREN, i +1, token)
                    value, _ = processValueExpression(tokens[i +1 : close_paren], token, 0, True, False, False)
                    singleton_value_element = Node(Node.Type.ORDER_PAREN, value=value)
                    i = close_paren +1
                
                elif tokenType == Token.Type.OPEN_CURLY: # Node.ANON_FUNC
                    singleton_value_element, i = processAnonFunc(tokens, i)
                
                elif tokenType == Token.Type.UNARY_ALS: # Node.FUNC_CALL['als'] == Token.UNARY_ALS
                    single_arg, i = nextSingletonValue(tokens, token, i +1, False)
                    singleton_value_element = Node(Node.Type.FUNC_CALL, with_als=True, als=token, args=[single_arg])
                
                else:
                    syntaxError(f"A value is required after this `{parent_token}`, found this instead `{token}`", token)
            else:
                syntaxError(f"Expected some value after this `{parent_token}`", parent_token)
            
            assert isSingletonValue(singleton_value_element), f"UNREACHABLE" # OCD be OCDing
            return (singleton_value_element, i)
        
        def appendOP (root_op_node: Node, op: Token, r_value: Token | Node) -> Node:
            '''Adds the `op` to the tree of ops according to the precedence of its content
            and returns the new root node of the ops' tree\n
            The process of appending goes as follows:\n
            \tIf the `root_op_node`'s precedence is greater than or equal to `op` => It is `op`'s l_value\n
            \tOtherwise => The `op` is the `root_op_node` new r_value, and its old r_value is the `op`'s l_value (treating
            the r_value in a recursive fashion)\n
            '''
            assert root_op_node.type == Node.Type.OP, f"The root_node is not a Node.OP"
            assert op.type == Token.Type.OP, f"The op is not an op token"
            assert isValueElement(r_value), f"Passed an r_value that does not produce value"
            
            if OP_SET.fromSymbol(root_op_node.components['op'].lexeme).precedence >= OP_SET.fromSymbol(op.lexeme).precedence:
                return Node(Node.Type.OP, op=op, l_value=root_op_node, r_value=r_value)
            else:
                root_op_r_value = root_op_node.components['r_value']
                root_op_new_r_value = None
                if type(root_op_r_value) == Node and root_op_r_value.type == Node.Type.OP:
                    root_op_new_r_value = appendOP(root_op_r_value, op, r_value)
                else:
                    root_op_new_r_value = Node(Node.Type.OP, op=op, l_value=root_op_r_value, r_value=r_value)
                root_op_node.components['r_value'] = root_op_new_r_value
                return root_op_node
        
        i = start_index # Just for ease of reference
        buffer, i = nextSingletonValue(tokens, parent_token, i, skip_eols)
        
        while i < len(tokens): # Node.OP or Node.FUNC_CALL['als'] == Token.BINARY_ALS
            token = tokens[i]
            tokenType = token.type
            
            if tokenType == Token.Type.OP: # Node.OP
                l_value = buffer
                r_value, i = nextSingletonValue(tokens, token, i +1, False)
                if type(l_value) == Node and l_value.type == Node.Type.OP: # If an op is the previous value then append
                    buffer = appendOP(l_value, token, r_value)
                else: # Otherwise create one
                    buffer = Node(Node.Type.OP, op=token, l_value=l_value, r_value=r_value)
            
            elif tokenType == Token.Type.BINARY_ALS: # Node.FUNC_CALL['als'] == Token.BINARY_ALS
                first_arg = buffer
                second_arg, i = nextSingletonValue(tokens, token, i +1, False)
                buffer = Node(Node.Type.FUNC_CALL, with_als=True, als=token, args=[first_arg, second_arg])
            
            elif tokenType == Token.Type.EOL:
                if skip_eols:
                    i += 1
                else:
                    break
            
            elif tokenType == Token.Type.COMMA:
                if accepts_comas:
                    break
                else:
                    syntaxError(f"Commas can't be here", token)
            
            elif tokenType == Token.Type.SEMICOLON:
                if accepts_semicolons:
                    break
                else:
                    syntaxError(f"Semicolons can't be here", token)
            
            else:
                syntaxError(f"What is this `{token}` doing here? (- In Hector Salamancas' voice). Expected an operation or a binary alias", token)
            
        if not isValueElement(buffer):
            assert False, f"Buffer is not a value element: {buffer}"
        return (buffer, i)
    
    def processFuncCall (tokens: list[Token], func: Token, open_paren_index: int) -> tuple[Node, int]:
        '''Processes a normal function call (no alias) and returns a Node.FUNC_CALL
        and the index at which to continue, which is where the function
        call ends +1\n
        `tokens`: normally, a list of all the tokens\n
        `func`: a Node.IDENTIFIER representing the function being called\n
        `open_paren_index`: where the function call starts'''
        i = open_paren_index # Just for ease of reference
        assert func.type == Token.Type.IDENTIFIER, f"Not Token.IDENTIFIER"
        assert tokens[i].type == Token.Type.OPEN_PAREN, f"Not Token.OPEN_PAREN"
        
        close_paren = findEnclosingToken(tokens, Token.Type.OPEN_PAREN, Token.Type.CLOSE_PAREN, i +1, tokens[i])
        args = []
        if isNextToken(tokens, Token.Type.CLOSE_PAREN, i +1, None) is None: # If it has some args
            args_tokens = tokens[i : close_paren] # Contains the `(`
            inc = 0
            while i +inc < close_paren:
                arg, inc = processValueExpression(args_tokens, args_tokens[inc], inc +1, True, False, True)
                if i +inc < close_paren:
                    assert tokens[i +inc].type == Token.Type.COMMA, f"It should only exit if it encountered a comma. Exited on {tokens[i +inc]}"
                args.append(arg)
        return (Node(Node.Type.FUNC_CALL, with_als=False, func=func, args=args), close_paren +1)
    
    def processAnonFunc (tokens: list[Token], open_curly_index: int) -> tuple[Node, int]:
        '''Processes an anonymous function and returns a Node.ANON_FUNC
        and the index at which to continue, which is where the anonymous
        function ends +1\n
        `tokens`: normally, a list of all the tokens\n
        `open_curly_index`: the anonymous function starter'''
        i = open_curly_index # Just for ease of reference
        assert tokens[i].type == Token.Type.OPEN_CURLY, f"Not Token.OPEN_CURLY"
        
        close_curly = findEnclosingToken(tokens, Token.Type.OPEN_CURLY, Token.Type.CLOSE_CURLY, i +1, tokens[i])
        body = construct(tokens[i +1 : close_curly], False)
        return (Node(Node.Type.ANON_FUNC, starter=tokens[i], body=body), close_curly +1)
    
    def processFuncDef (tokens: list[Token], def_kw_index: int, als: Token | None) -> tuple[Node, int]:
        '''Processes a function definition and returns a Node.FUNC_DEF
        and the index at which to continue, which where the function definition
        ends +1\n
        `als`: if this function definition is preceded by an alias then
        this should be a Token.UNARY_ALS or Token.BINARY_ALS, if not
        then it should be `None`'''
        i = def_kw_index # Just for ease of reference
        assert tokens[i].type == Token.Type.DEF_KW, f"Not Token.DEF_KW"
        assert als == None or als.type == Token.Type.UNARY_ALS or als.type == Token.Type.BINARY_ALS, f"Wrong argument {als}"
        
        i += 1
        if len(tokens) <= i or tokens[i].type != Token.Type.IDENTIFIER:
            syntaxError(f"There should be an identifier representing the name of the function being defined right after the `{tokens[i -1]}` keyword", {tokens[i -1]})
        func = tokens[i]
        i += 1
        if len(tokens) <= i or tokens[i].type != Token.Type.OPEN_PAREN:
            syntaxError(f"There should be an open parenthesis right after the function's name to define this function's parameters", tokens[i -1])
        i += 1
        close_paren = findEnclosingToken(tokens, Token.Type.OPEN_PAREN, Token.Type.CLOSE_PAREN, i, tokens[i -1])
        params = []
        last_token_was_comma = True # True just to init
        while i < close_paren:
            if tokens[i].type == Token.Type.EOL:
                i += 1
            elif tokens[i].type == Token.Type.COMMA:
                if last_token_was_comma:
                    message = f"Expected a parameter's name to start with, not a comma" if len(params) == 0 else f"Two consecutive commas. A parameter is missing"
                    syntaxError(message, tokens[i])
                else:
                    last_token_was_comma = True
                    i += 1
            elif tokens[i].type == Token.Type.IDENTIFIER:
                if last_token_was_comma:
                    params.append(tokens[i])
                    last_token_was_comma = False
                    i += 1
                else:
                    syntaxError(f"Two consecutive parameters. A comma is missing", tokens[i])
            else:
                message = f"Expected a parameters' name, not this:" if last_token_was_comma else f"Expected a comma to separate the parameters, not this:"
                syntaxError(message, tokens[i])
        if len(params) != 0 and last_token_was_comma:
            syntaxError(f"There is an extra comma before this closing parenthesis, remove it", tokens[i])
        open_curly = isNextToken(tokens, Token.Type.OPEN_CURLY, i +1, (f"Couldn't find an open curly bracket to start the body of the function after this:", tokens[i]))
        close_curly = findEnclosingToken(tokens, Token.Type.OPEN_CURLY, Token.Type.CLOSE_CURLY, open_curly +1, tokens[open_curly])
        body = construct(tokens[open_curly +1 : close_curly], False)
        func_def = None
        if als == None:
            func_def = Node(Node.Type.FUNC_DEF, func=func, has_als=False, params=params, body=body)
        else:
            if als.type == Token.Type.UNARY_ALS:
                if len(params) != 1:
                    syntaxError(f"This function definition is preceded with an unary alias yet it doesn't have one parameter, instead it has {len(params)} parameters", tokens[def_kw_index])
            elif als.type == Token.Type.BINARY_ALS:
                if len(params) != 2:
                    syntaxError(f"This function definition is preceded with an binary alias yet it doesn't have two parameter, instead it has {len(params)} parameter(s)", tokens[def_kw_index])
            else:
                assert False, f"Unreachable"
            func_def = Node(Node.Type.FUNC_DEF, func=func, has_als=True, als=als, params=params, body=body)
        return (func_def, close_curly +1)
    
    def construct (tokens: list[Token], root: bool) -> Node | list[Node]:
        '''The actual function that constructs
        the AST\n
        `root`: signifies whether this AST that is being constructed
        is the main content AST or not, to know whether to
        return a root node or a list of instruction nodes'''
        
        if root:
            assert tokens[0].type == Token.Type.BOC, f"Not Token.BOC {tokens[0]}"
            assert tokens[-1].type == Token.Type.EOC, f"Not Token.EOC {tokens[-1]}"
            BOC_TOKEN = tokens[0] # Leave them here so that it would raise an undefined error later on if we try to access them when we shouldn't. An assertion
            EOC_TOKEN = tokens[-1]
            tokens = tokens[1 : -1]
        
        content = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            tokenType = token.type
            
            if tokenType == Token.Type.EXT_KW: # EXT Node.VAR_ASSIGN
                i += 1
                if len(tokens) <= i or tokens[i].type != Token.Type.IDENTIFIER:
                    syntaxError(f"Expected a variables' name after the `ext` keyword", token)
                identifier = tokens[i]
                i += 1
                if len(tokens) <= i or tokens[i].type != Token.Type.ASSIGN_OP:
                    syntaxError(f"Expected an `=` after this variable `{token}` to assign a value to it", tokens[i -1])
                value, i = processValueExpression(tokens, tokens[i], i +1, False, True, False)
                content.append(Node(Node.Type.VAR_ASSIGN, var=identifier, ext=True, value=value))
                
            elif tokenType == Token.Type.IDENTIFIER: # LOCAL Node.VAR_ASSIGN or Node.FUNC_CALL
                if len(tokens) <= i +1:
                    syntaxError(f"Expected something after this identifier", token)
                i += 1
                if tokens[i].type == Token.Type.ASSIGN_OP: # Node.VAR_ASSIGN
                    value, i = processValueExpression(tokens, tokens[i], i +1, False, True, False)
                    content.append(Node(Node.Type.VAR_ASSIGN, var=token, ext=False, value=value))
                
                elif tokens[i].type == Token.Type.OPEN_PAREN: # Node.FUNC_CALL
                    func_call, i = processFuncCall(tokens, token, i)
                    content.append(func_call)
                
                else:
                    syntaxError(f"Was not expecting this `{tokens[i]}` after an identifier", tokens[i])
            
            elif tokenType == Token.Type.DEF_KW: # Node.FUNC_DEF['has_als'] == False
                func_def, i = processFuncDef(tokens, i, None)
                content.append(func_def)
            
            elif tokenType in [Token.Type.UNARY_ALS, Token.Type.BINARY_ALS]: # Node.FUNC_DEF['has_als'] == True
                i = isNextToken(tokens, Token.Type.DEF_KW, i +1, (f"A function definition was expected after this alias. Aliases can only be used with function definition when used outside an a value expression", token))
                func_def, i = processFuncDef(tokens, i, token)
                content.append(func_def)
            
            elif tokenType == Token.Type.OPEN_CURLY: # Node.ANON_FUNC
                anon_func, i = processAnonFunc(tokens, i)
                content.append(anon_func)
            
            elif tokenType == Token.Type.RET_KW: # Node.RETURN
                i += 1
                if len(tokens) <= i or tokens[i].type in [Token.Type.EOL, Token.Type.SEMICOLON]: # Node.RETURN['has_value'] == False
                    content.append(Node(Node.Type.RETURN, has_value=False))
                else: # Node.RETURN['has_value'] == True
                    value, i = processValueExpression(tokens, token, i, False, True, False)
                    content.append(Node(Node.Type.RETURN, has_value=True, value=value))
            
            elif tokenType in [Token.Type.EOL, Token.Type.SEMICOLON]: # Skip
                i += 1
            
            elif tokenType in [Token.Type.BOC, Token.Type.EOC]: # Unreachable because they are removed from the list
                assert False, f"Unreachable"
            
            else:
                syntaxError(f"This `{token}` cannot start a new instruction", token)
        
        for node in content:
            assert node.isInstructionNode(), f"Content has something other than an instruction node {node}"
        if root:
            return Node(Node.Type.ROOT, boc=BOC_TOKEN, content=content, eoc=EOC_TOKEN)
        else:
            return content
    
    return construct(tokens, True)


def constructProgram (ast: Node) -> Instruction:
    '''Constructs the program by translating
    Nodes into Instructions (only a single Instruction
    is returned of course)\n
    Also checks for the validity of the code; referencing
    a none existing variable, defining an already existing
    function, recursion and
    cyclic calls'''
    
    RETURN_VAR_NAME = 'res'
    
    def invalidCode (message: str, token: Token) -> None:
        '''Raises an invalid code exception.'''
        assert type(token) == Token, f"Not a Token"
        message = "❌ INVALID CODE: " +message +f"\n{token.pointOut()}\n{token.location()}"
        raise Exception(message)
    
    class Scope:
    
        class FunctionSignature:
            def __init__(self, identifier: Token, als: Token, params_count: int) -> None:
                '''A struct that refers to / identifies a function, either
                from a function call or a function definition\n
                Must have at least the identifier or the als'''
                assert identifier != None or als != None, f"Either the identifier or the als must be given!"
                assert identifier == None or identifier.type == Token.Type.IDENTIFIER, f"Not a Token.IDENTIFIER {identifier}"
                if als is not None:
                    assert als.type in [Token.Type.UNARY_ALS, Token.Type.BINARY_ALS], f"Not a Token.XXX_ALS {als}"
                    if als.type == Token.Type.UNARY_ALS:
                        assert params_count == 1, f"Token.UNARY_ALS with params_count != 1"
                    elif als.type == Token.Type.BINARY_ALS:
                        assert params_count == 2, f"Token.BINARY_ALS with params_count != 2"
                    else:
                        assert False, f"Unreachable, I just checked cases" 
                
                self.identifier = identifier
                self.als = als
                self.params_count = params_count
            
            @classmethod
            def __fromFuncDef (cls, func_def: Node) -> Scope.FunctionSignature:
                '''Creates a FunctionSignature from a Node.FUNC_DEF'''
                assert func_def.type == Node.Type.FUNC_DEF, f"Not a Node.FUNC_DEF {func_def}"
                als = None
                if func_def.components['has_als']:
                    als = func_def.components['als']
                return cls(func_def.components['func'], als, len(func_def.components['params']))
            
            @classmethod
            def __fromFuncCall (cls, func_call: Node) -> Scope.FunctionSignature:
                '''Creates a FunctionSignature from a Node.FUNC_CALL'''
                assert func_call.type == Node.Type.FUNC_CALL, f"Not a Node.FUNC_CALL {func_call}"
                identifier = None
                als = None
                if func_call.components['with_als']:
                    als = func_call.components['als']
                else:
                    identifier = func_call.components['func']
                return cls(identifier, als, len(func_call.components['args']))
            
            def __lookLocally(self, scope: Scope) -> Node | None:
                '''Looks in the local scope for `self`'''
                for func_def in scope.funcs:
                    if self == Scope.FunctionSignature.__fromFuncDef(func_def):
                        return func_def
                return None
            
            def __lookRecursively(self, scope: Scope) -> Node | None:
                '''Looks in the scopes for `self``'''
                while scope is not None:
                    func_def = self.__lookLocally(scope)
                    if func_def is not None:
                        return func_def
                    scope = scope.parent
                return None
            
            @classmethod
            def checkAlreadyDefined (cls, func_def: Node, scope: Scope) -> None:
                '''Checks if a function (in the form of Node.FUNC_DEF)
                is already defined in this scope (local scope only
                of course), if it is, throw an InvalidCode exception'''
                assert func_def.type == Node.Type.FUNC_DEF, f"Not a Node.FUNC_DEF {func_def}"
                exists = cls.__fromFuncDef(func_def).__lookLocally(scope)
                if exists is not None:
                    original = exists.components['func']
                    func = func_def.components['func']
                    invalidCode(f"This function `{func}`:\n{func.pointOut()}\n{func.location()}\nCannot be defined again as it's already defined here in the same scope (similar name and parameter count or similar alias):", original)
            
            @classmethod
            def findFromFuncCall (cls, func_call: Node, scope: Scope) -> Node:
                '''Checks scopes recessively for the  function corresponding
                to the `func_call`
                and returns the Node.FUNC_DEF corresponding to it. Or
                throws an InvalidCode exception if it didn't find it'''
                assert func_call.type == Node.Type.FUNC_CALL, f"Not a Node.FUNC_CALL {func_call}"
                func_sig = cls.__fromFuncCall(func_call)
                func_def = func_sig.__lookRecursively(scope)
                if func_def is None:
                    call = func_sig.identifier
                    if call == None:
                        call = func_sig.als
                    invalidCode(f"Unknown function `{call}`", call)
                else:
                    return func_def
            
            @classmethod
            def checkFuncCall (cls, func_call: Node, scope: Scope) -> None:
                '''Checks if this Node.FUNC_CALL is calling
                an existing function (in local scope or parent ones),
                if not its an InvalidCode exception'''
                assert func_call.type == Node.Type.FUNC_CALL, f"Not a Node.FUNC_CALL {func_call}"
                cls.findFromFuncCall(func_call, scope)
                return
            
            def __eq__(self, other: object) -> bool:
                '''Two FunctionSignatures are equal if they
                have the same (`identifier` and `params_count`) or same `als`'''
                if isinstance(other, self.__class__):
                    identifierEq = self.identifier != None and self.identifier == other.identifier and self.params_count == other.params_count
                    alsEq = self.als != None and self.als == other.als
                    return identifierEq or alsEq
                else:
                    return False
        
        def __init__(self, parent: Type[Scope] | None, starter: Token) -> None:
            '''A Scope is a scope boi, what is there to explain.\n
            Every scope has its return variable that is
            synthesized from the `starter` which is
            the token that started this scope\n
            The class attributes are as follow:\n
            - `parent`: the parent scope if it exists\n
            - `return_var`: the return variable of this scope
            that is synthesized from the `starter`\n
            - `vars`: a `dict` that maps a Token.IDENTIFIER to an Instruction / Number\n
            - `funcs`: a `list` of Node.FUNC_DEF'''
            
            return_var = Token(Token.Type.IDENTIFIER, RETURN_VAR_NAME, *starter.getSynthesizedInfo())
            
            self.parent = parent
            self.return_var = return_var
            self.vars = {return_var: 0}
            self.funcs = []
        
        def resolveVar (self, identifier: Token) -> Number | Instruction:
            '''Looks for the variable recursively and returns its state\n
            If it doesn't exist then its an InvalidCode exception'''
            
            assert identifier.type == Token.Type.IDENTIFIER, f"Not a Token.IDENTIFIER {identifier}"
            
            scope = self
            while scope is not None:
                if identifier in scope.vars:
                    return scope.vars[identifier]
                scope = scope.parent
            invalidCode(f"Unknown variable `{identifier}`", identifier)
        
        def resolveFuncCall (self, func_call: Node, args: list[Number | Instruction]) -> Number | Instruction:
            '''Looks for the function recursively and
            calls (evaluates) it with the given arguments. If
            the function does not exists then its an InvalidCode exception'''
            
            assert func_call.type == Node.Type.FUNC_CALL, f"Not Node.FUNC_CALL {func_call}"
            
            func_def = Scope.FunctionSignature.findFromFuncCall(func_call, self)
            func_scope = Scope(self, func_def.components['func'])
            params = func_def.components['params']
            assert len(args) == len(params), f"Unreachable" # The correct fun_def is returned
            for param, arg in zip(params, args):
                func_scope.setVarState(param, False, arg)
            return evaluateScope(func_def.components['body'], func_scope)
        
        def setVarState (self, identifier: Token, ext: bool, state: Number | Instruction) -> None:
            '''Sets the new state for a variable, and if it doesn't exist add
            it, unless it's an external variable, then it's an InvalidCode exception'''
            assert identifier.type == Token.Type.IDENTIFIER, f"Not a Token.IDENTIFIER {identifier}"
            if ext:
                scope = self.parent # Since ext, self is skipped
                while scope is not None:
                    if identifier in scope.vars:
                        scope.vars[identifier] = state
                        return
                    scope = scope.parent
                invalidCode(f"This external variable does not exists", identifier)
            else:
                self.vars[identifier] = state
        
        def addFunc (self, func_def: Node) -> None:
            '''Adds a Node.FUNC_DEF to the scope (as a Scope.Function) if it doesn't
            already exist (in that scope), after validating it.
            Otherwise, if it exists or is invalid, throw an InvalidCode exception\n
            #### How it works:
            Simply check if this function already exists in this scope
            and check if you call any unknown functions. Simple as that.
            Also you don't add a function, meaning you don't define a function,
            unless it's valid, so that removes recursion.
            #### Reminder for my self:
            You may be like "Hey, well since when I call a function
            I check if it exists, why do it here. Here let's just
            check if it already exists in the scope and that's it"
            The problem with that would be that you could add a function
            and inside that function call another function that you define later
            on, and that one calls the first one.. And also recursion
            I'm only saying this
            because my head was fried yesterday and I left it as a note
            for today's me, so here I am for future me in case I change something'''
            
            def validateScopeFuncCalls (content: list[Node], parent_scope: Scope, starter: Token) -> None:
                '''Creates a new, temporary, scope for this content and validates
                its function calls'''
                
                def checkCalledFuncs (value_element: Node | Token, scope: Scope) -> None:
                    '''Checks if all the functions called
                    by the given value element are available
                    (in this scope or parent ones)'''
                    
                    assert isValueElement(value_element), f"Not a value element {value_element}"
                    
                    if type(value_element) == Token:
                        if value_element.type in [Token.Type.NUMBER, Token.Type.IDENTIFIER]:
                            return
                    
                    elif type(value_element) == Node:
                        if value_element.type == Node.Type.OP:
                            checkCalledFuncs(value_element.components['l_value'], scope)
                            checkCalledFuncs(value_element.components['r_value'], scope)
                            return
                        
                        elif value_element.type == Node.Type.ORDER_PAREN:
                            checkCalledFuncs(value_element.components['value'], scope)
                            return
                        
                        elif value_element.type == Node.Type.FUNC_CALL:
                            Scope.FunctionSignature.checkFuncCall(value_element, scope)
                            for arg in value_element.components['args']:
                                checkCalledFuncs(arg, scope)
                            return
                        
                        elif value_element.type == Node.Type.ANON_FUNC:
                            validateScopeFuncCalls(value_element.components['body'], scope, value_element.components['starter'])
                            return
                    
                    assert False, f"Unreachable"
                
                scope = Scope(parent_scope, starter)
                
                for node in content:
                    if node.type == Node.Type.VAR_ASSIGN:
                        checkCalledFuncs(node.components['value'], scope)
                    
                    elif node.type == Node.Type.FUNC_DEF:
                        scope.addFunc(node)
                    
                    elif node.type in [Node.Type.FUNC_CALL, Node.Type.ANON_FUNC]:
                        checkCalledFuncs(node, scope)
                    
                    elif node.type == Node.Type.RETURN:
                        if node.components['has_value']:
                            checkCalledFuncs(node.components['value'], scope)
                    
                    else:
                        assert False, f"Something other than instruction node {node}"
            
            assert func_def.type == Node.Type.FUNC_DEF, f"Something other than Node.FUNC_DEF {func_def}"
            
            Scope.FunctionSignature.checkAlreadyDefined(func_def, self)
            validateScopeFuncCalls(func_def.components['body'], self, func_def.components['func'])
            self.funcs.append(func_def)
        
        def getReturnVarState (self) -> Number | Instruction:
            '''Returns the return variable state'''
            try:
                return self.vars[self.return_var]
            except KeyError:
                assert False, f"Unreachable" # The return var is assigned to this scope at __init__
    
    def evaluateScope (content: list[Node], scope: Scope | tuple[Token , Scope | None]) -> Number | Instruction:
        '''Evaluates a scope and returns 
        the return variable value, either a Number
        or an Instruction.
        Either a Scope is given or a tuple
        to create a new one\n
        If a tuple is given it should contain:\n
            - `parent_scope`: the parent scope or `None` in case of the main scope\n
            - `starter`: a token that started this scope. To synthesize the return variable\n'''
        
        def processValueElement (value_element: Node | Token, scope: Scope) -> Number | Instruction:
            '''Processes a value element and returns an instruction
            or a number representing it'''
            
            assert isValueElement(value_element), f"Not a value element {value_element}"
            
            if type(value_element) == Token:
                if value_element.type == Token.Type.NUMBER:
                    return value_element.lexeme
                
                elif value_element.type == Token.Type.IDENTIFIER:
                    return scope.resolveVar(value_element)
                
            elif type(value_element) == Node:
                if value_element.type == Node.Type.OP:
                    op = OP_SET.fromSymbol(value_element.components['op'].lexeme)
                    l_value = processValueElement(value_element.components['l_value'], scope)
                    r_value = processValueElement(value_element.components['r_value'], scope)
                    return Instruction(op, l_value, r_value)
                
                elif value_element.type == Node.Type.ORDER_PAREN:
                    return processValueElement(value_element.components['value'], scope)
                
                elif value_element.type == Node.Type.FUNC_CALL:
                    args = []
                    for arg in value_element.components['args']:
                        args.append(processValueElement(arg, scope))
                    return scope.resolveFuncCall(value_element, args)
                
                elif value_element.type == Node.Type.ANON_FUNC:
                    return evaluateScope(value_element.components['body'], (scope, value_element.components['starter']))
            
            assert False, f"Unreachable"
        
        if type(scope) == tuple:
            parent_scope, starter = scope
            assert starter != None, f"No starter was given"
            scope = Scope(parent_scope, starter)
        
        for node in content:
            if node.type == Node.Type.VAR_ASSIGN:
                state = processValueElement(node.components['value'], scope)
                scope.setVarState(node.components['var'], node.components['ext'], state)
            
            elif node.type == Node.Type.FUNC_DEF:
                scope.addFunc(node)
            
            elif node.type in [Node.Type.FUNC_CALL, Node.Type.ANON_FUNC]:
                processValueElement(node, scope)
            
            elif node.type == Node.Type.RETURN:
                if node.components['has_value']:
                    return processValueElement(node.components['value'], scope)
                else:
                    return scope.getReturnVarState()
            
            else:
                assert False, f"Something other than an instruction node"
        
        return scope.getReturnVarState()
    
    assert ast.type == Node.Type.ROOT, f"Not Node.ROOT"
    
    return_value = evaluateScope(ast.components['content'], (None, ast.components['boc']))
    
    if isinstance(return_value, Number):
        return_value = Instruction(OP_SET.ADD, return_value, 0)
    return return_value


def compile (args: dict) -> None:
    '''Not only compiles, but rather does what ever is in the args'''
    
    FILE_PATH = args['file_path']
    DEBUG = args['debug']
    INTERPRET = args['interpret']
    
    tokens = parseSourceFile(FILE_PATH)
    if DEBUG:
        print('✅ Parsed')
        print("Tokens:\n", tokens)
    
    ast = constructAST(tokens)
    if DEBUG:
        print('✅ Constructed the AST')
        print("Node.ROOT['content']:\n")
        for node in ast.components['content']:
            print("\t-", node)
    
    program = constructProgram(ast)
    if DEBUG:
        print('✅ Constructed the program')
        str_program = str(program)[1:-1]
        print("Program:", str_program, sep='\n')
    
    
    result, time, count = program.runProgram()
    if INTERPRET:
        if result in [0, 1]:
            result = bool(result)
        elif result == 69:
            result = 'Nice'
        elif result > 99:
            chars = ''
            iteration = 0
            buffer = 0
            while result > 0:
                num = result % 10
                result //= 10
                buffer += num * 10**iteration
                iteration += 1
                if iteration == 3:
                    chars += (chr(int(buffer)))
                    buffer = 0
                    iteration = 0
            if iteration != 0:
                chars += (chr(int(buffer)))
            result = chars[:: -1]
    
    print(result)
    if DEBUG:
        print(f"The result of the program is {result}")
        print(f"It was computed in {time} seconds")
        print(f"It took {count} instructions to compute the result")