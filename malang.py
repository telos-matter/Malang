"""
Programming using, literally, only math

More specifically, using only the basic arithmetic operators, i.e. +,-,* and /
, along side ^ (exponents) (which are just repeated multiplication) and
// (integer division) (which is "controlled" subtraction)
, and other basic functions like sqrt, ln, sin and cos

There is one big exception (which hopefully I can resolve in the future) which
is the use of limits in the central-building block/function
of all of this, which is the
different-than-zero function, other than that, it is all just basic operators
and functions, not even the |x| (abs) function, or sign function..

HOW-TO:
. Simply write the function/program that you want at the bottom
using these functions
. Specify whether you want LaTeX output or simple form output
so that it can be evaluated by the evaluator.py script
. Specify the basic option if you want the output to be basic,
for example, if it is set to false, instead of outputting sqrt(x^2) for the abs function
it will output abs(x) directly and so on
. Run the script
"""

# Don't specify the options here, better at the bottom
LATEX_OUTPUT = None
BASIC = None

def engulf (value):
    """
        Parenthesize
        
        Puts parentheses around the passed value if it's not a simple
        number, i.e. it is an expression or function
    """
    if LATEX_OUTPUT:
        try:
            float(value)
            return str(value)
        except ValueError:
            return '\\left(' +str(value) +'\\right)'
    else:
        try:
            float(value)
            return str(value)
        except ValueError:
            return '( ' +str(value) +' )'

def add (value_1, value_2):
    """
        Addition
    """
    return engulf(value_1) +' + ' +engulf(value_2)

def sub (value_1, value_2):
    """
        Subtraction
    """
    return engulf(value_1) +' - ' +engulf(value_2)

def mul (value_1, value_2):
    """
        Multiplication
    """
    if LATEX_OUTPUT:
        return engulf(value_1) +' \\cdot ' +engulf(value_2)
    else:
        return engulf(value_1) +' * ' +engulf(value_2)

def div (value_1, value_2):
    """
        Division
    """
    if LATEX_OUTPUT:
        return '\\frac{' +engulf(value_1) +'}{' +engulf(value_2) +'}'
    else:
        return engulf(value_1) +' / ' +engulf(value_2)

def idiv (value_1, value_2):
    """
        Integer division
        
        //
    """
    if LATEX_OUTPUT:
        return engulf(value_1) +'//' +engulf(value_2) # There is no symbol for it in LaTeX
    else:
        return engulf(value_1) +' // ' +engulf(value_2)

def pow (value_1, value_2):
    """
        Exponential
        
        value_1 raised to the power of value_2, value_1 ^ value_2
    """
    if LATEX_OUTPUT:
        return engulf(value_1) +'^{' +engulf(value_2) +'}'
    else:
        return engulf(value_1) +' ^ ' +engulf(value_2)

def sqrt (value):
    """
        Square root
    """
    if LATEX_OUTPUT:
        return '\\sqrt{' +engulf(value) +'}'
    else:
        return 'sqrt ' +engulf(value)

def ln (value):
    """
        Natural Logarithm
    """
    if LATEX_OUTPUT:
        return '\\ln' +engulf(value)
    else:
        return 'ln ' +engulf(value)

def sin (value):
    """
        Sine
    """
    if LATEX_OUTPUT:
        return '\\sin' +engulf(value)
    else:
        return 'sin ' +engulf(value)

def cos (value): # TODO: Somehow just from sin?
    """
        Cosine
    """
    if LATEX_OUTPUT:
        return '\\cos' +engulf(value)
    else:
        return 'cos ' +engulf(value)

# Those are the building blocks/functions, the rest is just a combination of those
# With the exception of diffZero, upon which everything is based, lol

def diffZero (value): # TODO: find a solution to implement it with basic operations
    """
        Different than zero
        
        Tests if the value is different than zero
    """
    if LATEX_OUTPUT:
        return '\\lim_{x\\to' +engulf(value) +'}' +engulf(div(value, 'x'))
    else:
        return engulf(value) +' != 0' # Not going to bother by implementing limits in the evaluator just for this one expression

def _not (boolean):
    """
        The Not logical operator, !
    """
    return div(sub(boolean, 1), -1)

def equalZero (value):
    """
        Equal to zero
        
        Tests if the value is equal to zero
    """
    return _not(diffZero(value))

def diffNumber (value_1, value_2):
    """
        Different numbers
        
        Tests if value_1 is different than value_2
    """
    return diffZero(sub(value_1, value_2))

def equalNumber (value_1, value_2):
    """
        Equal numbers
        
        Tests if value_1 and value_2 are equal
    """
    return _not(diffNumber(value_1, value_2))

