
def engulf (value):
    """
        engulf
    """
    if len(str(value)) > 1:
        return '\\left(' +str(value) +'\\right)'
    else:
        return str(value)

def add (value_1, value_2):
    """
        add
    """
    return engulf(value_1) +' + ' +engulf(value_2)

def subtract (value_1, value_2):
    """
        subtract
    """
    return engulf(value_1) +' - ' +engulf(value_2)

def multiply (value_1, value_2):
    """
        multiply
    """
    return engulf(value_1) +' \\cdot ' +engulf(value_2)

def divide (value_1, value_2):
    """
        divide
    """
    return '\\frac{' +engulf(value_1) +'}{' +engulf(value_2) +'}'

def _raise (value_1, value_2):
    """
        raise
    """
    return engulf(value_1) +'^{' +engulf(value_2) +'}'

def sqrt (value):
    """
        sqrt
    """
    return '\\sqrt{' +engulf(value) +'}'

def lim_x (limit, expression):
    """
        lim_x
    """
    return '\\lim_{x\\to' +engulf(limit) +'}' +engulf(expression)

def _not (boolean):
    """
        _not

        Boolean here are as such:
            True is 1 and False is 0
        If False is 0 and True is different than 0 then 
        you can replace this function by:
            return divide(subtract(lim_x(boolean, divide(boolean, 'x')), 1), -1)
        or use parseBoolean, which does the same as diffZero
    """
    return divide(subtract(boolean, 1), -1)

def parseBoolean (value):
    """
        parseBoolean
    """
    return lim_x(value, divide(value, 'x'))

def diffZero (value):
    """
        diffZero
    """
    return lim_x(value, divide(value, 'x'))
    #return engulf(value) +'\\neq 0'

def equalZero (value):
    """
        equalZero
    """
    return _not(diffZero(value))
    #return engulf(value) + ' == 0'

def diffNumber (value_1, value_2):
    """
        diffNumber
    """
    return diffZero(subtract(value_1, value_2))

def equalNumber (value_1, value_2):
    """
        equalNumber
    """
    return _not(diffNumber(value_1, value_2))

def abs (value):
    """
        abs
    """
    return sqrt(_raise(value, 2))

def _if (boolean, value_1, value_2):
    """
        _if
    """
    return subtract(multiply(boolean, value_1), multiply(subtract(boolean, 1), value_2))

def _and (boolean_1, boolean_2):
    """
        _and
    """
    return multiply(boolean_1, boolean_2)

def _or (boolean_1, boolean_2):
    """
        _or
    """
    return _if(_and(equalZero(boolean_1), equalZero(boolean_2)), 0, 1)

def xor (boolean_1, boolean_2):
    """
        xor
    """
    return _if(_and(boolean_1, boolean_2), 0, _or(boolean_1, boolean_2))

def nand (boolean_1, boolean_2):
    """
        nand
    """
    return _not(_and(boolean_1, boolean_2))

def nor (boolean_1, boolean_2):
    """
        nor
    """
    return _not(_or(boolean_1, boolean_2))

def xnor (boolean_1, boolean_2):
    """
        xnor
    """
    return _not(xor(boolean_1, boolean_2))

def diffSign (value_1, value_2):
    """
        diffSign

        +, - and 0
    """
    return _if(_and(equalZero(value_1), equalZero(value_2)), 0, _if(_or(equalZero(value_1), equalZero(value_2)), 1, diffNumber(multiply(value_1, value_2), multiply(abs(value_1), abs(value_2)))))

def sameSign (value_1, value_2):
    return _not(diffSign(value_1, value_2))

def greaterZero (value):
    """
        greaterZero
    """
    return _if(equalZero(value), 0, diffSign(value, -1))

def greater (value_1, value_2):
    """
        greater
    """
    return greaterZero(subtract(value_1, value_2))

def lessZero (value):
    """
        lessZero
    """
    return _if(equalZero(value), 0, diffSign(value, 1))

def less (value_1, value_2):
    """
        less
    """
    return lessZero(subtract(value_1, value_2))

def greaterEqualZero (value):
    """
        greaterEqualZero
    """
    return _or(equalZero(value), greaterZero(value))

def greaterEqual (value_1, value_2):
    """
        greaterEqual
    """
    return greaterEqualZero(subtract(value_1, value_2))

def lessEqualZero (value):
    """
        lessEqualZero
    """
    return _or(equalZero(value), lessZero(value))

def lessEqual (value_1, value_2):
    """
        lessEqual
    """
    return lessEqualZero(subtract(value_1, value_2))

def max (value_1, value_2):
    """
        max
    """
    return _if(greater(value_1, value_2), value_1, value_2)

def min (value_1, value_2):
    """
        min
    """
    return _if(less(value_1, value_2), value_1, value_2)

print(max(420,69))
