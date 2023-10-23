'''The core file
It has the possible instructions
And it is what runs and evaluates programmes'''

from enum import Enum

class OP_SET (Enum):
#   OP_NAME = (REPR, PRECEDENCE)
    OP_ADD  = ('+' , 1)  # Addition
    OP_SUB  = ('-' , 1)  # Subtraction
    OP_MUL  = ('*' , 2)  # Multiplication
    OP_DIV  = ('/' , 2)  # Division
    OP_IDIV = ('//', 2)  # Integer division. For example: 5//2 = 2
    OP_POW  = ('^' , 3)  # Exponentiation
    
    @property
    def symbol (self) -> str:
        return self.value[0]
    
    @property
    def precedence (self) -> int:
        return self.value[1]
    
    @classmethod
    def fromSymbol (cls, symbol) -> 'OP_SET':
        for op in OP_SET:
            if op.symbol == symbol:
                return op
        assert False, f"Passed a none existing symbol: {symbol}"
    
    @classmethod
    def getSymbols (cls) -> list[str]:
        return [op.symbol for op in OP_SET]
    
    def __str__(self) -> str:
        return self.value[0]
    
    def __repr__(self) -> str:
        return self.__str__()


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


# If you are wondering, because i was, if the change is global (to all future python instances), no it is not, i tested it
import sys
sys.setrecursionlimit(10_000)

class Instruction ():
    def __init__(self, temp_a, temp_b) -> None:
        pass
    #def __init__(self, op: OP_SET, a: 'float' | 'int' | 'Instruction', b: 'float' | 'int' | 'Instruction') -> None:
        pass
    pass
# A program is a single instruction
"""
A program is always a TUPLE of two things:
    1. The op_code
    2. A LIST containing the 2 args needed by that operation
then of course an individual arg can be another program, i.e. another tuple

For example 5 + 4 would be:
    ('+', [5, 4])
And 5 + 4 * 2 for example would be:
    ('+', [5, ('*', [4, 2])])
"""

def evaluateOP (op_code: str, args: list) -> float:
    # TODO fix since i switched to enum
    # First compute the args if they need computing
    a, b = args
    if isinstance(a, tuple):
        a = evaluateOP(a[0], a[1])
    if isinstance(b, tuple):
        b = evaluateOP(b[0], b[1])
    
    
    # Then preform the op
    if op_code == OP_ADD: 
        return ADD(a, b)
    
    elif op_code == OP_SUB:
        return SUB(a, b)
    
    elif op_code == OP_MUL:
        return MUL(a, b)
    
    elif op_code == OP_DIV:
        return DIV(a, b)
    
    elif op_code == OP_IDIV:
        return IDIV(a, b)
    
    elif op_code == OP_POW:
        return POW(a, b)
    
    else:
        raise Exception(f"Unknown OP: `{op_code}`, with args: `{args}`")