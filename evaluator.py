import math

def isNumber (token: any) -> bool: 
    return type(token) == float

def validBinaryOperator (tokens: list, index: int) -> bool:
    return isNumber(tokens[index -1]) and isNumber(tokens[index +1])

def validUnaryOperator (tokens: list, index: int, right: bool) -> bool:
    if right:
        return isNumber(tokens[index +1])
    else:
        return isNumber(tokens[index -1])

def isSingleNumber (tokens: list, index: int) -> bool:
    return tokens[index -1] == '(' and tokens[index +1] == ')'

def findClosingParenthesis (tokens: list, index: int) -> int:
    count = 1
    index += 1
    while index < len(tokens):
        token = tokens[index]
        if token == '(':
            count += 1
        elif token == ')':
            count -= 1
        if count == 0:
            return index
        index += 1
    assert False, f'Found no closing parenthesis {tokens}'

def findOpeningParenthesis (tokens: list, index: int) -> int:
    count = 1
    index -= 1
    while index >= 0:
        token = tokens[index]
        if token == ')':
            count += 1
        elif token == '(':
            count -= 1
        if count == 0:
            return index
        index -= 1
    assert False, f'Found no opening parenthesis {tokens}'

def preprocess (tokens: list):
    
    def getNumber (token: str) -> tuple[bool, float]:
        try:
            return (True, float(token))
        except ValueError:
            return (False, None)
    
    for i in range(len(tokens)):
        result = getNumber(tokens[i])
        if result[0]:
            tokens[i] = result[1]

def substituteZeros (tokens: list) -> list:
    i = 0
    while i +4 < len(tokens):
        token = tokens[i]
        if token == 0 and tokens[i +1] == '*' and tokens[i +2] == '(':
            closingParenthesis = findClosingParenthesis(tokens, i +2)
            tokens = tokens[: i +1] + tokens[closingParenthesis +1 :]
        i += 1
    
    i = len(tokens) -1
    while i -4 >= 0:
        token = tokens[i]
        if token == 0 and tokens[i -1] == '*' and tokens[i -2] == ')':
            openingParenthesis = findOpeningParenthesis(tokens, i -2)
            tokens = tokens[: openingParenthesis] + tokens[i :]
            i -= i - openingParenthesis
        i -= 1

    return tokens

def evaluate (input: str) -> float:
    tokens = input.split()

    preprocess(tokens)

    tokens = substituteZeros(tokens)

    while len(tokens) > 1:
        i = 0
        evaluated = False
        
        while i < len(tokens):
            token = tokens[i]
            
            if token == '-' and validBinaryOperator(tokens, i):
                a = tokens.pop(i -1)
                b = tokens.pop(i)
                tokens[i -1] = (a - b)
                evaluated = True
            
            elif token == '+' and validBinaryOperator(tokens, i): 
                a = tokens.pop(i -1)
                b = tokens.pop(i)
                tokens[i -1] = (a + b)
                evaluated = True
            
            elif token == '*' and validBinaryOperator(tokens, i): 
                a = tokens.pop(i -1)
                b = tokens.pop(i)
                tokens[i -1] = (a * b)
                evaluated = True
            
            elif token == '/' and validBinaryOperator(tokens, i): 
                a = tokens.pop(i -1)
                b = tokens.pop(i)
                tokens[i -1] = (a / b)
                evaluated = True
            
            elif token == '^' and validBinaryOperator(tokens, i): 
                a = tokens.pop(i -1)
                b = tokens.pop(i)
                tokens[i -1] = (a ** b)
                evaluated = True
            
            elif token == '!=' and validBinaryOperator(tokens, i): 
                a = tokens.pop(i -1)
                b = tokens.pop(i)
                tokens[i -1] = float(a != b)
                evaluated = True
            
            elif token == '//' and validBinaryOperator(tokens, i):
                a = tokens.pop(i -1)
                b = tokens.pop(i)
                tokens[i -1] = a // b
                evaluated = True
            
            elif token == '%' and validBinaryOperator(tokens, i):
                a = tokens.pop(i -1)
                b = tokens.pop(i)
                tokens[i -1] = a % b
                evaluated = True
            
            elif token == 'sqrt' and validUnaryOperator(tokens, i, True): 
                a = tokens.pop(i +1)
                tokens[i] = math.sqrt(a)
                evaluated = True
            
            elif token == 'sin' and validUnaryOperator(tokens, i, True): 
                a = tokens.pop(i +1)
                tokens[i] = math.sin(a)
                evaluated = True
            
            elif token == 'cos' and validUnaryOperator(tokens, i, True): 
                a = tokens.pop(i +1)
                tokens[i] = math.cos(a)
                evaluated = True
            
            elif token == 'tan' and validUnaryOperator(tokens, i, True): 
                a = tokens.pop(i +1)
                tokens[i] = math.tan(a)
                evaluated = True
            
            elif token == 'ln' and validUnaryOperator(tokens, i, True): 
                a = tokens.pop(i +1)
                tokens[i] = math.log(a)
                evaluated = True
            
            elif token == 'abs' and validUnaryOperator(tokens, i, True): 
                a = tokens.pop(i +1)
                tokens[i] = abs(a)
                evaluated = True
            
            elif isNumber(token) and isSingleNumber(tokens, i):
                tokens.pop(i -1)
                tokens.pop(i)
                evaluated = True
            
            i += 1
        
        if not evaluated:
            if len(tokens) > 2000:
                tokens = tokens[:2000]
            assert False, f'Didn\'t evaluate a thing, expression:\n{tokens}'
    
    try:
        i = int(tokens[0])
        f = float(tokens[0])
        if i == f:
            return i
        else:
            return f
    except ValueError:
        return tokens[0]

# TODO: Improve by finding repeating sequences and computing them once
