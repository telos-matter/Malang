import math

def isNumber (token: str) -> bool: 
    try:
        float(token)
        return True
    except ValueError:
        return False

def getNumber (token) -> float: 
    try:
        if int(token) == float(token):
            return int(token)
        else:
            return float(token)
    except ValueError:
        return float(token)

def validBinaryOperator (tokens: list, index: int) -> bool:
    return isNumber(tokens[index -1]) and isNumber(tokens[index +1])

def validUnaryOperator (tokens: list, index: int, right: bool) -> bool:
    if right:
        return isNumber(tokens[index +1])
    else:
        return isNumber(tokens[index -1])

def isSingleNumber (tokens: list, index: int) -> bool:
    return tokens[index -1] == '(' and tokens[index +1] == ')'


def evaluate (input: str):
    tokens = input.split()

    while len(tokens) > 1:
        for i in range(len(tokens)):
            token = tokens[i]

            if token == '-' and validBinaryOperator(tokens, i):
                a = getNumber(tokens[i -1])
                b = getNumber(tokens[i +1])
                for _ in range(3):
                    tokens.pop(i -1)
                tokens.insert(i -1, a - b)
                break

            elif token == '+' and validBinaryOperator(tokens, i): 
                a = getNumber(tokens[i -1])
                b = getNumber(tokens[i +1])
                for _ in range(3):
                    tokens.pop(i -1)
                tokens.insert(i -1, a + b)
                break

            elif token == '*' and validBinaryOperator(tokens, i): 
                a = getNumber(tokens[i -1])
                b = getNumber(tokens[i +1])
                for _ in range(3):
                    tokens.pop(i -1)
                tokens.insert(i -1, a * b)
                break

            elif token == '/' and validBinaryOperator(tokens, i): 
                a = getNumber(tokens[i -1])
                b = getNumber(tokens[i +1])
                for _ in range(3):
                    tokens.pop(i -1)
                
                tokens.insert(i -1, getNumber(a / b))
                break

            elif token == '^' and validBinaryOperator(tokens, i): 
                a = getNumber(tokens[i -1])
                b = getNumber(tokens[i +1])
                for _ in range(3):
                    tokens.pop(i -1)
                tokens.insert(i -1, a ** b)
                break

            elif token == '!=' and validBinaryOperator(tokens, i): 
                a = getNumber(tokens[i -1])
                b = getNumber(tokens[i +1])
                for _ in range(3):
                    tokens.pop(i -1)
                tokens.insert(i -1, int(a != b))
                break

            elif token == 'sqrt' and validUnaryOperator(tokens, i, True): 
                a = getNumber(tokens[i +1])
                for _ in range(2):
                    tokens.pop(i)
                tokens.insert(i, getNumber(math.sqrt(a)))
                break

            elif isNumber(token) and isSingleNumber(tokens, i):
                for _ in range(3):
                    tokens.pop(i -1)
                tokens.insert(i -1, token)
                break

    print(tokens[0])