def abs (value):
    """
        Absolute value
    """
    if BASIC:
        return sqrt(pow(value, 2))
    else:
        if LATEX_OUTPUT:
            return '\\lvert' +value +'\\rvert'
        else:
            return 'abs ' +engulf(value)

def tan (value):
    """
        Tangent
    """
    if BASIC:
        return div(sin(value), cos(value))
    else:
        if LATEX_OUTPUT:
            return '\\tan' +engulf(value)
        else:
            return 'tan ' +engulf(value)

def _if (boolean, value_1, value_2):
    """
        If statement
        
        Evaluates to value_1 if the boolean is true, and to value_2 if it is false
    """
    return sub(mul(boolean, value_1), mul(sub(boolean, 1), value_2))

def _and (boolean_1, boolean_2):
    """
        The And logical operator
    """
    return mul(boolean_1, boolean_2)

def _or (boolean_1, boolean_2):
    """
        The Or logical operator
    """
    return _if(_and(equalZero(boolean_1), equalZero(boolean_2)), 0, 1)

def xor (boolean_1, boolean_2):
    """
        The XOR logical operator
    """
    return _if(_and(boolean_1, boolean_2), 0, _or(boolean_1, boolean_2))

def nand (boolean_1, boolean_2):
    """
        The NAND logical operator
    """
    return _not(_and(boolean_1, boolean_2))

def nor (boolean_1, boolean_2):
    """
        The NOR logical operator
    """
    return _not(_or(boolean_1, boolean_2))

def xnor (boolean_1, boolean_2):
    """
        The XNOR logical operator
    """
    return _not(xor(boolean_1, boolean_2))

def diffSign (value_1, value_2):
    """
        Different sign
        
        Tests if value_1 and value_2 have different signs (+, - and 0)
    """
    return _if(_and(equalZero(value_1), equalZero(value_2)), 0, _if(_or(equalZero(value_1), equalZero(value_2)), 1, diffNumber(mul(value_1, value_2), mul(abs(value_1), abs(value_2)))))

def sameSign (value_1, value_2):
    """
        Same sign
        
        Tests if value_1 and value_2 have the same sign (+, - and 0)
    """
    return _not(diffSign(value_1, value_2))

def greaterZero (value):
    """
        Greater than zero
        
        Tests if the value is greater than zero, value > 0
    """
    return _if(equalZero(value),0 , diffSign(value, -1))

def greater (value_1, value_2):
    """
        Greater than
        
        Tests if value_1 is greater than value_2, value_1 > value_2
    """
    return greaterZero(sub(value_1, value_2))

def lessZero (value):
    """
        Less than zero
        
        Tests if the value is less than zero, value < 0
    """
    return _if(equalZero(value), 0, diffSign(value, 1))

def less (value_1, value_2):
    """
        Less than
        
        Tests if value_1 is less than value_2, value_1 < value_2
    """
    return lessZero(sub(value_1, value_2))

def greaterEqualZero (value):
    """
        Greater than or equal to zero
        
        Tests if the value is greater than or equal to zero, value >= 0
    """
    return _or(equalZero(value), greaterZero(value))

def greaterEqual (value_1, value_2):
    """
        Greater than or equal to
        
        Tests if value_1 is greater than or equal to value_2, value_1 >= value_2
    """
    return greaterEqualZero(sub(value_1, value_2))

def lessEqualZero (value):
    """
        Less than or equal to zero
        
        Tests if the value is less than or equal to zero, value <= 0
    """
    return _or(equalZero(value), lessZero(value))

def lessEqual (value_1, value_2):
    """
        Less than or equal to
        
        Tests if value_1 is less than or equal to value_2, value_1 <= value_2
    """
    return lessEqualZero(sub(value_1, value_2))

def sign (value):
    """
        Sign
        
        Returns -1 if the value is negative, 0 if equal to zero, and 1 if positive
    """
    return _if(lessZero(value), -1, _if(equalZero(value), 0, 1))

def max (value_1, value_2):
    """
        Max
        
        Returns the maximum of the two
    """
    return _if(greater(value_1, value_2), value_1, value_2)

def min (value_1, value_2):
    """
        Min
        
        Returns the minimum of the two
    """
    return _if(less(value_1, value_2), value_1, value_2)

def mod (value_1, value_2):
    """
        Modulus
    """
    if BASIC:
        return sub(value_1)

# Those are the functions available, now write you program like in the example below

BASIC = True
LATEX_OUTPUT = False

from evaluator import evaluate
# import pyperclip


out = max(max(69, 420), 666)
# out = greater(2, 5)

print(out)
print(len(out))

# pyperclip.copy(out)

print(evaluate(out))
