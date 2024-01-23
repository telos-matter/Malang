from __future__ import annotations

# Is it a compiler / interpreter / JIT compiler? I don't know, it's a runner.

if __name__ == '__main__':
    raise Exception('The runner should not be run directly.')

import os
from core import OP_SET, Operation
from typing import Type
from enum import Enum, auto
from numbers import Number


class Token ():
    class Type (Enum):
        '''Token types'''
        NUMBER        = auto() # Any number
        OP            = auto() # Any operation of the allowed operations from the set of operations (+, -, *..)
        EOL           = auto() # End of a line
        OPEN_PAREN    = auto() # Opening parenthesis `(`
        CLOSE_PAREN   = auto() # Closing parenthesis `)`
        IDENTIFIER    = auto() # Any identifier; variable, function name ext.. Can only have letters, `_` and numbers but can only start with the first two; _fOo10
        ASSIGN_OP     = auto() # The assigning operation, `=`
        DEF_KW        = auto() # The `def` keyword to declare functions
        OPEN_CURLY    = auto() # Opening curly brackets `{`
        CLOSE_CURLY   = auto() # Closing curly brackets `}`
        COMMA         = auto() # The `,` that separates the params or args
        SEMICOLON     = auto() # `;` to end expressions (not required)
        BOC           = auto() # Beginning of Content (It's Content and not File because the include keyword basically just copies and pastes the content of the included file in the one including it, and so its not a single file being parsed rather some content)
        EOC           = auto() # End of Content. This one is not used really
        EXT_KW        = auto() # The `ext` keyword to assign to external variables, the one in the parent scope recursively
        RET_KW        = auto() # The `ret` keyword to return values
        UNARY_ALS     = auto() # Unary aliases. They start with $
        BINARY_ALS    = auto() # Binary aliases. They start with @
        FOR_KW        = auto() # The `for` keyword for for loops
        COLON         = auto() # `:` to separate the parameters of the for loop
        
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
            elif self == Token.Type.FOR_KW:
                return 'for'
            elif self == Token.Type.COLON:
                return ':'
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
    
    @classmethod
    def synthesizeNumber (cls, value: Number, synthesizer: Token) -> Token:
        '''Synthesizes a Token.NUMBER with the given value from the given synthesizer'''
        assert isinstance(value, Number), f"Not a number, {value}"
        assert type(synthesizer) == Token, f"Not a Token, {synthesizer}"
        
        return Token(Token.Type.NUMBER, value, *synthesizer.getSynthesizedInfo())
    
    @classmethod
    def synthesizeIdentifier (cls, name: str, synthesizer: Token) -> Token:
        '''Synthesizes a Token.IDENTIFIER with the given name from the given synthesizer'''
        assert type(name) == str, f"Not a string, {name}"
        assert type(synthesizer) == Token, f"Not a Token, {synthesizer}"
        
        return Token(Token.Type.IDENTIFIER, name, *synthesizer.getSynthesizedInfo())

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
        INCLUDE_SEP   = ',' # include std, str
        
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
                    
                    elif identifier == Token.Type.FOR_KW.lexeme:
                        tokenType = Token.Type.FOR_KW
                    
                    elif identifier == 'include':
                        # Split by INCLUDE_SEP and strip
                        included_files_paths = [path.strip() for path in line[j +1:].split(INCLUDE_SEP)]
                        for included_file_path in included_files_paths:
                            result = resolveFile(included_file_path, main_file_path)
                            if result is None:
                                temp_token = Token(None, line[i :], line, len(line) -i, file_path, line_index, i)
                                raise Exception(f"❌ NO SUCH FILE: Couldn't locate this file `{included_file_path}` that you wanted to include in here\n{temp_token.pointOut()}\n{temp_token.location()}")
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
                
                elif char == '"':
                    string, j = readString(line, i, file_path, line_index)
                    if len(string) == 0:
                        temp_token = Token(None, string, line, j -i, file_path, line_index, i)
                        parsingError(f"Strings can't be empty", temp_token)
                    value = 0
                    for c in string:
                        value *= 2**8
                        value += ord(c)
                    tokens.append(Token(Token.Type.NUMBER, value, line, j -i, file_path, line_index, i))
                    i = j
                
                elif char == "'":
                    string, j = readString(line, i, file_path, line_index)
                    if len(string) != 1:
                        temp_token = Token(None, string, line, j -i, file_path, line_index, i)
                        parsingError(f"Characters must contain one single character", temp_token)
                    tokens.append(Token(Token.Type.NUMBER, ord(string), line, j -i, file_path, line_index, i))
                    i = j
                
                elif char == Token.Type.COLON.lexeme:
                    tokens.append(Token(Token.Type.COLON, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char == '#':
                    # A line comment, go to the next line
                    break
                
                elif char.isspace():
                    i += 1
                
                else:
                    temp_token = Token(None, char, line, len(char), file_path, line_index, i)
                    parsingError(f"Unexpected / unacceptable char: `{char}`", temp_token)
            
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
        OP          = auto() # Any operation of the allowed operations from the set of operations (+, -, *..)
        ORDER_PAREN = auto() # Order parenthesis. They can only contain a value element
        FUNC_DEF    = auto() # Function definition. Can have nested functions. Functions overloading is allowed
        FUNC_CALL   = auto() # Function call
        ANON_FUNC   = auto() # Anonymous function
        RETURN      = auto() # Return to return from scopes, either a value in front of it or the return variable
        FOR_LOOP    = auto() # A deterministic for loop. Gets unwrapped at compilation / runtime
    
    def __init__(self, nodeType: Node.Type, **components) -> None:
        ''' The components that each nodeType has:\n
        - `ROOT`:
            - `boc`: the beginning of content Token
            - `content`: a list of the instruction nodes. The compiled files
            - `eoc`: the end of content Token
        - `VAR_ASSIGN`:
            - `ext`: a boolean stating whether this variable is a local or external one
            - `var`: an identifier token representing the variable getting assigned to
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
            - `starter`: a Token.OPEN_CURLY representing the start of the anonymous function
            - `body`: a list of nodes (another AST, but without the root node) 
            representing the body of the anonymous function. It
            can contain any other node, including another Node.ANON_FUNC
        - `RETURN`:
            - `has_value`: a boolean indicating whether this return has a value that
            it should return or if it should return the return variable
            - `value`: a value element that would be returned, if and only if `has_value`
            is `True`
        - `FOR_LOOP`:
            - `for_kw`: the `for` keyword of this for loop. Used to raise errors
            - `has_var`: a boolean indicating whether this for loop uses / has
            a variable
            - `var`: a Token.IDENTIFIER representing the variable is going
            to take the iteration values. Like `i` for example. Only exists
            if `has_var` is `True`
            - `begin`: a value element representing from where the loop
            should start
            - `end`: a value element representing up to where the loop
            should end
            - `step`: a value element representing the step by which
            to increment the variable. If it is negative, the iteration
            would start from end
            - `starter`: a Token.OPEN_CURLY representing the start of
            the for loop body. Used to synthesize tokens
            - `body`: a list of instruction nodes representing
            the body of the for loop that is going to get duplicated
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
        return self.type in [Node.Type.VAR_ASSIGN, Node.Type.FUNC_DEF, Node.Type.ANON_FUNC, Node.Type.RETURN, Node.Type.FOR_LOOP]
    
    def __repr__(self) -> str:
        return f"{self.type}\n\t=> {self.components}"
    
    @classmethod
    def makeVarAssign (cls, ext: bool, var: Token, value: Node | Token) -> Node:
        '''Creates a Node.VAR_ASSIGN'''
        assert type(ext) == bool, f"Not a bool, {ext}"
        assert type(var) == Token and var.type == Token.Type.IDENTIFIER, f"Not a Token.IDENTIFIER, {var}"
        assert isValueElement(value), f"Not a value element, {value}"
        
        return Node(Node.Type.VAR_ASSIGN, ext=ext, var=var, value=value)

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
    
    def processValueExpression (tokens: list[Token], parent_token: Token, start_index: int, skip_eols: bool, accepts_semicolons: bool, accepts_comas: bool, accepts_colons: bool) -> tuple[Node | Token, int]:
        '''Processes a value expression and return a value element
        representing it as well as from where to continue\n
        Whether a value expression can have certain
        terminators vary, so
        the parameters specify whether it can have it or not\n
        `tokens`: normally, the list of all the tokens\n
        `parent_token`: the token that "wants" this value expression. To raise a SyntaxError with in case of an error\n
        `start_index`: from where to start processing. Safe if it's outsides the `tokens` bound\n
        `skip_eols`: skip EOLs or terminate when encountered\n
        `accepts_semicolons`: can a semicolon be in this value expression?\n
        `accepts_comas`: can a coma be in this value expression?\n
        `accepts_colons`: can a colon be in this values expression?\n
        '''
        
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
                    value, _ = processValueExpression(tokens[i +1 : close_paren], token, 0, True, False, False, False)
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
            
            elif tokenType == Token.Type.COLON:
                if accepts_colons:
                    break
                else:
                    syntaxError(f"Colons can't be here", token)
            
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
                arg, inc = processValueExpression(args_tokens, args_tokens[inc], inc +1, True, False, True, False)
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
            syntaxError(f"There should be an identifier representing the name of the function being defined right after the `{tokens[i -1]}` keyword", tokens[i -1])
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
    
    def processForLoop (tokens: list[Token], for_kw_index: int) -> tuple[Node, int]:
        '''Processes a for loop and returns a Node.FOR_LOOP
        and the index at which to continue, which is where the for loop
        body ends +1\n
        `tokens`: normally, a list of all the tokens\n
        `for_kw_index`: the Token.FOR_KW index by which you
        knew this is a for loop'''
        
        i = for_kw_index # Just for ease of reference
        assert tokens[i].type == Token.Type.FOR_KW, f"Not Token.FOR_KW"
        
        i += 1
        open_paren_index = isNextToken(tokens, Token.Type.OPEN_PAREN, i, (f'Expected an open parenthesis `(` after the `for` keyword to define the loop "parameters"', tokens[i -1]))
        close_paren_index = findEnclosingToken(tokens, Token.Type.OPEN_PAREN, Token.Type.CLOSE_PAREN, open_paren_index +1, tokens[open_paren_index])
        
        # Get the parameters of this for loop
        parameters = tokens[open_paren_index : close_paren_index] # The open parenthesis is included for ease of work
        temp = [] # Where the value expressions of the parameters are going to go
        param_i = 0
        while param_i < len(parameters):
            # Process the parameter
            value, param_i = processValueExpression(parameters, parameters[param_i], param_i +1, True, False, False, True)
            # Store the value   
            temp.append(value)
        parameters = temp
        # Check how many parameters have we got
        # At least 1, the end index
        if len(parameters) < 1:
            syntaxError(f"Must specify at least the end index of this for loop", tokens[for_kw_index])
        # And no more than 4, var: begin: end: step
        if len(parameters) > 4:
            syntaxError(f"You have {len(parameters) -4} too many `:` in this for loop. Check the proper syntax", tokens[for_kw_index])
        # Distribute the parameters depending on how many are there
        has_var = False # We assume there is no var at first
        var, begin, end, step = None, None, None, None
        # If there is only 1 parameter, it's the end index parameter
        if len(parameters) == 1:
            end = parameters[0]
        # If there are 2, it's the begin and end
        elif len(parameters) == 2:
            begin, end = parameters
        # If there are 3, it's var, begin and end
        elif len(parameters) == 3:
            has_var = True
            var, begin, end = parameters
        # Otherwise, if 4, it's var, begin, end, and step
        elif len(parameters) == 4:
            has_var = True
            var, begin, end, step = parameters
        else:
            assert False, f"Unreachable, checked bounds before"
        assert end != None, f"Unreachable, something is always assigned to end"
        # Check validity of var. If it exists, it should be a Token.IDENTIFIER
        if has_var and (type(var) != Token or var.type != Token.Type.IDENTIFIER):
            syntaxError(f"There should be a single identifier representing the variable of this for loop, first thing after the open parenthesis", tokens[for_kw_index])
        # Give default values to begin and step if they aren't defined
        temp = [begin, step]
        for param_i, parameter in enumerate(temp.copy()):
            if parameter is None:
                parameter = Token.synthesizeNumber(1, tokens[open_paren_index])
                temp[param_i] = parameter
        begin, step = temp
        i = close_paren_index +1
        
        # Get the body
        open_curly_index = isNextToken(tokens, Token.Type.OPEN_CURLY, i, ('Expected an open curly bracket `{` after this for loop "parameters" to start defining the loop\'s body', tokens[i -1]))
        close_curly_index = findEnclosingToken(tokens, Token.Type.OPEN_CURLY, Token.Type.CLOSE_CURLY, open_curly_index +1, tokens[open_curly_index])
        body = construct(tokens[open_curly_index +1 : close_curly_index], False)
        
        # Construct the Node.FOR_LOOP
        if has_var:
            return (Node(Node.Type.FOR_LOOP, for_kw=tokens[for_kw_index], has_var=has_var, var=var, begin=begin, end=end, step=step, starter=tokens[open_curly_index], body=body), close_curly_index +1)
        else:
            return (Node(Node.Type.FOR_LOOP, for_kw=tokens[for_kw_index], has_var=has_var, begin=begin, end=end, step=step, starter=tokens[open_curly_index], body=body), close_curly_index +1)
    
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
                value, i = processValueExpression(tokens, tokens[i], i +1, False, True, False, False)
                content.append(Node.makeVarAssign(True, identifier, value))
                
            elif tokenType == Token.Type.IDENTIFIER: # LOCAL Node.VAR_ASSIGN or Node.FUNC_CALL
                if len(tokens) <= i +1:
                    syntaxError(f"Expected something after this identifier", token)
                i += 1
                if tokens[i].type == Token.Type.ASSIGN_OP: # Node.VAR_ASSIGN
                    value, i = processValueExpression(tokens, tokens[i], i +1, False, True, False, False)
                    content.append(Node.makeVarAssign(False, token, value))
                
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
                    value, i = processValueExpression(tokens, token, i, False, True, False, False)
                    content.append(Node(Node.Type.RETURN, has_value=True, value=value))
            
            elif tokenType == Token.Type.FOR_KW: # Node.FOR_LOOP
                for_loop, i = processForLoop(tokens, i)
                content.append(for_loop)
            
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


def constructProgram (ast: Node, args: list[Number]) -> Operation:
    '''Constructs the program by translating
    Nodes into Operations (only a single Operation
    is returned of course)\n
    Also checks for the validity of the code; referencing
    a none existing variable, defining an already existing
    function, recursion and
    cyclic calls.\n
    - `args`: The args that will be passed to the main function'''
    
    RETURN_VAR_NAME = 'res'
    EXTERNAL_RETURN_VAR_NAME = 'ext_res'
    
    MAIN_FUNCTION_NAME = 'main'
    
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
        
        # Scopes counter
        __counter = 0
        # Attribute to assert that only 1 main scope is created.
        __created_main_scope = False
        def __init__(self, parent: Type[Scope] | None, starter: Token) -> None:
            '''A Scope is a scope boi, what is there to explain.\n
            Every scope has its return variable that is
            synthesized from the `starter` which is
            the token that started this scope\n
            The class attributes are as follow:\n
            - `id`: this scopes' ID\n
            - `main`: is this scope the main scope?\n
            - `parent`: the parent scope if it exists\n
            - `return_var`: the return variable of this scope
            that is synthesized from the `starter`\n
            - `vars`: a `dict` that maps a Token.IDENTIFIER to an Operation / Number\n
            - `funcs`: a `list` of Node.FUNC_DEF'''
            
            Scope.__counter += 1 # Inc the counter
            # Create the return var
            return_var = Token.synthesizeIdentifier(RETURN_VAR_NAME, starter)
            
            self.id = Scope.__counter
            self.main = parent is None
            self.parent = parent
            self.return_var = return_var
            self.vars = {return_var: 0}
            self.funcs = []
            
            # Assert that only 1 main scope exists
            if self.main:
                assert not Scope.__created_main_scope, f"Already created the main Scope!"
                Scope.__created_main_scope = True
        
        def resolveVar (self, identifier: Token) -> Number | Operation:
            '''Looks for the variable recursively and returns its state\n
            If it doesn't exist then its an InvalidCode exception'''
            
            assert identifier.type == Token.Type.IDENTIFIER, f"Not a Token.IDENTIFIER {identifier}"
            
            # Look for the variable recursively
            scope = self
            while scope is not None:
                if identifier in scope.vars:
                    return scope.vars[identifier]
                scope = scope.parent
            # If failed, check if the var is the external return variable
            if identifier.lexeme == EXTERNAL_RETURN_VAR_NAME:
                if self.parent is not None:
                    return self.parent.getReturnVarState()
                invalidCode(f"This is the main scope. There is no scope above to reference its return variable.", identifier)
            invalidCode(f"Unknown variable `{identifier}`", identifier)
        
        def resolveFuncCall (self, func_call: Node, args: list[Number | Operation]) -> Number | Operation:
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
            return evaluateScope(func_def.components['body'], func_scope, None)
        
        def setVarState (self, identifier: Token, ext: bool, state: Number | Operation) -> None:
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
                its function calls\n
                Works on a copy of the content'''
                
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
                content = content.copy() # Make a copy to be able to append Node.FOR_LOOP content so that it's checked too
                
                i = 0
                while i < len(content):
                    node = content[i]
                    nodeType = node.type
                    
                    if nodeType == Node.Type.VAR_ASSIGN:
                        checkCalledFuncs(node.components['value'], scope)
                        i += 1
                    
                    elif nodeType == Node.Type.FUNC_DEF:
                        scope.addFunc(node)
                        i += 1
                    
                    elif nodeType in [Node.Type.FUNC_CALL, Node.Type.ANON_FUNC]:
                        checkCalledFuncs(node, scope)
                        i += 1
                    
                    elif nodeType == Node.Type.RETURN:
                        if node.components['has_value']:
                            checkCalledFuncs(node.components['value'], scope)
                        i += 1
                    
                    elif nodeType == Node.Type.FOR_LOOP:
                        checkCalledFuncs(node.components['begin'], scope)
                        checkCalledFuncs(node.components['end'], scope)
                        checkCalledFuncs(node.components['step'], scope)
                        content.pop(i)
                        content[i:i] = node.components['body'] # Need to check body only once
                        # Don't increment the i because it gets unwrapped at its place
                    
                    else:
                        assert False, f"Forgot to update instruction nodes here {node}"
            
            assert func_def.type == Node.Type.FUNC_DEF, f"Something other than Node.FUNC_DEF {func_def}"
            
            Scope.FunctionSignature.checkAlreadyDefined(func_def, self)
            validateScopeFuncCalls(func_def.components['body'], self, func_def.components['func'])
            self.funcs.append(func_def)
        
        def getReturnVarState (self) -> Number | Operation:
            '''Returns the return variable state'''
            try:
                return self.vars[self.return_var]
            except KeyError:
                assert False, f"Unreachable" # The return var is assigned to this scope at __init__
        
        def __str__(self) -> str:
            return str(self.id)
    
    def processValueElement (value_element: Node | Token, scope: Scope) -> Number | Operation:
            '''Processes a value element and returns an operation
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
                    return Operation(op, l_value, r_value)
                
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
    
    def unwrapForLoop(content: list[Node], where: int, scope: Scope) -> None:
        '''Unwraps the for loop located at `where` after evaluating its
        bounds'''
        
        def insertIteration(for_loop: Node, content: list[Node], where: int, iteration: int, var_value: Number) -> None:
            '''Insert the body of the `for_loop` in the
            appropriate position for the given iteration (computes it
            from the iteration and length of the body)\n
            `where`: the original `for_loop` position\n
            `var_value`: the value to assign to the loop's var
            in this iteration if it has a var'''
            assert for_loop.type == Node.Type.FOR_LOOP, f"Not a Node.FOR_LOOP {for_loop}"
            assert isinstance(var_value, Number), f"Not a Number {var_value}"
            
            has_var = for_loop.components['has_var']
            if has_var:
                var = for_loop.components['var']
            starter = for_loop.components['starter']
            body = for_loop.components['body']
            
            if has_var:
                var_assign = Node.makeVarAssign(False, var, Token.synthesizeNumber(var_value, starter))
            
            stride = len(body)
            if has_var:
                stride += 1 # +1 for the Node.VAR_ASSIGN
            offset = where + stride*iteration
            if has_var:
                # Insert the var assign
                content.insert(offset, var_assign)
                offset += 1
            # Insert the body
            content[offset:offset] = body
        
        assert content[where].type == Node.Type.FOR_LOOP, f"Not a Node.FOR_LOOP"
        
        for_loop = content.pop(where) # We remove it in all cases
        
        # Get the loop's parameters
        parameters = [
            for_loop.components['begin'],
            for_loop.components['end'],
            for_loop.components['step'],
        ]
        for i, parameter in enumerate(parameters):
            parameter = processValueElement(parameter, scope)
            if type(parameter) == Operation:
                parameter = parameter.result
            parameters[i] = parameter
        begin, end, step = parameters
        
        if step == 0:
            invalidCode(f"For loops can't have a zero step (infinite loop). This for loop step was evaluated and it was zero", for_loop.components['for_kw'])
        
        # Now we iterate and insert the body
        iteration = 0
        if step > 0:
            while begin <= end:
                insertIteration(for_loop, content, where, iteration, begin)
                begin += step
                iteration += 1
        else:
            while end >= begin:
                insertIteration(for_loop, content, where, iteration, end)
                end += step
                iteration += 1
    
    def evaluateScope (content: list[Node], scope: Scope | tuple[Scope | None, Token], args: list[Number] | None) -> Number | Operation:
        '''Evaluates a scope and returns 
        the return variable value, either a Number
        or an Operation.
        Either a Scope is given or a tuple
        to create a new one\n
        If a tuple is given it should contain:\n
            - `parent_scope`: the parent scope or `None` in case of the main scope\n
            - `starter`: a token that started this scope. To synthesize the return variable\n
        - `args`: the command line arguments for this program. Should only be present if it's the main scope 
        '''
        
        def extractMainFunction (content: list[Node], i: int, args: list[args]) -> None:
            '''Extracts the main function into the main scope content.\n
            - `i`: where is the main function in the content?'''
            assert content[i].type == Node.Type.FUNC_DEF, f"Not a Node.FUNC_DEF. {content[i]}"
            
            comps = content[i].components # For ease of reference
            params = comps['params'] # For ease of reference
            
            # First, make sure the provided arguments match the parameters in terms of arity
            if len(args) != len(params):
                n_a = len(args)
                n_p = len(params)
                message = None
                if n_a < n_p:
                    message = f"This main function requires {n_p} parameter{['s', ''][int(n_p == 1)]}, yet{[' only', ''][int(n_a == 0)]} {n_a} argument{['s were', ' was'][int(n_a == 1)]} given."
                else:
                    message = f"{n_a} argument{['s were', ' was'][int(n_a == 1)]} given. But this main function{[' only', ''][int(n_p == 0)]} takes {n_p} parameter{['s', ''][int(n_p == 1)]}."
                invalidCode(message, comps['func'])
            
            # Then remove the function
            content.pop(i)
            # Append the parameters
            for param, arg in zip(params, args):
                var_assign = Node.makeVarAssign(False, param, Token.synthesizeNumber(arg, param))
                content.insert(i, var_assign)
                i += 1
            # Finally, append the body
            content[i : i] = comps['body']
        
        print(f"Content before: {content}") # DEBUG
        
        if type(scope) == tuple:
            parent_scope, starter = scope
            assert starter != None, f"No starter was given"
            scope = Scope(parent_scope, starter)
        
        # Assert that args only exist with main scope
        assert scope.main == (args is not None), f"Main scope with no args, or args outside main scope. Scope: {scope}. Args: {args}"
        
        if not scope.main:
            content = content.copy() # Make a copy in which the for loops (if they exist) are going to get unwrapped for this scope
        i = 0
        while i < len(content):
            node = content[i]
            nodeType = node.type
            
            if nodeType == Node.Type.VAR_ASSIGN:
                state = processValueElement(node.components['value'], scope)
                scope.setVarState(node.components['var'], node.components['ext'], state)
                i += 1
            
            elif nodeType == Node.Type.FUNC_DEF:
                # If it's a main function, then extract it
                if scope.main and node.components['func'].lexeme == MAIN_FUNCTION_NAME:
                    extractMainFunction(content, i, args)
                    # Don't increment `i` so that the body gets executed
                
                # Otherwise just add to function definitions
                else:
                    scope.addFunc(node)
                    i += 1
            
            elif nodeType in [Node.Type.FUNC_CALL, Node.Type.ANON_FUNC]:
                processValueElement(node, scope)
                i += 1
            
            elif nodeType == Node.Type.RETURN:
                if node.components['has_value']:
                    return processValueElement(node.components['value'], scope)
                else:
                    return scope.getReturnVarState()
            
            elif nodeType == Node.Type.FOR_LOOP:
                unwrapForLoop(content, i, scope)
                # Don't increment `i` because it gets unwrapped at its place
            
            else:
                assert False, f"Forgot to update instruction nodes handling"
        
        print(f"Content after: {content}") # DEBUG
        
        return scope.getReturnVarState()
    
    def isValueElementConstant (value: Token | Node) -> bool:
        '''Determines if a value element is constant.
        That is, it can only contain Token.NUMBER, Token.OP
        or Node.ORDER_PAREN.\n
        Could extend the definition to include Node.FUNC_CALL
        with functions that return constant values, but
        I'm not too fucked to do that.'''
        assert isValueElement(value), f"Not a value element {value}"
        
        if type(value) == Token:
            if value.type == Token.Type.NUMBER:
                return True
            elif value.type == Token.Type.IDENTIFIER:
                return False
            else:
                assert False, f"Unreachable, checked that it is a Token value element before"
        elif type(value) == Node:
            if value.type == Node.Type.OP:
                return isValueElementConstant(value.components['l_value']) and isValueElementConstant(value.components['r_value'])
            elif value.type == Node.Type.ORDER_PAREN:
                return isValueElementConstant(value.components['value'])
            elif value.type in [Node.Type.FUNC_CALL, Node.Type.ANON_FUNC]:
                return False
            else:
                assert False, f"Unreachable, checked that it is a Node value element before"
        else:
            assert False, f"Unreachable, checked that it is a value element before"
    
    assert ast.type == Node.Type.ROOT, f"Not Node.ROOT"
    
    # Unwrap the constant Node.FOR_LOOPs (with Token.NUMBER indexes and step) once before starting
    content = ast.components['content']
    i = 0
    while i < len(content):
        node = content[i]
        comps = node.components
        # If it's a Node.FOR_LOOP with constant indexes and step
        if (node.type == Node.Type.FOR_LOOP and
                isValueElementConstant(comps['begin']) and
                isValueElementConstant(comps['end']) and
                isValueElementConstant(comps['step'])):
            unwrapForLoop(content, i, None) # NOTE: ATM having scope == None works fine because it does not need it. If we change something later on in the called functions then fix this
            # Don't increment the i because it gets unwrapped in its place
        
        else:
            i += 1
    
    # After unwrapping the constant Node.FOR_LOOPs, we evaluate the main scope
    return_value = evaluateScope(content, (None, ast.components['boc']), args)
    # If the resulting value is just a Number then make the simple operation of that_number + 0. So that's always an operation
    if isinstance(return_value, Number):
        return_value = Operation(OP_SET.ADD, return_value, 0)
    return return_value


def run (options: dict, args: list[Number]) -> None:
    '''Runs a program from source code with the specified options.\n
    - `args`: The args that will be passed to the main function'''
    
    import time
    start = time.time()
    
    FILE_PATH = options['file_path']
    VERBOSE = options['verbose']
    SHOW = options['show']
    DEBUG = options['debug']
    INTERPRET = options['interpret']
    
    
    if VERBOSE:
        print('👨🏻‍🍳 Parsing..')
    tokens = parseSourceFile(FILE_PATH)
    if VERBOSE:
        print('✅ Parsed')
    if DEBUG:
        print("Tokens:\n", tokens)
    
    if VERBOSE:
        print('👨🏻‍🍳 Constructing the AST..')
    ast = constructAST(tokens)
    if VERBOSE:
        print('✅ Constructed the AST')
    if DEBUG:
        print("Node.ROOT['content']:")
        for node in ast.components['content']:
            print("\t-", node)
    
    if VERBOSE:
        print('👨🏻‍🍳 Constructing and computing the operation..')
    program = constructProgram(ast, args)
    if VERBOSE:
        print('✅ Constructed and computed the operation')
    if SHOW:
        print("NOTE: Printing the operation could be, literally, physically impossible if the program is too big. Consider interrupting (Ctrl + c) this process and re-running it without the `-s` option. If you finished reading this and it still didn't print then it's probably not going to..")
        print('Operation:')
        str_program = str(program)[1:-1]
        print(str_program)
    
    count = program.operations_count
    if count > 10**100:
        import math
        count = int(math.log10(count)) # Actually surprised log is implemented in a way that it can handle this big of numbers. It wouldn't be dividing on 10 and counting, would it?
        count = f'around 10^{count}'
    
    original_result = program.result
    
    result = original_result
    if INTERPRET:
        if result in [0, 1]:
            result = bool(result)
        elif result == 69:
            result = 'Nice'
        elif result >= 0 and int(result) == result:
            chars = ''
            while result > 0:
                num = result & 0b1111_1111
                result = result >> 8
                chars += chr(num)
            result = chars[:: -1]
    
    end = time.time()
    duration = end - start
    
    if VERBOSE:
        if INTERPRET:
            print(f"📠 The interpreted result is `{result}`")
            print(f"🤖 The raw result is {original_result}")
        else:
            print(f"🧾 The result is {result}")
        print(f"🏃🏻 It took {count} operation{['', 's'][0 if count == 1 else 1]} to compute the result")
        print(f"⏱️  This whole process took {duration} seconds")
    else:
        print(result, end='')
