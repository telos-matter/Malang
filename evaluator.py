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


def preProcess (tokens: list):

    def getNumber (token: str) -> tuple[bool, float]: 
        try:
            return (True, float(token))
        except ValueError:
            return (False, None)

    for i in range(len(tokens)):
        result = getNumber(tokens[i])
        if result[0]:
            tokens[i] = result[1]


def evaluate (input: str) -> float:
    tokens = input.split()

    preProcess(tokens)

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

            elif token == 'sqrt' and validUnaryOperator(tokens, i, True): 
                a = tokens.pop(i +1)
                tokens[i] = math.sqrt(a)
                evaluated = True

            elif isNumber(token) and isSingleNumber(tokens, i):
                tokens.pop(i -1)
                tokens.pop(i)
                evaluated = True
            
            i += 1
        
        if not evaluated:
            if len(tokens) > 2000:
                tokens = tokens[:2000]
            assert False, f'Didn\'t evaluate anything, expression:\n{tokens}..'

    try:
        i = int(tokens[0])
        f = float(tokens[0])
        if i == f:
            return i
        else:
            return f
    except ValueError:
        return float(tokens[0])

# TODO imporve by substuting 0 * (xxxx) with 0

