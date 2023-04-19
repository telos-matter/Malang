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

def engulf (x):
    """
        Parenthesize
        
        Puts parentheses around the passed x if it's not a simple
        number, i.e. it is an expression or function
    """
    if LATEX_OUTPUT:
        try:
            float(x)
            return str(x)
        except ValueError:
            return '\\left(' +str(x) +'\\right)'
    else:
        try:
            float(x)
            return str(x)
        except ValueError:
            return '( ' +str(x) +' )'

def add (a, b):
    """
        Addition
    """
    return engulf(a) +' + ' +engulf(b)

def sub (a, b):
    """
        Subtraction
    """
    return engulf(a) +' - ' +engulf(b)

def mul (a, b):
    """
        Multiplication
    """
    if LATEX_OUTPUT:
        return engulf(a) +' \\cdot ' +engulf(b)
    else:
        return engulf(a) +' * ' +engulf(b)

def div (a, b):
    """
        Division
    """
    if LATEX_OUTPUT:
        return '\\frac{' +engulf(a) +'}{' +engulf(b) +'}'
    else:
        return engulf(a) +' / ' +engulf(b)

def idiv (a, b):
    """
        Integer division
        
        //
    """
    if LATEX_OUTPUT:
        return engulf(a) +'//' +engulf(b) # There is no symbol for it in LaTeX
    else:
        return engulf(a) +' // ' +engulf(b)

def pow (a, b):
    """
        Exponential
        
        a raised to the power of b, a ^ b
    """
    if LATEX_OUTPUT:
        return engulf(a) +'^{' +engulf(b) +'}'
    else:
        return engulf(a) +' ^ ' +engulf(b)

def sqrt (x):
    """
        Square root
    """
    if LATEX_OUTPUT:
        return '\\sqrt{' +engulf(x) +'}'
    else:
        return 'sqrt ' +engulf(x)

def ln (x):
    """
        Natural Logarithm
    """
    if LATEX_OUTPUT:
        return '\\ln' +engulf(x)
    else:
        return 'ln ' +engulf(x)

def sin (x):
    """
        Sine
    """
    if LATEX_OUTPUT:
        return '\\sin' +engulf(x)
    else:
        return 'sin ' +engulf(x)

def cos (x): # TODO: Somehow just from sin?
    """
        Cosine
    """
    if LATEX_OUTPUT:
        return '\\cos' +engulf(x)
    else:
        return 'cos ' +engulf(x)

# Those are the building blocks/functions, the rest is just a combination of those
# With the exception of diffZero, upon which everything is based, lol

def diffZero (x): # TODO: find a solution to implement it with basic operations
    """
        Different than zero
        
        Tests if x is different than zero
    """
    if LATEX_OUTPUT:
        return '\\lim_{x\\to' +engulf(x) +'}' +engulf(div(x, 'x'))
    else:
        return engulf(x) +' != 0' # Not going to bother by implementing limits in the evaluator just for this one expression

def _not (boolean):
    """
        The NOT logical operator, !
    """
    return div(sub(boolean, 1), -1)

def equalZero (x):
    """
        Equal to zero
        
        Tests if x is equal to zero
    """
    return _not(diffZero(x))

def null (x):
    """Alias for equalZero"""
    return equalZero(x)

def diffNumber (a, b):
    """
        Different numbers
        
        Tests if a is different than b
    """
    return diffZero(sub(a, b))

def equalNumber (a, b):
    """
        Equal numbers
        
        Tests if a and b are equal
    """
    return _not(diffNumber(a, b))

def abs (x):
    """
        Absolute x
    """
    if BASIC:
        return sqrt(pow(x, 2))
    else:
        if LATEX_OUTPUT:
            return '\\lvert' +x +'\\rvert'
        else:
            return 'abs ' +engulf(x)

def tan (x):
    """
        Tangent
    """
    if BASIC:
        return div(sin(x), cos(x))
    else:
        if LATEX_OUTPUT:
            return '\\tan' +engulf(x)
        else:
            return 'tan ' +engulf(x)

