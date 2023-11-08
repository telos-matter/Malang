from core import OP_SET, Instruction
from enum import Enum, auto
from numbers import Number


class TokenType (Enum):
    NUMBER      = auto() # Any number
    OP          = auto() # Any operation of the allowed operations from the set of instruction (+, -, *..)
    EOL         = auto() # End of a line
    OPEN_PAREN  = auto() # Opening parenthesis `(`
    CLOSE_PAREN = auto() # Closing parenthesis `)`
    IDENTIFIER  = auto() # Any identifier; variable, function name ext.. Can only have letters, `_` and numbers but can only start with the first two; _fOo10
    ASSIGN_OP   = auto() # The assigning operation, `=`
    DEF_KW      = auto() # The `def` keyword to declare functions
    OPEN_CURLY  = auto() # Opening curly brackets `{`
    CLOSE_CURLY = auto() # Closing curly brackets `}`
    COMMA       = auto() # The `,` that separates the params and args
    SEMICOLON   = auto() # `;` to end expressions (not required)
    BOC         = auto() # Beginning of Content (It's Content and not File because the include keyword basically just copies and pastes the content of the included file in the one including it, and so its not a single file being parsed rather some content)
    EOC         = auto() # End of Content # This one is not used really

class Token ():
    def __init__(self, tokenType: TokenType, lexeme: str | Number, line: str, span: int, file_path: str, line_index: int, char_index: int, synthesized: bool=False) -> None:
        '''`line`: the actual line, the string in which this Token exists\n
        `span`: the length of the Token in the line\n
        `synthesized`: refers to whether the token was created by the compiler, for example -foo => (-1 * foo)
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
        return self.type in [TokenType.IDENTIFIER, TokenType.NUMBER]
    
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
    
    def __repr__(self) -> str:
        return str(self.lexeme)

def parseSourceFile (file_path: str) -> list[Token]:
    '''Takes a source file and parses its content to tokens
    Does not check for structure validity,
    only checks for content correctness\n
    Also handles includes'''
    
    def parsingError (message: str, temp_token: Token) -> None:
        '''Raises a parsing error exception'''
        message = "❌ PARSING ERROR: " +message +f"\n{temp_token.pointOut()}\n{temp_token.location()}"
        raise Exception(message)
    
    def readContent (file_path: str) -> str:
        '''Reads the content of a file\n
        If the file is empty it would return an empty str'''
        with open(file_path, 'r') as f:
            return f.read()
    
    NUMBER_PERIOD = '.' # 3.14
    NUMBER_SEP    = '_' # 100_00
    
    def parse (file_path: str, main: bool) -> list[Token]:
        '''The functions that actually parses the file\n
        `main` specifies whether this is the main file being
        parsed to know whether or not to include the BOC and EOC
        tokens'''
        
        content = readContent(file_path).splitlines() # Returns an empty list in case of empty content
        tokens = []
        
        if main:
            line = '' if len(content) == 0 else content[0]
            tokens.append(Token(TokenType.BOC, None, line, 0, file_path, 0, 0))
        
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
                        number = float(number)
                        if int(number) == number:
                            number = int(number)
                    except ValueError:
                        temp_token = Token(None, number, line, j -i, file_path, line_index, i)
                        parsingError(f"Couldn't parse this number: `{number}`", temp_token)
                    tokens.append(Token(TokenType.NUMBER, number, line, j -i, file_path, line_index, i))
                    i = j
                
                elif char in OP_SET.getSymbols(): # Should be after number to handle negative numbers
                    if char == OP_SET.IDIV.symbol[0] and i +1 < len(line) and line[i +1] == OP_SET.IDIV.symbol[1]: # Handles `//`
                        char = line[i : i +2]
                    tokens.append(Token(TokenType.OP, char, line, len(char), file_path, line_index, i))
                    i += len(char)
                
                elif char == '(':
                    tokens.append(Token(TokenType.OPEN_PAREN, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char == ')':
                    tokens.append(Token(TokenType.CLOSE_PAREN, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char == '_' or char.isalpha(): # An identifier, a keyword or include
                    identifier = char
                    j = i +1
                    while j < len(line) and (line[j].isalpha() or line[j].isdigit() or line[j] == '_'):
                        identifier += line[j]
                        j += 1
                    
                    tokenType = None
                    if identifier == 'def':
                        tokenType = TokenType.DEF_KW
                    elif identifier == 'include':
                        tokens.extend(parse(line[j:], False))
                        break
                    else:
                        tokenType = TokenType.IDENTIFIER
                    
                    tokens.append(Token(tokenType, identifier, line, j -i, file_path, line_index, i))
                    i = j
                
                elif char == '{':
                    tokens.append(Token(TokenType.OPEN_CURLY, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char == '}':
                    tokens.append(Token(TokenType.CLOSE_CURLY, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char == '=':
                    tokens.append(Token(TokenType.ASSIGN_OP, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char == ',':
                    tokens.append(Token(TokenType.COMMA, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char == ';':
                    tokens.append(Token(TokenType.SEMICOLON, char, line, len(char), file_path, line_index, i))
                    i += 1
                
                elif char == '#':
                    # A line comment, go to the next line
                    break
                
                elif char.isspace():
                    i += 1
                
                else:
                    temp_token = Token(None, char, line, len(char), file_path, line_index, i)
                    parsingError(f"Unexpected char: `{char}`", temp_token)
            
            tokens.append(Token(TokenType.EOL, '\n', line, 1, file_path, line_index, len(line))) # Fuck Windows' new lines
        
        if main:
            line = '' if len(content) == 0 else content[-1]
            tokens.append(Token(TokenType.EOC, None, line, 0, file_path, len(content), len(line)))
        
        return tokens
    
    return parse(file_path, True)


class NodeType (Enum):
    ROOT        = auto() # Root node of the content. Will only contain instruction nodes. Only 1 exists.
    VAR_ASSIGN  = auto() # Assigning to a variable
    OP          = auto() # Any operation of the allowed operations from the set of instruction (+, -, *..)
    ORDER_PAREN = auto() # Order parenthesis. They can only contain a value element
    FUNC_DEF    = auto() # Function definition. Can have nested functions. Functions overloading is allowed
    FUNC_CALL   = auto() # Function call
    ANON_FUNC   = auto() # Anonymous function

class Node():
    def __init__(self, nodeType: NodeType, **components) -> None:
        ''' The components that each nodeType has:\n
        - `ROOT`:
            - `boc`: the beginning of content Token
            - `content`: a list of the instruction nodes
            - `eoc`: the end of content Token
        - `VAR_ASSIGN`:
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
            - `params`: a list of identifier tokens representing the parameters
            - `body`: a list of nodes (another AST, but without the root node) 
            representing the body of the function. It
            can contain any other node, including another Node.FUNC_DEF
        - `FUNC_CALL`:
            - `func`: an identifier token representing the function being called
            - `args`: a list of value elements representing the arguments
        - `ANON_FUNC`:
            - `opener`: an open curly bracket representing the start of the anonymous function
            - `body`: a list of nodes (another AST, but without the root node) 
            representing the body of the anonymous function. It
            can contain any other node, including another Node.ANON_FUNC
        '''
        self.type = nodeType
        self.components = components
    
    def isValueNode (self) -> bool:
        '''Whether this Node is a value element node or not'''
        return self.type in [NodeType.OP, NodeType.ORDER_PAREN, NodeType.FUNC_CALL, NodeType.ANON_FUNC]
    
    def isInstructionNode (self) -> bool:
        '''Whether this Node is an instruction node or not\n
        Instruction nodes are the only Nodes that can start new instructions'''
        return self.type in [NodeType.VAR_ASSIGN, NodeType.FUNC_CALL, NodeType.FUNC_DEF, NodeType.ANON_FUNC]
    
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
        message = "❌ SYNTAX ERROR: " +message +f"\n{token.pointOut()}\n{token.location()}"
        raise Exception(message)
    
    def findEnclosingToken (tokens: list[Token], opening_tokenType: TokenType, enclosing_tokenType: TokenType, search_from: int, required: Token | None) -> int | None:
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
    
    def isNextToken (tokens: list[Token], tokenType: TokenType, start_from: int, required: tuple[str, Token] | None) -> int | None:
        '''Checks if the next token, from `start_from`, is `tokenType`, while skipping over
        Token.EOLs. If it is return its index, otherwise `None`\n
        `required`: if it's required that the next token be `tokenType`
        then this should be a tuple containing a message as well
        as a token to raise a SyntaxError exception with. If it's
        not required then give it `None`'''
        
        while start_from < len(tokens):
            if tokens[start_from].type == tokenType:
                return start_from
            elif tokens[start_from].type == TokenType.EOL:
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
        The location and what terminates a value expression can vary, so
        the parameters specify how to handle it\n
        `tokens`: normally, the list of all the tokens\n
        `parent_token`: the token that "wants" this value expression. To raise a SyntaxError with in case of an error\n
        `start_index`: from where to start processing\n
        `skip_eols`: skip EOLs or terminate when encountered\n
        `accepts_semicolons`: can a semicolon be in this value expression?\n
        `accepts_comas`: can a coma be in this value expression?\n'''
        
        def nextSingletonValue (tokens: list[Token], parent_token: Token, start_index: int) -> tuple[Node | Token, int]:
            '''Returns the immediate next singleton
            value starting from `start_index` along side the index
            on which to continue.\n
            A singleton value is a value element that exists on it's own. The
            only value element that is an exception to this is Node.OP, as it requires
            two value elements\n
            `tokens`: normally, a list of all the tokens\n
            `parent_token`: the token that "wants" this singleton value. To raise a SyntaxError with in case of an error\n
            `start_index`: from where to start\n'''
            
            i = start_index # Just for ease of reference
            token = tokens[i]
            tokenType = token.type
            singleton_value_element = None
            
            if tokenType == TokenType.NUMBER: # Token.NUMBER
                singleton_value_element = token
                i += 1
            
            elif tokenType == TokenType.IDENTIFIER: # A variable or a Node.FUNC_CALL
                if i +1 < len(tokens) and tokens[i +1].type == TokenType.OPEN_PAREN: # Node.FUNC_CALL
                    singleton_value_element, i = processFuncCall(tokens, token, i +1)
                
                else: # A variable
                    singleton_value_element = token
                    i += 1
            
            elif tokenType == TokenType.OPEN_PAREN: # Node.ORDER_PAREN
                close_paren = findEnclosingToken(tokens, TokenType.OPEN_PAREN, TokenType.CLOSE_PAREN, i +1, token)
                value, _ = processValueExpression(tokens[i : close_paren], token, 0, True, False, False)
                singleton_value_element = Node(NodeType.ORDER_PAREN, value=value)
                i = close_paren +1
            
            elif tokenType == TokenType.OPEN_CURLY: # Node.ANON_FUNC
                singleton_value_element, i = processAnonFunc(tokens, i)
            
            else:
                syntaxError(f"A value is required after this `{parent_token}`, found this instead `{token}`", parent_token)
            
            assert isValueElement(singleton_value_element) and (type(singleton_value_element) != Node or singleton_value_element.type != NodeType.OP), f"UNREACHABLE" # OCD
            return (singleton_value_element, i)
        
        def appendOP (root_op_node: Node, op: Token, r_value: Token | Node) -> Node:
            '''Adds the `op` to the tree of ops according to the precedence of its content
            and returns the new root node of the ops' tree\n
            The process of appending goes as follows:\n
            \tIf the `root_op_node`'s precedence is greater than or equal to `op` => It is `op`'s l_value\n
            \tOtherwise => The `op` is the `root_op_node` new r_value, and its old r_value is the `op`'s l_value (treating
            the r_value in a recursive fashion)\n
            '''
            assert root_op_node.type == NodeType.OP, f"The root_node is not a Node.OP"
            assert op.type == TokenType.OP, f"The op is not an op token"
            assert isValueElement(r_value), f"Passed an r_value that does not produce value"
            
            if OP_SET.fromSymbol(root_op_node.components['op'].lexeme).precedence >= OP_SET.fromSymbol(op.lexeme).precedence:
                return Node(NodeType.OP, op=op, l_value=root_op_node, r_value=r_value)
            else:
                root_op_r_value = root_op_node.components['r_value']
                root_op_new_r_value = None
                if type(root_op_r_value) == Node and root_op_r_value.type == NodeType.OP:
                    root_op_new_r_value = appendOP(root_op_r_value, op, r_value)
                else:
                    root_op_new_r_value = Node(NodeType.OP, op=op, l_value=root_op_r_value, r_value=r_value)
                root_op_node.components['r_value'] = root_op_new_r_value
                return root_op_node
        
        i = start_index # Just for ease of reference
        buffer = []
        value, i = nextSingletonValue(tokens, parent_token, i)
        buffer.append(value)
        
        while i < len(tokens): # Append Node.OPs if there is something left
            token = tokens[i]
            tokenType = token.type
            
            if tokenType == TokenType.OP: # Node.OP
                l_value = buffer[0]
                r_value, i = nextSingletonValue(tokens, token, i +1)
                if l_value == Node and l_value.type == NodeType.OP: # If an op is the previous value then append
                    buffer[0] = appendOP(l_value, token, r_value)
                else: # Otherwise create one
                    buffer[0] = Node(NodeType.OP, op=token, l_value=l_value, r_value=r_value)
            
            elif tokenType == TokenType.EOL:
                if skip_eols:
                    i += 1
                else:
                    break
            
            elif tokenType == TokenType.COMMA:
                if accepts_comas:
                    break
                else:
                    syntaxError(f"This comma can't be here", token)
            
            elif tokenType == TokenType.SEMICOLON:
                if accepts_semicolons:
                    break
                else:
                    syntaxError(f"This semicolon can't be here", token)
            
            else:
                syntaxError(f"What is this `{token}` doing here? (- In Hector Salamancas' voice) It can't be there", token)
            
        if len(buffer) != 1 or not isValueElement(buffer[0]):
            assert False, f"Buffer has a none value element: {buffer}"
        return (buffer[0], i)
    
    def processFuncCall (tokens: list[Token], func: Token, open_paren_index: int) -> tuple[Node, int]:
        '''Processes a function call and returns a Node.FUNC_CALL
        and the index at which to continue, which is where the function
        call ends +1\n
        `tokens`: normally, a list of all the tokens\n
        `func`: a Node.IDENTIFIER representing the function being called\n
        `open_paren_index`: where the function call starts'''
        i = open_paren_index # Just for ease of reference
        assert func.type == TokenType.IDENTIFIER, f"Not Token.IDENTIFIER"
        assert tokens[i].type == TokenType.OPEN_PAREN, f"Not Token.OPEN_PAREN"
        
        i += 1
        close_paren = findEnclosingToken(tokens, TokenType.OPEN_PAREN, TokenType.CLOSE_PAREN, i, tokens[i -1])
        args = []
        if isNextToken(tokens, TokenType.CLOSE_PAREN, i, None) is None: # If it has some args
            args_tokens = tokens[i : close_paren]
            inc = 0
            while i +inc < close_paren:
                parent_token = tokens[i +inc -1] if inc == 0 else tokens[i +inc] # First the `(` then the `,`s
                arg, inc = processValueExpression(args_tokens, parent_token, inc, True, False, True)
                if i +inc < close_paren:
                    assert tokens[i +inc].type == TokenType.COMMA, f"It should only exit if it encountered a comma. Exited on {tokens[i +inc]}"
                args.append(arg)
        return (Node(NodeType.FUNC_CALL, func=func, args=args), close_paren +1)
    
    def processAnonFunc (tokens: list[Token], open_curly_index: int) -> tuple[Node, int]:
        '''Processes an anonymous function and returns a Node.ANON_FUNC
        and the index at which to continue, which is where the anonymous
        function ends +1\n
        `tokens`: normally, a list of all the tokens\n
        `open_curly_index`: the anonymous function starter'''
        i = open_curly_index # Just for ease of reference
        assert tokens[i].type == TokenType.OPEN_CURLY, f"Not Token.OPEN_CURLY"
        
        close_curly = findEnclosingToken(tokens, TokenType.OPEN_CURLY, TokenType.CLOSE_CURLY, i +1, tokens[i])
        body = construct(tokens[i +1 : close_curly], False)
        return (Node(NodeType.ANON_FUNC, opener=tokens[i], body=body), close_curly +1)
    
    def construct (tokens: list[Token], root: bool) -> Node | list[Node]:
        '''The actual function that constructs
        the AST\n
        `root`: signifies whether this AST that is being constructed
        is the main content AST or not, to know whether to
        return a root node or a list of instruction nodes'''
        
        if root:
            assert tokens[0].type == TokenType.BOC, f"Not Token.BOC {tokens[0]}"
            assert tokens[-1].type == TokenType.EOC, f"Not Token.EOC {tokens[-1]}"
            BOC_TOKEN = tokens[0] # Leave them here so that it would raise an undefined error later on if we try to access them when we shouldn't. An assertion
            EOC_TOKEN = tokens[-1]
            tokens = tokens[1 : -1]
        
        content = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            tokenType = token.type
            
            if tokenType == TokenType.IDENTIFIER: # Node.VAR_ASSIGN or Node.FUNC_CALL
                if len(tokens) <= i +1:
                    syntaxError(f"Expected something after this identifier", token)
                i += 1
                if tokens[i].type == TokenType.ASSIGN_OP: # Node.VAR_ASSIGN
                    value, i = processValueExpression(tokens, tokens[i], i +1, False, True, False)
                    content.append(Node(NodeType.VAR_ASSIGN, var=token, value=value))
                
                elif tokens[i].type == TokenType.OPEN_PAREN: # Node.FUNC_CALL
                    func_call, i = processFuncCall(tokens, token, i)
                    content.append(func_call)
                
                else:
                    syntaxError(f"Was not expecting this after an identifier", tokens[i])
            
            elif tokenType == TokenType.DEF_KW: # Node.FUNC_DEF:
                i += 1
                if len(tokens) <= i or tokens[i].type != TokenType.IDENTIFIER:
                    syntaxError(f"There should be an identifier representing the name of the function being defined right after the `{token}` keyword", token)
                func = tokens[i]
                i += 1
                if len(tokens) <= i or tokens[i].type != TokenType.OPEN_PAREN:
                    syntaxError(f"There should be an open parenthesis right after the function's name to define this function's parameters", tokens[i])
                i += 1
                close_paren = findEnclosingToken(tokens, TokenType.OPEN_PAREN, TokenType.CLOSE_PAREN, i, tokens[i -1])
                params = []
                last_token_was_comma = True # True just to init
                while i < close_paren:
                    if tokens[i].type == TokenType.EOL:
                        i += 1
                    elif tokens[i].type == TokenType.COMMA:
                        if last_token_was_comma:
                            message = f"Expected a parameter's name to start with, not a comma" if len(params) == 0 else f"Two consecutive commas. A parameter is missing"
                            syntaxError(message, tokens[i])
                        else:
                            last_token_was_comma = True
                            i += 1
                    elif tokens[i].type == TokenType.IDENTIFIER:
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
                open_curly = isNextToken(tokens, TokenType.OPEN_CURLY, i +1, (f"Couldn't find an open curly bracket to start the body of the function after this:", tokens[i]))
                close_curly = findEnclosingToken(tokens, TokenType.OPEN_CURLY, TokenType.CLOSE_CURLY, open_curly +1, tokens[open_curly])
                body = construct(tokens[open_curly +1 : close_curly], False)
                content.append(Node(NodeType.FUNC_DEF, func=func, params=params, body=body))
                i = close_curly +1
            
            elif tokenType == TokenType.OPEN_CURLY: # Node.ANON_FUNC
                anon_func, i = processAnonFunc(tokens, i)
                content.append(anon_func)
            
            elif tokenType in [TokenType.EOL, TokenType.SEMICOLON]: # Skip
                i += 1
            
            elif tokenType in [TokenType.BOC, TokenType.EOC]: # Unreachable because they are removed from the list
                assert False, f"Unreachable"
            
            else:
                syntaxError(f"This `{token}` cannot start a new instruction", token)
        
        for node in content:
            assert node.isInstructionNode(), f"Content has something other than an instruction node {node}"
        if root:
            return Node(NodeType.ROOT, boc=BOC_TOKEN, content=content, eoc=EOC_TOKEN)
        else:
            return content
    
    return construct(tokens, True)


