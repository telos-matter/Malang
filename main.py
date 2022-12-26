
def engulf (value):
    return '\\left(' +str(value) +'\\right)'

def multiply (value_1, value_2):
    return engulf(value_1) +' \\cdot ' +engulf(value_2)

def _not (value):
    """
        return = (value -1)/-1 
        Where true is 1 and false is 0
        If false is 0 and true is different than 0 then
        return = lim x -> value (((value/x) -1)/-1)
    """
    return '\\frac{\\left(' +engulf(value) +'-1\\right)}{-1}'

def diffZero (value):
    """
        return = lim x -> value (value/x)
    """
    return '\\lim_{x\\to' +engulf(value) +'} \\frac{' + engulf(value) +'}{x}'

def equalZero (value):
    return _not(diffZero(value))

def diffNumber (value_1, value_2):
    return diffZero(f'{value_1} - {value_2}')

def equalNumber (value_1, value_2):
    return _not(diffNumber(value_1, value_2))

def abs (value):
    return '\\sqrt{' +engulf(value) +'^{2}}'

def _if (test, value_1, value_2):
    """
        return = (test)(value_1) -(test -1)(value_2)
    """
    return f'{multiply(test, value_1)} - {multiply(engulf(test) +" - 1", value_2)}'

def _and (value_1, value_2):
    return multiply(value_1, value_2)

def _or (value_1, value_2):
    return _if(_and(equalZero(value_1), equalZero(value_2)), 0, 1)

print(_or(1, 0))