def _if (boolean, a, b):
    """
        If statement
        
        Evaluates to a if the boolean is true, and to b if it is false
    """
    return sub(mul(boolean, a), mul(sub(boolean, 1), b))

def _and (boolean_1, boolean_2):
    """
        The AND logical operator, &
    """
    return mul(boolean_1, boolean_2)

def _or (boolean_1, boolean_2):
    """
        The OR logical operator, |
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

def diffSign (a, b):
    """
        Different sign
        
        Tests if a and b have different signs (+, - and 0)
    """
    return _if(_and(equalZero(a), equalZero(b)), 0, _if(_or(equalZero(a), equalZero(b)), 1, diffNumber(mul(a, b), mul(abs(a), abs(b)))))

def sameSign (a, b):
    """
        Same sign
        
        Tests if a and b have the same sign (+, - and 0)
    """
    return _not(diffSign(a, b))

def greaterZero (x):
    """
        Greater than zero
        
        Tests if the x is greater than zero, x > 0
    """
    return _if(equalZero(x),0 , diffSign(x, -1))

def positive (x):
    """Alias for greaterZero"""
    return greaterZero(x)

def greater (a, b):
    """
        Greater than
        
        Tests if a is greater than b, a > b
    """
    return greaterZero(sub(a, b))

def lessZero (x):
    """
        Less than zero
        
        Tests if the x is less than zero, x < 0
    """
    return _if(equalZero(x), 0, diffSign(x, 1))

def negative (x):
    """Alias for lessZero"""
    return lessZero(x)

def less (a, b):
    """
        Less than
        
        Tests if a is less than b, a < b
    """
    return lessZero(sub(a, b))

def greaterEqualZero (x):
    """
        Greater than or equal to zero
        
        Tests if the x is greater than or equal to zero, x >= 0
    """
    return _or(equalZero(x), greaterZero(x))

def greaterEqual (a, b):
    """
        Greater than or equal to
        
        Tests if a is greater than or equal to b, a >= b
    """
    return greaterEqualZero(sub(a, b))

def lessEqualZero (x):
    """
        Less than or equal to zero
        
        Tests if the x is less than or equal to zero, x <= 0
    """
    return _or(equalZero(x), lessZero(x))

def lessEqual (a, b):
    """
        Less than or equal to
        
        Tests if a is less than or equal to b, a <= b
    """
    return lessEqualZero(sub(a, b))

def sign (x):
    """
        Sign
        
        Returns -1 if the x is negative, 0 if equal to zero, and 1 if positive
    """
    return _if(lessZero(x), -1, _if(null(x), 0, 1))

def max (a, b):
    """
        Max
        
        Returns the maximum of the two
    """
    return _if(greater(a, b), a, b)

def min (a, b):
    """
        Min
        
        Returns the minimum of the two
    """
    return _if(less(a, b), a, b)

def mod (a, b):
    """
        Modulus
    """
    if BASIC:
        return _if(negative(a), sub(b, sub(abs(a), mul(idiv(abs(a), b), b))), sub(a, mul(idiv(a, b), b)))
    else:
        if LATEX_OUTPUT:
            return engulf(a) +'\\bmod' +engulf(b)
        else:
            return engulf(a) +' % ' +engulf(b)

def floor (x):
    """
        Floor, ⌊x⌋
    """
    return sub(x, mod(x, 1))

def ceil (x):
    """
        Ceil, ⌈x⌉
    """
    return add(floor(x), 1)

def _int (x):
    """
        Int
        
        Returns the integer part of x
    """
    return mul(sign(x), floor(abs(x)))

# TODO: Add factorial, combination and other probability useful stuff

# Those are the functions available, now write you program like in the example below

BASIC = True
LATEX_OUTPUT = False

program = max(max(69, 420), 666)

if LATEX_OUTPUT:
    print(program)
    print(len(program))
else:
    from evaluator import evaluate
    print(program)
    print(evaluate(program))
