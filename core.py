from __future__ import annotations

'''The core file
It has the possible instructions
And it is what runs and evaluates programmes'''

from enum import Enum
from typing import Callable, Type
from numbers import Number

class OP_SET (Enum):
#   OP   = (REPR, PRECEDENCE, FUNCTION)
    ADD  = ( '+',          1, lambda a, b: a + b)  # Addition
    SUB  = ( '-',          1, lambda a, b: a - b)  # Subtraction
    MUL  = ( '*',          2, lambda a, b: a * b)  # Multiplication
    DIV  = ( '/',          2, lambda a, b: a / b)  # Division
    IDIV = ('//',          2, lambda a, b: a // b) # Integer division. For example: 5//2 = 2
    POW  = ( '^',          3, lambda a, b: a ** b) # Exponentiation
    
    @property
    def symbol (self) -> str:
        return self.value[0]
    
    @property
    def precedence (self) -> int:
        return self.value[1]
    
    @property
    def function (self) -> Callable[[Number, Number], Number]:
        return self.value[2]
    
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


class Instruction ():
    '''An entire program is a single instruction, that instruction
    it self may of course contain other instructions'''
    
    def __init__(self, op: OP_SET, a: Number | Type[Instruction], b: Number | Type[Instruction]) -> None:
        '''`op`: the operation to preform\n
        `a`: the first argument as a number or another Instruction\n
        `b`: the second argument as a number or another Instruction\n'''
        self.op = op
        self.a = a
        self.b = b
    
    def evaluate(self) -> tuple[Number, int]:
        '''Evaluates self'''
        counter = 1
        if type(self.a) == Instruction:
            self.a, _ = self.a.evaluate()
            counter += _
        if type(self.b) == Instruction:
            self.b, _ = self.b.evaluate()
            counter += _
        
        return (self.op.function(self.a, self.b), counter)
    
    def runProgram(self) -> tuple[Number, float, int]:
        '''Runs the program and returns information about it\n
        Namely:\n
        - The result\n
        - How long it took to compute in seconds\n
        - How many instructions it computed'''
        
        import sys
        sys.setrecursionlimit(10_000) # If you are wondering, because I was, if the change is global (to all future python instances), no it is not, I tested it
        
        import time
        
        start = time.time()
        result, counter = self.evaluate() # The instructions are close together so that it misses no milliseconds                                                                                                                                                                                               # A joke obviously
        end = time.time()
        duration = end - start
        
        if result == int(result):
            result = int(result)
        
        return (result, duration, counter)
    
    def __str__(self) -> str:
        return f"({self.a} {self.op} {self.b})"
    
    def __repr__(self) -> str:
        return self.__str__()