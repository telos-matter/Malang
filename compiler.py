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
    def __init__(self, tokenType: TokenType, lexeme: str | float, file_path: str, line_index: int, char_index: int) -> None:
        self.type = tokenType
        self.lexeme = lexeme
        self.file = file_path
        self.line = line_index +1
        self.char = char_index +1
    
    def location(self) -> str:
        return f"File `{self.file}`, line: {self.line}, column: {self.char}"
    
    def __repr__(self) -> str:
        return str(self.lexeme)

def parseSourceFile (content: str, filePath: str) -> list[Token]:
    '''Takes a source file and parses its content to tokens
    Does not check for structure validity,
    only checks for content correctness'''
    
    NUMBER_PERIOD = '.'
    tokens = []
    
    for line_index, line in enumerate(content.splitlines()):
        i = 0
        while i < len(line):
            char = line[i]
            
            if char in OP_SET.getSymbols():
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
                    raise Exception(f"PARSING ERROR: Couldn't parse this number: `{number}`\nFile `{filePath}`, line: {line_index +1}, column: {i +1}")
                tokens.append(Token(TokenType.NUMBER, number, filePath, line_index, i))
                i = j
            
            elif char == '(':
                tokens.append(Token(TokenType.OPEN_PAREN, char, filePath, line_index, i))
                i += 1
            
            elif char == ')':
                tokens.append(Token(TokenType.CLOSE_PAREN, char, filePath, line_index, i))
                i += 1
            
            elif char == '_' or char.isalpha():
                identifier = char
                j = i +1
                while j < len(line) and (line[j].isalpha() or line[j].isdigit() or line[j] == '_'):
                    identifier += line[j]
                    j += 1
                tokens.append(Token(TokenType.IDENTIFIER, identifier, filePath, line_index, i))
                i = j
            
            elif char == '=':
                tokens.append(Token(TokenType.ASSIGN_OP, char, filePath, line_index, i))
                i += 1
            
            elif char == '#':
                # A line comment, go to next line
                break
            
            elif char.isspace():
                i += 1
            
            else:
                raise Exception(f"PARSING ERROR: Unexpected char: `{char}`\nFile `{filePath}`, line: {line_index +1}, column: {i +1}")
        
        tokens.append(Token(TokenType.EOL, '\n', filePath, line_index, len(line))) # Fuck Windows' new lines
    
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
                    raise Exception(f"SYNTAX ERROR: Was not expecting a number here.\n{token.location()}")
                buffer.append(token)
                i += 1
            
            elif tokenType == TokenType.IDENTIFIER:
                if len(buffer) != 0:
                    raise Exception(f"SYNTAX ERROR: Was not expecting an identifier here.\n{token.location()}")
                buffer.append(token)
                i += 1
            
            elif tokenType == TokenType.OPEN_PAREN:
                if len(buffer) != 0:
                    raise Exception(f"SYNTAX ERROR: Was not expecting an open parenthesis here.\n{token.location()}")
                close_paren = findEnclosingToken(tokens, TokenType.OPEN_PAREN, TokenType.CLOSE_PAREN, i +1)
                if close_paren == None:
                    raise Exception(f"SYNTAX ERROR: The closing parenthesis is missing.\n{token.location()}")
                value = processValueExpression(tokens[i +1 : close_paren], token)
                buffer.append(Node(NodeType.ORDER_PAREN, value=value))
                i = close_paren +1
            
            elif tokenType == TokenType.OP:
                if len(buffer) != 1 or not producesValue(buffer[0]): # Should have already found a value before
                    if len(buffer) == 0:
                        raise Exception(f"SYNTAX ERROR: This operation `{token}` requires a left-hand side value.\n{token.location()}")
                    elif len(buffer) == 1:
                        assert False, f"Buffer has a none value element: {buffer[0]}"
                        # raise Exception(f"SYNTAX ERROR: Can't use this `{buffer[0]}` with this operation `{tokens[i]}`.\n{tokens[i].location()}")
                    else:
                        assert False, f"Buffer has more than one element: {buffer}"
                if len(tokens) <= i +1:
                    raise Exception(f"SYNTAX ERROR: Expected something after this operation `{token}`.\n{token.location()}")
                r_value = None
                if tokens[i +1].type in [TokenType.NUMBER, TokenType.IDENTIFIER]: # TODO separate once we have func_call
                    r_value = tokens[i +1]
                    i += 2
                elif tokens[i +1].type == TokenType.OPEN_PAREN:
                    close_paren = findEnclosingToken(tokens, TokenType.OPEN_PAREN, TokenType.CLOSE_PAREN, i +2)
                    if close_paren == None:
                        raise Exception(f"SYNTAX ERROR: The closing parenthesis is missing.\n{token.location()}")
                    value = processValueExpression(tokens[i +2 : close_paren], tokens[i +1])
                    r_value = Node(NodeType.ORDER_PAREN, value=value)
                    i = close_paren +1
                else:
                    raise Exception(f"SYNTAX ERROR: Was not expecting this after this operation `{token}`.\n{token.location()}")
                if type(buffer[0]) == Node and buffer[0].type == NodeType.OP: # If an op is the previous value then append
                    buffer[0] = appendOP(buffer[0], token, r_value)
                else: # Otherwise create one
                    buffer[0] = Node(NodeType.OP, op=token, l_value=buffer[0], r_value=r_value)
            
            elif tokenType == TokenType.EOL:
                i += 1
            
            else:
                raise Exception(f"SYNTAX ERROR: Was not expecting this `{tokens[i]}` here.\n{tokens[i].location()}")
        if len(buffer) != 1 or not producesValue(buffer[0]):
            if len(buffer) == 0:
                raise Exception(f"SYNTAX ERROR: Expected something after this `{parent_token}`.\n{parent_token.location()}")
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
                raise Exception(f"SYNTAX ERROR: Expected the assign operation `=` after this variable `{token}`.\nVariables can't be declared without assigning a value to then.\n{token.location()}")
            i += 2
            eol = findToken(tokens, TokenType.EOL, i)
            assert eol != None, f"EOL was not appended to the line of this token: {token}\n{token.location()}"
            open_paren = findToken(tokens[: eol], TokenType.OPEN_PAREN, i)
            if open_paren != None: # If there is a paren, then look for the last EOL
                end_paren = findEnclosingToken(tokens, TokenType.OPEN_PAREN, TokenType.CLOSE_PAREN, open_paren +1)
                if end_paren == None:
                    raise Exception(f"SYNTAX ERROR: The closing parenthesis is missing.\n{tokens[open_paren].location()}")
                eol = findToken(tokens, TokenType.EOL, end_paren +1)
                assert eol != None, f"EOL was not appended to the line of this token: {token}\n{token.location()}"
            ast.append(Node(NodeType.VAR_ASSIGN, var=token, value=processValueExpression(tokens[i : eol], tokens[i -1])))
            i = eol +1
        
        elif tokenType == TokenType.EOL: # Skip
            i += 1
        # TODO add support in processValue for open paren
        
        else:
            raise Exception(f"This `{token}` shouldn't be here here!\n{token.location()}")
    
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