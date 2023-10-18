'''The core file
It has the possible instructions
And it is what runs and evaluates programmes'''

import math
import sys

def iota (reset: bool= False) -> int:
    """Defines constants"""
    if reset:
        iota.counter = -1
    iota.counter += 1
    return iota.counter
iota.counter = -1

# The allowed operations, the instructions set:
OP_ADD  = iota(True) # Addition, +
OP_SUB  = iota() # Subtraction, -
OP_MUL  = iota() # Multiplication, *
OP_DIV  = iota() # Division, /
OP_IDIV = iota() # Integer division, //. Example: 5//2 = 2
OP_POW  = iota() # Exponentiation or raising to the power, ^
OP_SQRT = iota() # Square root (Can be expressed in terms of exponentiation, but its fine by me to have it), sqrt(2)
OP_LN   = iota() # Natural log, ln(2)
OP_SIN  = iota() # Sine, sin(0)
OP_COS  = iota() # Cosine, cos(0)

# The functions that preform the operations:
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


# If you are wondering, because i was, if the change is global (to all future python instances), no it is not, i tested it
sys.setrecursionlimit(10_000)


"""
A program is always a TUPLE of two things:
    1. The op_code
    2. A LIST of the args needed by that operation

Then of course an individual arg can be another program, i.e. another tuple
"""

def evaluateOP (op_code: int, args: list) -> float:
    for i, arg in enumerate(args[:]): # First compute the args
        if isinstance(arg, tuple):
            args[i] = evaluateOP(arg[0], arg[1])
    
    # Then preform the op
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
        raise Exception(f"Unknown OP: `{op_code}`, with args: `{args}`")