RETURN_VAR_NAME = 'res'

def validateAST (ast: list[Node]) -> None:
    '''Checks for the validity of the code; referencing
    a none existing variable, or defining an already existing
    function. (Recursion and cyclic calls are automatically 
    accounted for by the fact that functions definitions
    are sequential)'''
    
    def invalidCode (message: str, token: Token) -> None:
        '''Raises an invalid code exception.'''
        message = "❌ INVALID CODE: " +message
        if token is not None: # TODO??? why is it like so? just add it normally. dont have any case where its none
            message += f"\n{token.pointOut()}\n{token.location()}"
        raise Exception(message)
    
    def getVarsUsedByValueElement (value_element: Node | Token) -> set[Token]:
        '''Returns a set of Token.IDENTIFIER representing
        the variables USED BY this value element.'''
        assert isValueElement(value_element), f"Passed something other than a Value Element"
        
        if type(value_element) == Token:
            if value_element.type == TokenType.IDENTIFIER:
                return {value_element}
            
            elif value_element.type == TokenType.NUMBER:
                return set()
        
        elif type(value_element) == Node:
            if value_element.type == NodeType.OP:
                l_value = value_element.components['l_value']
                vars = getVarsUsedByValueElement(l_value)
                r_value = value_element.components['r_value']
                vars |= getVarsUsedByValueElement(r_value)
                return vars
            
            elif value_element.type == NodeType.ORDER_PAREN:
                value = value_element.components['value']
                return getVarsUsedByValueElement(value)
            
            elif value_element.type == NodeType.FUNC_CALL:
                vars = set()
                args = value_element.components['args']
                for arg in args:
                    vars |= getVarsUsedByValueElement(arg)
                return vars
        
        assert False, f"Unreachable"
    
    def getFuncsUsedByValueElement (value_element: Node | Token) -> set[Token]:
        '''Returns a set of Token.IDENTIFIER representing
        the functions USED BY this value element.'''
        assert isValueElement(value_element), f"Passed something other than a Value Element"
        
        if type(value_element) == Token:
            if value_element.type == TokenType.IDENTIFIER:
                return set()
            
            elif value_element.type == TokenType.NUMBER:
                return set()
        
        elif type(value_element) == Node:
            if value_element.type == NodeType.OP:
                l_value = value_element.components['l_value']
                funcs = getFuncsUsedByValueElement(l_value)
                r_value = value_element.components['r_value']
                funcs |= getFuncsUsedByValueElement(r_value)
                return funcs
            
            elif value_element.type == NodeType.ORDER_PAREN:
                value = value_element.components['value']
                return getFuncsUsedByValueElement(value)
            
            elif value_element.type == NodeType.FUNC_CALL:
                funcs = {value_element.components['func']}
                args = value_element.components['args']
                for arg in args:
                    funcs |= getFuncsUsedByValueElement(arg)
                return funcs
        
        assert False, f"Unreachable"
    
    def checkVarsAndFuncsUsedByValueElement (value_element: Node | Token, vars: set[Token], funcs: set[Token]) -> None:
        '''Checks if the variables and functions used
        by this value element already exist'''
        assert isValueElement(value_element), f"Something other than value element"
        
        used_vars = getVarsUsedByValueElement(value_element)
        if not used_vars.issubset(vars):
            var = next(iter(used_vars.difference(vars)))
            invalidCode(f"Unknown variable `{var}`", var)
        used_funcs = getFuncsUsedByValueElement(value_element)
        if not used_funcs.issubset(funcs):
            func = next(iter(used_funcs.difference(funcs)))
            invalidCode(f"Unknown / undefined function `{func}`", func)
    
    def validate (ast: list[Node], vars: set[Token], funcs: set[Token]) -> None:
        '''The functions that actually validates the AST.\n
        It is put here because it can be called recursively\n
        `vars`: the variables that I have access to\n
        `funcs`: the funcs that I have access to'''
        
        for node in ast:
            if node.type == NodeType.VAR_ASSIGN:
                value = node.components['value']
                checkVarsAndFuncsUsedByValueElement(value, vars, funcs)
                vars.add(node.components['var'])
            
            elif node.type == NodeType.FUNC_DEF:
                func = node.components['func']
                if func in funcs:
                    original = [original for original in funcs if original == func][0]
                    invalidCode(f"This function `{func}` is already defined here:\n{original.location()}: {original.pointOut()}", func)
                func_vars = {Token(TokenType.IDENTIFIER, RETURN_VAR_NAME, *func.getSynthesizedInfo())}
                func_vars |= set(node.components['params'])
                validate(node.components['body'], func_vars, funcs.copy())
                funcs.add(func)
            
            elif node.type == NodeType.FUNC_CALL:
                checkVarsAndFuncsUsedByValueElement(node, vars, funcs)
            
            else:
                assert False, f"Forgot to update this. Expecting instruction nodes"

    return_var = Token(TokenType.IDENTIFIER, RETURN_VAR_NAME, '', 0, None, 0, 0) # TODO appoint it to the start line either of the function or the file. Requires adding begin_file token
    validate(ast, {return_var}, set())


