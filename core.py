from __future__ import annotations

'''The core file. Has the possible operations'''

from enum import Enum
from typing import Callable, Type
from numbers import Number

class OP_SET (Enum):
    '''The possible operations, but I say OP here in the sense of machine OP, like MOV or JMP'''
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

class Operation ():
    '''An operation object represents a mathematical
    operation (+, -, *,.., namely one from the OP_SET)
    that has an arity of two, e.i. it takes 2 inputs. These two inputs
    however can be other operations, for example: 1 + 2 + 3 is in fact
    (1 + 2) + 3, where the top operation is the second addition and it takes
    what ever the result of (1 + 2) is and adds it to 3.\n
    And so, an entire program is a SINGLE
    operation (and usually it's a VERY BIG one)\n
    ### Object structure:\n
    - Each operation has exactly two arguments, `a` and `b`,
    they are either operations or numbers.
    - Each operation
    keeps track of how many sub operations it has plus it self
    with the `operations_count` attribute. Know that this number
    refers to how many operation there are mathematically,
    and not actual Operations' objects (because most of the Operation
    objects are reused multiple times)
    - When an Operation is created, its result is immediately computed
    and stored. This is to avoid overflowing the stack with function
    calls (that is, in case they were created and then evaluated recursively).
    '''
    
    def __init__(self, op: OP_SET, a: Number | Type[Operation], b: Number | Type[Operation]) -> None:
        '''`op`: the operation to preform, one from the OP_SET\n
        `a`: the first argument as a number or another Operation\n
        `b`: the second argument as a number or another Operation\n'''
        assert type(op) == OP_SET, f"Not from the OP set: {op}"
        assert type(a) == Operation or isinstance(a, Number), f"Neither a Number nor an Operation: {a}"
        assert type(b) == Operation or isinstance(b, Number), f"Neither a Number nor an Operation: {b}"
        
        operations_count = 1 # Self
        a_value = a
        b_value = b
        # If a or b are Operations:
        #   - Add their count
        #   - Get their results
        if type(a) == Operation:
            operations_count += a.operations_count
            a_value = a.result
        if type(b) == Operation:
            operations_count += b.operations_count
            b_value = b.result
        
        # Compute the result
        result = op.function(a_value, b_value)
        # Check if the result is an int. If so assign it to result. This is to avoid auto casting to float, which loses precision. For example, in the if function: 1.0 * VERY_LARGE_INT_NUMBER would return incorrect results
        int_result = int(result)
        if int_result == result:
            result = int_result
        
        self.operations_count = operations_count
        self.op = op
        self.a = a
        self.b = b
        self.result = result
    
    def __str__(self) -> str:
        return f"({self.a} {self.op} {self.b})"
    
    def __repr__(self) -> str:
        return self.__str__()