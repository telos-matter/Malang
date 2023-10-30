from enum import Enum, auto
from core import OP_SET, Instruction
from numbers import Number

class TokenType (Enum):
    NUMBER      = auto() # Any number
    OP          = auto() # Any operation of the allowed operations from the set of instruction (+, -, *..)
    EOL         = auto() # End of a line (Could also be an EOF)
    OPEN_PAREN  = auto() # Opening parenthesis `(`
    CLOSE_PAREN = auto() # Closing parenthesis `)`
    IDENTIFIER  = auto() # Any identifier; variable, function name ext.. Can only have letters, `_` and numbers but can only start with the first two; _fOo10
    ASSIGN_OP   = auto() # The assigning operation, `=`
    DEF_KW      = auto() # The `def` keyword to declare functions
    OPEN_CURLY  = auto() # Opening curly brackets `{`
    CLOSE_CURLY = auto() # Closing curly brackets `}`
    COMMA       = auto() # The `,` that separates the params and args

class Token ():
    def __init__(self, tokenType: TokenType, lexeme: str | Number, line: str, span: int, file_path: str, line_index: int, char_index: int, synthesized: bool=False) -> None:
        '''`line`: the line in which this Token exists\n
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
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.type == other.type and self.lexeme == other.lexeme
        else:
            return False
    
    def __hash__(self) -> int:
        return hash((self.type, self.lexeme))
    
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
                if char == OP_SET.IDIV.symbol[0] and i +1 < len(line) and line[i +1] == OP_SET.IDIV.symbol[1]:
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
            
            elif char == '_' or char.isalpha(): # Identifier or keyword
                identifier = char
                j = i +1
                while j < len(line) and (line[j].isalpha() or line[j].isdigit() or line[j] == '_'):
                    identifier += line[j]
                    j += 1
                if identifier == 'def':
                    tokens.append(Token(TokenType.DEF_KW, identifier, line, j -i, filePath, line_index, i))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, identifier, line, j -i, filePath, line_index, i))
                i = j
            
            elif char == '{':
                tokens.append(Token(TokenType.OPEN_CURLY, char, line, len(char), filePath, line_index, i))
                i += 1
            
            elif char == '}':
                tokens.append(Token(TokenType.CLOSE_CURLY, char, line, len(char), filePath, line_index, i))
                i += 1
            
            elif char == '=':
                tokens.append(Token(TokenType.ASSIGN_OP, char, line, len(char), filePath, line_index, i))
                i += 1
            
            elif char == ',':
                tokens.append(Token(TokenType.COMMA, char, line, len(char), filePath, line_index, i))
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
    FUNC_DEF    = auto() # Function definition. Can have nested functions. Functions overloading is allowed
    FUNC_CALL   = auto() # Function call

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
        `FUNC_DEF`:
            params: a list of identifier tokens representing the parameters
            body: a list of nodes representing the body of the function. It
            can contain any other node, including another Node.FUNC_DEF
        `FUNC_CALL`:
            func: an identifier token representing the function being called
            args: a list of value elements representing the arguments
        \n
        A value element means a Token or a Node that can return or is a value, one
        fo these: Token.NUMBER, Token.IDENTIFIER, Node.OP, Node.ORDER_PAREN or
        Node.FUNC_CALL
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
            return element.type in [NodeType.OP, NodeType.ORDER_PAREN, NodeType.FUNC_CALL]
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
    
    def findEnclosingToken (tokens: list[Token], opening_tokenType: TokenType, enclosing_tokenType: TokenType, search_from: int, required: Token=None) -> int | None:
        '''Returns the index of the enclosing token starting from `search_from`
        This handles nested tokens such as ((())) for example\n
        `required` should have the opening token
        if you want this function to raise a SyntaxError if 
        the closing element was not found'''
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
            syntaxError(f"The closing element for this one is missing.", required)
        return None
    
    def isNextToken (tokens: list[Token], tokenType: TokenType, start_from: int) -> int | None:
        '''Checks if the token, from `start_from`, is `tokenType`, while skipping over
        Token.EOLs. If it is return its index, otherwise None'''
        while start_from < len(tokens):
            if tokens[start_from].type == tokenType:
                return start_from
            elif tokens[start_from].type == TokenType.EOL:
                start_from += 1
            else:
                return None
        return None
    
    def processValueExpression (tokens: list[Token], parent_token_index: int, skip_eols: bool) -> tuple[Node | Token, int]:
        '''Called to process a value expression and return a value element representing it\n
        It would for example process whatever is in between parenthesis,
        function args or a variable assignment. And returns where to continue\n
        It process/parses whatever
        it has as long as it can be in a single value expression\n
        `tokens` is the list of the actual tokens\n
        `parent_token_index` is the index
        of token that wants to process this value expression, we
        start right after it\n
        `skip_eols` tells it whether it should halt if it encounters
        a new line (useful when the ones who wants to process are
        parenthesis)'''
        
        def negateValue(tokens: list[Token], negate_token_index: int) -> tuple[Token | Node, int]:
            '''Negates the value element after the negate token
            at `negate_token_index`. Returns the negated value element and
            the index at which to continue'''
            i = negate_token_index # Ease of reference
            assert tokens[i].type == TokenType.OP and tokens[i].lexeme == OP_SET.SUB.symbol, f"Passed something other than -"
            
            token = tokens[i]
            value = None
            if len(tokens) <= i +1:
                syntaxError(f"Expected a value to negate after this", token)
            if tokens[i +1].type == TokenType.NUMBER:
                tokens[i +1].lexeme *= -1
                value = tokens[i +1]
                i += 2
            elif tokens[i +1].type in [TokenType.IDENTIFIER, TokenType.OPEN_PAREN]:
                negation_r_value = None
                if tokens[i +1].type == TokenType.IDENTIFIER: # A variable or Node.FUNC_CALL
                    if i +2 < len(tokens) and tokens[i +2].type == TokenType.OPEN_PAREN: # Node.FUNC_CALL
                        negation_r_value, i = processFuncCall(tokens, tokens[i +1], i +2)
                    else: # A variable
                        negation_r_value = tokens[i +1]
                        i += 2
                elif tokens[i +1].type == TokenType.OPEN_PAREN:
                    negation_r_value, i = processParen(tokens, i +1)
                else:
                    assert False, f"Unreachable"
                negation_op = Token(TokenType.OP, OP_SET.MUL.symbol, *token.getSynthesizedInfo())
                negation_l_value = Token(TokenType.NUMBER, -1, *token.getSynthesizedInfo())
                negation = Node(NodeType.OP, op=negation_op, l_value=negation_l_value, r_value=negation_r_value)
                value = Node(NodeType.ORDER_PAREN, value=negation)
            else:
                syntaxError(f"Can't negate something other than a value", tokens[i +1])
            return (value, i)
        
        def processParen(tokens: list[tokens], open_paren: int) -> tuple[Node, int]:
            '''Process just the parenthesis and stops\n
            Returns a Node.ORDER_PAREN and the index at which to continue'''
            assert tokens[open_paren].type == TokenType.OPEN_PAREN, f"Passed something other open_paren: {tokens[open_paren]}"
            close_paren = findEnclosingToken(tokens, TokenType.OPEN_PAREN, TokenType.CLOSE_PAREN, open_paren +1)
            if close_paren == None:
                syntaxError(f"The closing parenthesis for this one is missing!", tokens[open_paren])
            value, _ = processValueExpression(tokens[open_paren : close_paren], 0, True)
            node = Node(NodeType.ORDER_PAREN, value=value)
            return (node, close_paren +1)
        
        buffer = []
        i = parent_token_index +1
        while i < len(tokens):
            token = tokens[i]
            tokenType = token.type
            
            if tokenType == TokenType.NUMBER:
                if len(buffer) != 0:
                    syntaxError(f"The number `{token}` can't be here! Expected an operation.", token)
                buffer.append(token)
                i += 1
            
            elif tokenType == TokenType.IDENTIFIER: # A variable or a Node.FUNC_CALL
                if len(buffer) != 0:
                    syntaxError(f"The variable `{token}` can't be here! Expected an operation", token)
                if i +1 < len(tokens) and tokens[i +1].type == TokenType.OPEN_PAREN: # Node.FUNC_CALL
                    func_call, i = processFuncCall(tokens, token, i +1)
                    buffer.append(func_call)
                
                else: # A variable
                    buffer.append(token)
                    i += 1
            
            elif tokenType == TokenType.OPEN_PAREN:
                if len(buffer) != 0:
                    syntaxError(f"This open parenthesis `{token}` can't be here! Expected an operation", token)
                node, i = processParen(tokens, i)
                buffer.append(node)
            
            elif tokenType == TokenType.OP:
                if len(buffer) == 0 and token.lexeme == OP_SET.SUB.symbol:
                    value, i = negateValue(tokens, i)
                    buffer.append(value)
                    continue
                
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
                if tokens[i +1].type == TokenType.NUMBER:
                    r_value = tokens[i +1]
                    i += 2
                elif tokens[i +1].type == TokenType.IDENTIFIER: # A variable or a Node.FUNC_CALL
                    if i +2 < len(tokens) and tokens[i +2].type == TokenType.OPEN_PAREN: # Node.FUNC_CALL
                        r_value, i = processFuncCall(tokens, tokens[i +1], i +2)
                    else: # A variable
                        r_value = tokens[i +1]
                        i += 2
                elif tokens[i +1].type == TokenType.OPEN_PAREN:
                    r_value, i = processParen(tokens, i +1)
                elif tokens[i +1].type == TokenType.OP and tokens[i +1].lexeme == OP_SET.SUB.symbol:
                    r_value, i = negateValue(tokens, i +1)
                else:
                    syntaxError(f"This operation `{token}` requires a value after it, not this `{tokens[i +1]}`", tokens[i +1])
                if type(buffer[0]) == Node and buffer[0].type == NodeType.OP: # If an op is the previous value then append
                    buffer[0] = appendOP(buffer[0], token, r_value)
                else: # Otherwise create one
                    buffer[0] = Node(NodeType.OP, op=token, l_value=buffer[0], r_value=r_value)
            
            elif tokenType == TokenType.EOL:
                assert skip_eols is not None, f"Who gave you None?"
                if skip_eols:
                    i += 1
                else:
                    break
            
            elif tokenType == TokenType.COMMA: # End of arg for Node.FUNC_CALL
                break
            
            elif tokenType == TokenType.CLOSE_PAREN:
                syntaxError(f"You forgot the opening parenthesis for this one", token)
            
            else:
                syntaxError(f"What is this `{token}` doing here? (- In Hector Salamancas' voice) It shouldn't be there", token)
        
        if len(buffer) != 1 or not producesValue(buffer[0]):
            if len(buffer) == 0:
                syntaxError(f"Expected some sort of expression after this", tokens[parent_token_index])
            elif len(buffer) == 1:
                assert False, f"Buffer has a none value element: {buffer[0]}"
                # raise Exception(f"SYNTAX ERROR: Can't assign this `{buffer[0]}` to this variable `{token}`.\n{token.location()}")
            else:
                assert False, f"Buffer contains more than 1 element: {buffer}"
        return (buffer[0], i)
    
    def processFuncCall (tokens: list[Token], func: Token, open_paren_index: int) -> tuple[Node, int]:
        '''Processes a function call and returns a Node.FUNC_CALL
        and the index at which to continue, which is where the function
        call ends +1'''
        i = open_paren_index # Ease of reference
        assert func.type == TokenType.IDENTIFIER, f"Not Token.IDENTIFIER"
        assert tokens[i].type == TokenType.OPEN_PAREN, f"Not Token.OPEN_PAREN"
        
        close_paren = findEnclosingToken(tokens, TokenType.OPEN_PAREN, TokenType.CLOSE_PAREN, i +1, tokens[i])
        args = []
        if isNextToken(tokens, TokenType.CLOSE_PAREN, i +1) is None: # If it has some args
            args_tokens = tokens[i : close_paren]
            inc = 0
            while i +inc < close_paren:
                arg, inc = processValueExpression(args_tokens, inc, True)
                if i +inc < close_paren:
                    assert tokens[i +inc].type == TokenType.COMMA, f"Not sure if this should be an assert or Syntax Error" # I think rn it should be assert, cuz the only thing that should exit it is the comma
                args.append(arg)
        return (Node(NodeType.FUNC_CALL, func=func, args=args), close_paren +1)
    
    ast = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        tokenType = token.type
        
        if tokenType == TokenType.IDENTIFIER: # Node.VAR_ASSIGN or Node.FUNC_CALL
            if len(tokens) <= i +1:
                syntaxError(f"Expected something after this identifier", token)
            i += 1
            if tokens[i].type == TokenType.ASSIGN_OP: # Node.VAR_ASSIGN
                value, i = processValueExpression(tokens, i, False)
                ast.append(Node(NodeType.VAR_ASSIGN, var=token, value=value))
            
            elif tokens[i].type == TokenType.OPEN_PAREN: # Node.FUNC_CALL
                func_call, i = processFuncCall(tokens, token, i)
                ast.append(func_call)
            
            else:
                syntaxError(f"Was not expecting this after an identifier", tokens[i])
        
        elif tokenType == TokenType.DEF_KW: # Node.FUNC_DEF:
            i += 1
            if len(tokens) <= i or tokens[i].type != TokenType.IDENTIFIER:
                syntaxError(f"There should be an identifier representing the name of the function being defined right after the `{token}` keyword", token)
            i += 1
            if len(tokens) <= i or tokens[i].type != TokenType.OPEN_PAREN:
                syntaxError(f"There should be an open parenthesis right after the function's name that starts the definition of this function parameters", tokens[i])
            i += 1
            close_paren = findEnclosingToken(tokens, TokenType.OPEN_PAREN, TokenType.CLOSE_PAREN, i)
            if close_paren == None:
                syntaxError(f"The closing parenthesis for the function's parameters is missing", tokens[i +2])
            params = []
            last_thing_was_comma = True
            while i < close_paren:
                if tokens[i].type == TokenType.EOL:
                    i += 1
                elif tokens[i].type == TokenType.COMMA:
                    if last_thing_was_comma:
                        if len(params) == 0:
                            syntaxError(f"Expected a parameter's name to start with, not a comma", tokens[i])
                        else:
                            syntaxError(f"Two consecutive commas", tokens[i])
                    else:
                        last_thing_was_comma = True
                        i += 1
                elif tokens[i].type == TokenType.IDENTIFIER:
                    if last_thing_was_comma:
                        params.append(tokens[i])
                        last_thing_was_comma = False
                        i += 1
                    else:
                        syntaxError(f"Two consecutive parameters", tokens[i])
                else:
                    if last_thing_was_comma:
                        syntaxError(f"Expected an identifier representing the name of a parameter, not this.", tokens[i])
                    else:
                        syntaxError(f"Expected a comma to separate the parameters, not this.", tokens[i])
            if len(params) != 0 and last_thing_was_comma:
                syntaxError(f"There is an extra comma before this closing parenthesis, remove it", tokens[i])
            open_curly = isNextToken(tokens, TokenType.OPEN_CURLY, i +1)
            if open_curly is None:
                syntaxError(f"Couldn't find an open curly bracket to start the body of the function after this", tokens[i])
            close_curly = findEnclosingToken(tokens, TokenType.OPEN_CURLY, TokenType.CLOSE_CURLY, open_curly +1)
            if close_curly is None:
                syntaxError(f"This open curly bracket is missing its closing one", tokens[open_curly])
            body = constructAST(tokens[open_curly +1 : close_curly])
            ast.append(Node(NodeType.FUNC_DEF, params=params, body=body))
            i = close_curly +1
        
        elif tokenType == TokenType.EOL: # Skip
            i += 1
        
        else:
            syntaxError(f"This `{token}` cannot start a new expression", token)
    
    return ast


RETURN_VAR_NAME = 'res'

def validateAST (ast: list[Node]) -> None:
    '''Checks for the validity of the code; referencing
    a none existing variable and so on'''
    
    def invalidCode (message: str, token: Token) -> None:
        '''Raises an invalid code exception'''
        message = "INVALID CODE: " +message
        if token is not None:
            message += f"\n{token.pointOut()}\n{token.location()}"
        raise Exception(message)
    
    def getUsedVars (node: Node) -> set[Token]:
        '''Returns a list of Token.IDENTIFIER representing
        the variables USED BY this node. And NOT the
        variable it self in case of Node.VAR_ASSIGN for example'''
        # TODO recheck this to optimize
        
        if node.type == NodeType.VAR_ASSIGN:
            value = node.components['value']
            if type(value) == Token and value.type == TokenType.IDENTIFIER:
                return {value}
            elif type(value) == Node and value.type in [NodeType.OP, NodeType.ORDER_PAREN]:
                return getUsedVars(value)
        
        elif node.type == NodeType.OP:
            vars = set()
            l_value = node.components['l_value']
            if type(l_value) == Token and l_value.type == TokenType.IDENTIFIER:
                vars.add(l_value)
            elif type(l_value) == Node and l_value.type in [NodeType.OP, NodeType.ORDER_PAREN]:
                vars |= getUsedVars(l_value)
            r_value = node.components['r_value']
            if type(r_value) == Token and r_value.type == TokenType.IDENTIFIER:
                vars.add(r_value)
            elif type(r_value) == Node and r_value.type in [NodeType.OP, NodeType.ORDER_PAREN]:
                vars |= getUsedVars(r_value)
            return vars
        
        elif node.type == NodeType.ORDER_PAREN:
            value = node.components['value']
            if type(value) == Token and value.type == TokenType.IDENTIFIER:
                return {value}
            elif type(value) == Node and value.type in [NodeType.OP, NodeType.ORDER_PAREN]:
                return getUsedVars(value)
        
        else:
            assert False, f"You forgot to update this"
        return set()
    
    vars = {Token(TokenType.IDENTIFIER, RETURN_VAR_NAME, '', 0, None, 0, 0)} # TODO maybe later on appoint it to the start line either of the function or the file
    for node in ast:
        if node.type == NodeType.VAR_ASSIGN:
            used_vars = getUsedVars(node)
            if not used_vars.issubset(vars):
                var = next(iter(used_vars.difference(vars)))
                invalidCode(f"This variable `{var}` was referenced before assignment", var)
            vars.add(node.components['var'])
        
        else:
            assert False, f"Something other than Node.VAR_ASSIGN"


def constructProgram (ast: list[Node]) -> Instruction:
    '''Constructs the program from a valid AST, translates
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


def runSourceFile (filePath: str) -> None:
    '''Compiles and runs a source file'''
    
    DEBUG = True
    
    content = None
    with open(filePath, 'r') as f:
        content = f.read()
    
    tokens = parseSourceFile(content, filePath)
    if DEBUG:
        print("Tokens:\n", tokens)
    
    ast = constructAST(tokens)
    if DEBUG:
        print("AST:\n")
        for node in ast:
            print("-", node)
    
    validateAST(ast)
    if DEBUG:
        print('AST is valid')
    
    program = constructProgram(ast)
    if DEBUG:
        print("Program:", program, sep='\n')
    
    program.runProgram()