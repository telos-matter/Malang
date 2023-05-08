import math
import sys

# TODO mention tsoading

def iota () -> int:
    iota.counter += 1
    return iota.counter
iota.counter = -1

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

def ADD (a: float, b: float) -> float:
    return a + b

def SUB (a: float, b: float) -> float:
    return a - b

def MUL (a: float, b: float) -> float:
    return a * b

def DIV (a: float, b: float) -> float:
    return a / b

def IDIV (a: float, b: float) -> float:
    return a // b

def POW (a: float, b: float) -> float:
    return a ** b

def SQRT (n: float) -> float:
    return math.sqrt(n)

def LN (n: float) -> float:
    return math.log(n)

def SIN (n: float) -> float:
    return math.sin(n)

def COS (n: float) -> float:
    return math.cos(n)


"""
A program is always a tuple of two things:
1. The op_code
2. A list of the args
Then ofc the individual args can be another program, i.e. another tuple
"""

sys.setrecursionlimit(10_000) # If you are wondering, cuz i was, if the change is global (to all future python instances), no it is not, i tested it

def evaluateOP (op_code: int, args: list) -> float:
    for i, arg in enumerate(args[:]):
        if isinstance(arg, tuple):
            args[i] = evaluateOP(arg[0], arg[1])
    
    if op_code == OP_ADD:
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
