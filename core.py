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
    however can be other operations; for example: `1 + 2 + 3` is in fact
    `(1 + 2)` `+ 3`, where the top operation is the second addition and it takes
    what ever the result of `(1 + 2)` is and adds it to `3`.\n
    And so, an entire program is a SINGLE
    operation (and usually it's a VERY BIG one).\n
    
    ### Object structure:\n
        - Each operation knows its operation type (+, -, *..) with the
    `op` attribute.
        - Each operation has exactly two arguments, `a` and `b`,
    they are either operations or numbers. They, respectively,
    represent the left hand side and the right hand side
    of the `op`.
        - When an operation is created it immediately computes its
    result using `op` and stores it in
    the `result` attribute*. This is to avoid
    overflowing the stack with function
    calls (that is, in case they were created and
    then evaluated recursively), and also
    to provide sequential execution of code.
        - Each operation keeps track of how many sub operations
    it has plus it self with the `operations_count` attribute. Know
    that this number refers to how many operation there are mathematically,
    and not actual Operations' objects (because most of the Operation
    objects are reused / referenced multiple times).
    
    
    *: A VERY FREQUENTLY used function is the absolute
    function, which is `((x^2)^0.5)`. And when it's used
    with VERY LARGE integer numbers, the result comes out incorrect
    due to the loss of precision because it gets converted to
    a float. To remedy this, when an operation is created
    it checks if it follows this exact structure: 
    `((x^2)^0.5)`, if so, instead of computing the result
    using `op` it instead just calls the builtin `abs`
    function on `x`. This substitution process
    produces the same
    result intended from the operation, and
    avoids precisions errors because of
    float limitations.
    '''
    
    def __init__(self, op: OP_SET, a: Number | Type[Operation], b: Number | Type[Operation]) -> None:
        '''`op`: the operation to preform, one from the OP_SET\n
        `a`: the first argument as a number or another Operation\n
        `b`: the second argument as a number or another Operation\n'''
        assert type(op) == OP_SET, f"Not from the OP set: {op}"
        assert type(a) == Operation or isinstance(a, Number), f"Neither a Number nor an Operation: {a}"
        assert type(b) == Operation or isinstance(b, Number), f"Neither a Number nor an Operation: {b}"
        
        # Initial operations count is 1, which is self.
        operations_count = 1 
        # Initialize the result
        result = None
        
        # Check if it the absolute function, with this very nicely formatted if statement.
        if (op            is OP_SET.POW and # If this is an exponentiation operation, and
                type(b)   is float      and # its right hand side is a float, and
                b         == 0.5        and # that float is equal to 0.5 (square root), and
                type(a)   is Operation  and # its left hand side is an operation, and
                a.op      is OP_SET.POW and # that operation is an exponentiation operation, and
                type(a.b) is int        and # the right hand side of that operation is an int, and
                a.b       == 2):            # that int is equal to 2, then
                # it's ((x^2)^0.5), which is abs(x)
            
            # First add the operations count from a
            operations_count += a.operations_count
            # Then get x, which is the left hand side of (x^2)
            x = a.a
            # Extract its result if it's an operation
            if type(x) is Operation:
                x = x.result
            # Finally, apply the abs function
            result = abs(x)
        
        # Otherwise, if it's not the absolute function, then compute the result normally
        else:
            # First initialize a_value and b_value
            a_value = a
            b_value = b
            # Then check if they are operations, if so:
            #   - Add their count
            #   - Extract their result
            if type(a) is Operation:
                operations_count += a.operations_count
                a_value = a.result
            if type(b) is Operation:
                operations_count += b.operations_count
                b_value = b.result
            # Now a_value and b_value have the left hand 
            #   side and right side of this operation, respectively.
            #   So just compute the result
            result = op.function(a_value, b_value)
        
        # Check if the result is an int. If so assign it to
        #   result. This is to avoid auto casting to float, which loses
        #   precision.
        #   For example: 1.0 * x, would not return x
        #   if x is a VERY LARGE int number
        int_result = int(result)
        if int_result == result:
            result = int_result
        
        # Finally, store the values
        self.operations_count = operations_count
        self.op = op
        self.a = a
        self.b = b
        self.result = result
    
    def __str__(self) -> str:
        return f"({self.a} {self.op} {self.b})"
    
    def __repr__(self) -> str:
        return self.__str__()