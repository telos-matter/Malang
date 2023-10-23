from enum import Enum, auto
from core import OP_SET

class TokenType (Enum):
    NUMBER      = auto()     # Any number
    OP          = auto()     # Any operation of the allowed operations from the set of instruction (+, -, *..)
    EOL         = auto()     # End of a line (Could also be an EOF)
    OPEN_PAREN  = auto()     # Opening parenthesis `(`
    CLOSE_PAREN = auto()     # Closing parenthesis `)`
    IDENTIFIER  = auto()     # Any identifier; variable, function name ext.. Can only have letters, `_` and numbers but can only start with the first two; _fOo10
    ASSIGN_OP   = auto()     # The assigning operation, `=`

class Token ():
    def __init__(self, tokenType: TokenType, lexeme: str | float | int, line: str, span: int, file_path: str, line_index: int, char_index: int) -> None:
        '''`line`: the line in which this Token exists\n
        `span`: the length of the Token in the line
        '''
        self.type = tokenType
        self.lexeme = lexeme
        self.line = line
        self.span = span
        self.file = file_path
        self.line_number = line_index +1
        self.char_number = char_index +1
    
    def location(self) -> str:
        return f"File `{self.file}`, line: {self.line_number}, column: {self.char_number}"
    
    def pointOut(self) -> str:
        return f"{self.line[:self.char_number -1]}>>>{self.line[self.char_number -1 : self.char_number -1 +self.span]}<<<{self.line[self.char_number -1 +self.span:]}"
    
    def __repr__(self) -> str:
        return str(self.lexeme)

def parseSourceFile (content: str, filePath: str) -> list[Token]:
    '''Takes a source file and parses its content to tokens
    Does not check for structure validity,
    only checks for content correctness'''
    
    def parsingError (message: str, temp_token: Token) -> None:
        '''Raises a parsing error exception'''
        message = "PARSING ERROR: " +message +f"\n{temp_token.pointOut()}\n{temp_token.location()}"
        raise Exception(message)
    
    NUMBER_PERIOD = '.'
    tokens = []
    
    for line_index, line in enumerate(content.splitlines()):
        i = 0
        while i < len(line):
            char = line[i]
            
            if char in OP_SET.getSymbols():
                if char == OP_SET.OP_IDIV.symbol[0] and i +1 < len(line) and line[i +1] == OP_SET.OP_IDIV.symbol[1]:
                    char = line[i : i +2]
                tokens.append(Token(TokenType.OP, char,line, len(char), filePath, line_index, i))
                i += len(char)
            
            elif char.isdigit():
                number = char
                j = i +1
                while j < len(line) and (line[j].isdigit() or line[j] == NUMBER_PERIOD):
                    number += line[j]
                    j += 1
                try:
                    number = float(number)
                    if int(number) == number:
                        number = int(number)
                except ValueError:
                    temp_token = Token(None, number, line, j -i, filePath, line_index, i)
                    parsingError(f"Couldn't parse this number: `{number}`", temp_token)
                tokens.append(Token(TokenType.NUMBER, number, line, j -i, filePath, line_index, i))
                i = j
            
            elif char == '(':
                tokens.append(Token(TokenType.OPEN_PAREN, char, line, len(char), filePath, line_index, i))
                i += 1
            
            elif char == ')':
                tokens.append(Token(TokenType.CLOSE_PAREN, char, line, len(char), filePath, line_index, i))
                i += 1
            
            elif char == '_' or char.isalpha():
                identifier = char
                j = i +1
                while j < len(line) and (line[j].isalpha() or line[j].isdigit() or line[j] == '_'):
                    identifier += line[j]
                    j += 1
                tokens.append(Token(TokenType.IDENTIFIER, identifier, line, j -i, filePath, line_index, i))
                i = j
            
            elif char == '=':
                tokens.append(Token(TokenType.ASSIGN_OP, char, line, len(char), filePath, line_index, i))
                i += 1
            
            elif char == '#':
                # A line comment, go to the next line
                break
            
            elif char.isspace():
                i += 1
            
            else:
                temp_token = Token(None, char, line, len(char), filePath, line_index, i)
                parsingError(f"Unexpected char: `{char}`", temp_token)
        
        tokens.append(Token(TokenType.EOL, '\n', line, 1, filePath, line_index, len(line))) # Fuck Windows' new lines
    
    return tokens


class NodeType (Enum):
    VAR_ASSIGN  = auto() # Assigning to a variable
    OP          = auto() # Any operation of the allowed operations from the set of instruction (+, -, *..)
    ORDER_PAREN = auto() # Order parenthesis. They can only contain a value element