def constructProgram (ast: list[Node]) -> Instruction:
    '''Constructs the program from a valid AST. Translates
    Nodes into Instructions'''
    
    def setValueInstruction(value: Number) -> Instruction:
        '''Creates an instruction that sets a value'''
        return Instruction(OP_SET.ADD, value, 0)
    
    def getInstruction(value: Node | Token, vars_state: dict[Token, Instruction]) -> Instruction | Number:
        '''IDK how it will work when we have functions, but the
        idea rn is that it takes stuff that don't affect
        the `var_state`. RN there is only VAR_ASSIGN, so it takes
        its value
        and recessively calls it selfs to find its Instruction
        or if its a simple number returns it
        HMMM how about getValueInstruction, that way for params it would
        call this and it works fine
        Boi you worrying about the name and idea you gave to the function
        YOU CAN EDIT BOI + ITS YOUR PROJECT STFU, do whatever you want'''
        
        if type(value) == Token:
            if value.type == TokenType.NUMBER:
                return value.lexeme
            
            elif value.type == TokenType.IDENTIFIER:
                return vars_state[value]
            
            else:
                assert False, f"Forgot to update this. Received {value}"
            
        elif type(value) == Node:
            if value.type == NodeType.OP:
                op = OP_SET.fromSymbol(value.components['op'].lexeme)
                l_value = getInstruction(value.components['l_value'], vars_state)
                r_value = getInstruction(value.components['r_value'], vars_state)
                return Instruction(op, l_value, r_value)
            
            elif value.type == NodeType.ORDER_PAREN:
                return getInstruction(value.components['value'], vars_state)
            
            elif value.type == NodeType.VAR_ASSIGN:
                assert False, f"A Node.VAR_ASSIGN can't be here. {value}"
            
            else:
                assert False, f"Forgot to update this. Received {value}"
            
        else:
            assert False, f"Something other than Node and Token? {value}"
    
    return_var = Token(TokenType.IDENTIFIER, RETURN_VAR_NAME, '', 0, None, 0, 0) # TODO maybe later on appoint it to the start line either of the function or the file
    vars_state = {return_var: setValueInstruction(0)}
    
    for node in ast:
        if node.type == NodeType.VAR_ASSIGN:
            var = node.components['var']
            value = node.components['value']
            vars_state[var] = getInstruction(value, vars_state)
            
        else:
            assert False, f"Something other than Node.VAR_ASSIGN"
    
    return_value = vars_state[return_var]
    if isinstance(return_value, Number):
        return_value = setValueInstruction(return_value)
    return return_value


def runSourceFile (file_path: str) -> None:
    '''Compiles and runs a source file'''
    
    DEBUG = True
    
    tokens = parseSourceFile(file_path)
    if DEBUG:
        print('✅ Parsing')
        print("Tokens:\n", tokens)
    
    ast = constructAST(tokens)
    if DEBUG:
        print('✅ Constructing the AST')
        print("AST:\n")
        for node in ast:
            print("-", node)
    
    validateAST(ast)
    if DEBUG:
        print('✅ AST is valid')
    
    program = constructProgram(ast)
    if DEBUG:
        print('✅ Constructing the program')
        print("Program:", program, sep='\n')
    
    program.runProgram()