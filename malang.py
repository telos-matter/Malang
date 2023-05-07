import math
from functools import cache

def iota ():
    iota.counter += 1
    return iota.counter
iota.counter = -1

OP_DIFFZERO = iota()
OP_ADD = iota()
OP_SUB = iota()
OP_MUL = iota()
OP_DIV = iota()
OP_IDIV = iota()
OP_POW = iota()
OP_SQRT = iota()
OP_LN = iota()
OP_SIN = iota()
OP_COS = iota()
OP_COUNT = iota() # Not using it really

def DIFFZERO (n):
    return int(n != 0)

def ADD (a, b):
    return a + b

def SUB (a, b):
    return a - b

def MUL (a, b):
    return a * b

def DIV (a, b):
    return a / b

def IDIV (a, b):
    return a // b

def POW (a, b):
    return a ** b

def SQRT (n):
    return math.sqrt(n)

def LN (n):
    return math.log(n)

def SIN (n):
    return math.sin(n)

def COS (n):
    return math.cos(n)


"""
Always a tuple of the OP_CODE, and the list of ARGS
Then ofc the individual args can be another tuple
"""

# @cache
def evaluateOP (op_code: int, args: list) -> float:
    for i, arg in enumerate(args[:]):
        if isinstance(arg, tuple):
            args[i] = evaluateOP(arg[0], arg[1])
    
    if op_code == OP_DIFFZERO:
        n = args[0]
        return DIFFZERO(n)
    
    elif op_code == OP_ADD:
        a, b = args
        return ADD(a, b)
    
    elif op_code == OP_SUB:
        a, b = args
        return SUB(a, b)
    
    elif op_code == OP_MUL:
        a, b = args
        return MUL(a, b)
    
    elif op_code == OP_DIV:
        a, b = args
        return DIV(a, b)
    
    elif op_code == OP_IDIV:
        a, b = args
        return IDIV(a, b)
    
    elif op_code == OP_POW:
        a, b = args
        return POW(a, b)
    
    elif op_code == OP_SQRT:
        n = args[0]
        return SQRT(n)
    
    elif op_code == OP_LN:
        n = args[0]
        return LN(n)
    
    elif op_code == OP_SIN:
        n = args[0]
        return SIN(n)
    
    elif op_code == OP_COS:
        n = args[0]
        return COS(n)
    
    else:
        raise Exception(f"Unknown OP: {op_code}, with args: {args}")

# program = (OP_ADD, [(OP_ADD, [10, 10]), 20])
# out = evaluateOP(program[0], program[1])
# print(out)


# TODO: Add factorial, combination and other probability useful stuff
# TODO: How about a rand function?
