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
                # A line comment
                break
            
            elif char.isspace():
                i += 1
            
            else:
                raise Exception(f"PARSING ERROR: Unexpected char: `{char}`\nFile `{filePath}`, line: {line_index +1}, column: {i +1}")
        
        tokens.append(Token(TokenType.EOL, '\n', filePath, line_index, len(line))) # Fuck Windows' new lines
    
    return tokens


class NodeType (Enum):
    VAR_ASSIGN       = auto()     # Assigning to a variable
    OP               = auto()     # Any operation of the allowed operations from the set of instruction (+, -, *..)

class Node():
    def __init__(self, nodeType: NodeType, **components) -> None:
        ''' The components that each nodeType may have
        VAR_ASSIGN:
            var: an identifier token representing the variable getting assigned to
            value: a value element
        OP:
            op: the op token
            l_value: a value element representing the left value of the operation
            r_value: a value element representing the right value of the operation
        \n
        A value element means a Token or a Node that can return or is a value, it
        can be: Token.number, Token.identifier or Node.op
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
            return element.type in [NodeType.OP]
        else:
            assert False, f"Passed something other than Token or Node, {element}"
    
    def appendOP (root_node: Node, op: Token, r_value: Token) -> Node:
        '''Adds the op to the tree according to their precedence
        and returns the new root node\n
        The process goes as follows:\n
        \tIf its precedence is greater than or equal to mine => It is my left-hand side\n
        \tOtherwise => Im its new right-hand side, and its old right-hand value is my left-hand value\n
        '''
        assert root_node.type == NodeType.OP, f"The root_node is not an op node"
        assert op.type == TokenType.OP, f"The op is not an op token"
        assert type(r_value) == Token and producesValue(r_value), f"Passed a Token that does not produce value"
        
        if OP_SET.fromSymbol(root_node.components['op'].lexeme).precedence >= OP_SET.fromSymbol(op.lexeme).precedence:
            return Node(NodeType.OP, op=op, l_value=root_node, r_value=r_value)
        else:
            root_r_value = root_node.components['r_value']
            new_r_value = None
            if type(root_r_value) == Node and root_r_value.type == NodeType.OP:
                new_r_value = appendOP(root_r_value, op, r_value) # Repeat until its a leaf (a number, function call, variable..)
            else:
                new_r_value = Node(NodeType.OP, op=op, l_value=root_r_value, r_value=r_value)
            root_node.components['r_value'] = new_r_value
            return root_node
    
    ast = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        tokenType = token.type
        
        if tokenType == TokenType.IDENTIFIER: # var_assign
            if len(tokens) <= i +1 or tokens[i +1].type != TokenType.ASSIGN_OP:
                raise Exception(f"SYNTAX ERROR: Expected the assign operation `=` after this variable `{token}`.\nVariables can't be declared without assigning a value to then.\n{token.location()}")
            i += 2
            buffer = [] # After the while loop, it should only contain one element, either a number token or an op node
            while i < len(tokens):
                if tokens[i].type == TokenType.NUMBER:
                    if len(buffer) != 0:
                        raise Exception(f"SYNTAX ERROR: Was not expecting this number here.\n{tokens[i].location()}")
                    buffer.append(tokens[i])
                    i += 1
                elif tokens[i].type == TokenType.IDENTIFIER:
                    if len(buffer) != 0:
                        raise Exception(f"SYNTAX ERROR: Was not expecting this identifier here.\n{tokens[i].location()}")
                    buffer.append(tokens[i])
                    i += 1
                elif tokens[i].type == TokenType.OP:
                    if len(buffer) != 1 or not producesValue(buffer[0]): # Should have already found a value before
                        if len(buffer) == 0:
                            raise Exception(f"SYNTAX ERROR: This operation `{tokens[i]}` requires a left-hand side value.\n{tokens[i].location()}")
                        elif len(buffer) == 1:
                            raise Exception(f"SYNTAX ERROR: Can't use this `{buffer[0]}` with this operation `{tokens[i]}`.\n{tokens[i].location()}")
                        else:
                            assert False, f"Buffer has more than one element: {buffer}"
                    if len(tokens) <= i +1 or not producesValue(tokens[i +1]): # The token after should be a value
                        raise Exception(f"SYNTAX ERROR: Expected a number or an identifier after this operation `{tokens[i]}`.\n{tokens[i].location()}")
                    if type(buffer[0]) == Node and buffer[0].type == NodeType.OP: # If an op is the previous value then append
                        buffer[0] = appendOP(buffer[0], tokens[i], tokens[i +1])
                    else: # Otherwise create one
                        buffer[0] = Node(NodeType.OP, op=tokens[i], l_value=buffer[0], r_value=tokens[i +1])
                    i += 2
                elif tokens[i].type == TokenType.EOL: # Assignment is done
                    break
                else:
                    raise Exception(f"SYNTAX ERROR: Was not expecting this `{tokens[i]}` in this variable assignment `{token}`.\n{tokens[i].location()}")
            if len(buffer) != 1 or not producesValue(buffer[0]):
                if len(buffer) == 0:
                    raise Exception(f"SYNTAX ERROR: Something must be assigned to this variable `{token}`.\n{token.location()}")
                elif len(buffer) == 1:
                    raise Exception(f"SYNTAX ERROR: Can't assign this `{buffer[0]}` to this variable `{token}`.\n{token.location()}")
                else:
                    assert False, f"Buffer contains more than 1 element: {buffer}"
            ast.append(Node(NodeType.VAR_ASSIGN, var=token, value=buffer[0]))
        
        elif tokenType == TokenType.EOL: # Next line
            i += 1
        
        else:
            raise Exception(f"Was not expecting this `{token.lexeme}`!\n{token.location()}")
    
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