class Node():
    def __init__(self, nodeType: NodeType, **components) -> None:
        ''' The components that each nodeType has:\n
        `VAR_ASSIGN`:
            var: an identifier token representing the variable getting assigned to
            value: a value element representing the assigned value
        `OP`:
            op: the op token representing the operation being performed
            l_value: a value element representing the left value of the operation
            r_value: a value element representing the right value of the operation
        `ORDER_PAREN`:
            value: a value element representing their content
        \n
        A value element means a Token or a Node that can return or is a value, one
        fo these: Token.NUMBER, Token.IDENTIFIER, Node.OP or Node.ORDER_PAREN
        '''
        self.type = nodeType
        self.components = components
    
    def __repr__(self) -> str:
        return f"{self.type}\n\t=> {self.components}"

def constructAST (tokens: list[Token]) -> list[Node]:
    '''Takes tokens and construct a list of nodes representing their ast
    Does not check for the validity of the
    code (referencing a none existing variable for example or recursion),
    only checks for validity of the structure / syntax'''
    
    def syntaxError (message: str, token: Token) -> None:
        '''Raises a syntax error exception'''
        message = "SYNTAX ERROR: " +message +f"\n{token.pointOut()}\n{token.location()}"
        raise Exception(message)
    
    def producesValue (element: Token | Node) -> bool:
        '''Checks if the element is a value element'''
        if type(element) == Token:
            return element.type in [TokenType.NUMBER, TokenType.IDENTIFIER]
        elif type(element) == Node:
            return element.type in [NodeType.OP, NodeType.ORDER_PAREN]
        else:
            assert False, f"Passed something other than Token or Node, {element}"
    
    def appendOP (root_node: Node, op: Token, r_value: Token | Node) -> Node:
        '''Adds the `op` to the tree according to the precedence of its content
        and returns the new root node\n
        The process of appending goes as follows:\n
        \tIf the root_nodes' precedence is greater than or equal to mine => It is my l_value\n
        \tOtherwise => Im its new r_value, and its old r_value is my l_value (treating
        the r_value in a recursive fashion)\n
        '''
        assert root_node.type == NodeType.OP, f"The root_node is not a Node.OP"
        assert op.type == TokenType.OP, f"The op is not an op token"
        assert producesValue(r_value), f"Passed an r_value that does not produce value"
        
        if OP_SET.fromSymbol(root_node.components['op'].lexeme).precedence >= OP_SET.fromSymbol(op.lexeme).precedence:
            return Node(NodeType.OP, op=op, l_value=root_node, r_value=r_value)
        else:
            root_r_value = root_node.components['r_value']
            new_r_value = None
            if type(root_r_value) == Node and root_r_value.type == NodeType.OP:
                new_r_value = appendOP(root_r_value, op, r_value)
            else:
                new_r_value = Node(NodeType.OP, op=op, l_value=root_r_value, r_value=r_value)
            root_node.components['r_value'] = new_r_value
            return root_node
    
    def findToken (tokens: list[Token], tokenType: TokenType, search_from: int) -> int | None:
        '''Looks for a Token starting from `search_from`'''
        while search_from < len(tokens):
            if tokens[search_from].type == tokenType:
                return search_from
            search_from += 1
        return None
    
    def findEnclosingToken (tokens: list[Token], opening_tokenType: TokenType, enclosing_tokenType: TokenType, search_from: int) -> int | None:
        '''Returns the index of the enclosing token starting from `search_from`
        This handles nested tokens such as ((())) for example'''
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
        return None
    
    def processValueExpression (tokens: list[Token], parent_token: Token) -> Node | Token:
        '''Called to process a value expression and return a value element representing it\n
        `tokens` is a sub list of the actual tokens and
        would have the content of whatever is between parenthesis,
        function parameters or a variable assignment for example\n
        `parent_token` is the token that wants to process this value expression\n
        It does not care for EOLs and just process/parses whatever
        was given to it as long as it can be in a single expression'''
        buffer = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            tokenType = token.type
            
            if tokenType == TokenType.NUMBER:
                if len(buffer) != 0:
                    syntaxError(f"The number `{token}` can't be here! Expected an operation.", token)
                buffer.append(token)
                i += 1
            
            elif tokenType == TokenType.IDENTIFIER:
                if len(buffer) != 0:
                    syntaxError(f"The variable `{token}` can't be here! Expected an operation", token)
                buffer.append(token)
                i += 1
            
            elif tokenType == TokenType.OPEN_PAREN:
                if len(buffer) != 0:
                    syntaxError(f"This open parenthesis `{token}` can't be here! Expected an operation", token)
                close_paren = findEnclosingToken(tokens, TokenType.OPEN_PAREN, TokenType.CLOSE_PAREN, i +1)
                if close_paren == None:
                    syntaxError(f"The closing parenthesis for this one is missing!", token)
                value = processValueExpression(tokens[i +1 : close_paren], token)
                buffer.append(Node(NodeType.ORDER_PAREN, value=value))
                i = close_paren +1
            
            elif tokenType == TokenType.OP:
                if len(buffer) != 1 or not producesValue(buffer[0]): # Should have already found a value before
                    if len(buffer) == 0:
                        syntaxError(f"There should be a left-hand side value for this operation `{token}`", token)
                    elif len(buffer) == 1:
                        assert False, f"Buffer has a none value element: {buffer[0]}"
                        # raise Exception(f"SYNTAX ERROR: Can't use this `{buffer[0]}` with this operation `{tokens[i]}`.\n{tokens[i].location()}")
                    else:
                        assert False, f"Buffer has more than one element: {buffer}"
                if len(tokens) <= i +1:
                    syntaxError(f"There should be a right-hand side value for this operation `{token}`", token)
                r_value = None
                if tokens[i +1].type in [TokenType.NUMBER, TokenType.IDENTIFIER]: # TODO separate once we have func_call
                    r_value = tokens[i +1]
                    i += 2
                elif tokens[i +1].type == TokenType.OPEN_PAREN:
                    close_paren = findEnclosingToken(tokens, TokenType.OPEN_PAREN, TokenType.CLOSE_PAREN, i +2)
                    if close_paren == None:
                        syntaxError(f"The closing parenthesis for this one is missing!", tokens[i +1])
                    value = processValueExpression(tokens[i +2 : close_paren], tokens[i +1])
                    r_value = Node(NodeType.ORDER_PAREN, value=value)
                    i = close_paren +1
                else:
                    syntaxError(f"This operation `{token}` requires a value after it, not this `{tokens[i +1]}`", tokens[i +1])
                if type(buffer[0]) == Node and buffer[0].type == NodeType.OP: # If an op is the previous value then append
                    buffer[0] = appendOP(buffer[0], token, r_value)
                else: # Otherwise create one
                    buffer[0] = Node(NodeType.OP, op=token, l_value=buffer[0], r_value=r_value)
            
            elif tokenType == TokenType.EOL:
                i += 1
            
            else:
                syntaxError(f"What is this `{token}` doing here? It shouldn't be there", token)
        if len(buffer) != 1 or not producesValue(buffer[0]):
            if len(buffer) == 0:
                syntaxError(f"Expected some sort of expression after this", parent_token)
            elif len(buffer) == 1:
                assert False, f"Buffer has a none value element: {buffer[0]}"
                # raise Exception(f"SYNTAX ERROR: Can't assign this `{buffer[0]}` to this variable `{token}`.\n{token.location()}")
            else:
                assert False, f"Buffer contains more than 1 element: {buffer}"
        return buffer[0]
    
    ast = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        tokenType = token.type
        
        if tokenType == TokenType.IDENTIFIER: # var_assign
            if len(tokens) <= i +1 or tokens[i +1].type != TokenType.ASSIGN_OP:
                syntaxError(f"There should be an assignment operator after this variable `{token}`\nVariables can't be declared without assigning a value to them", token)
            i += 2
            eol = findToken(tokens, TokenType.EOL, i)
            assert eol != None, f"EOL was not appended to the line of this token: {token}\n{token.location()}"
            open_paren = findToken(tokens[: eol], TokenType.OPEN_PAREN, i)
            if open_paren != None: # If there is a paren, then look for the last EOL
                end_paren = findEnclosingToken(tokens, TokenType.OPEN_PAREN, TokenType.CLOSE_PAREN, open_paren +1)
                if end_paren == None:
                    syntaxError(f"The closing parenthesis for this one is missing!", tokens[open_paren])
                eol = findToken(tokens, TokenType.EOL, end_paren +1)
                assert eol != None, f"EOL was not appended to the line of this token: {token}\n{token.location()}"
            ast.append(Node(NodeType.VAR_ASSIGN, var=token, value=processValueExpression(tokens[i : eol], tokens[i -1])))
            i = eol +1
        
        elif tokenType == TokenType.EOL: # Skip
            i += 1
        
        else:
            syntaxError(f"This `{token}` cannot start a new expression", token)
    
    return ast

def runSourceFile (filePath: str) -> None:
    '''Compiles and runs a source file'''
    content = None
    with open(filePath, 'r') as f:
        content = f.read()
    tokens = parseSourceFile(content, filePath)
    print("Tokens:\n", tokens)
    ast = constructAST(tokens)
    print("AST:\n")
    for node in ast:
        print("-", node)
    
    pass