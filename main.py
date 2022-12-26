import math

def _not (value):
    """
        return = (value -1)/-1 
        # Where true is 1 and false is 0
        # If false is 0 and true is different than 0 then
        return = lim x -> value (((value/x) -1)/-1)
    """
    return not value

def diffZero (value):
    """
        return = lim x -> value (value/x)
    """
    return value != 0

def equalZero (value):
    """
        return_1 = lim x -> value (value/x)
        return = (return_1 -1)/-1
    """
    return _not(diffZero(value))

def diffNumber (value, number):
    """
        value_1 = value - number
        return lim x -> value_1 (value_1/x)
    """
    return diffZero(value - number)

def equalNumber (value, number):
    """
        value_1 = value - number
        return_1 lim x -> value_1 (value_1/x)
        return = (return_1 -1)/-1
    """
    return _not(diffNumber(value, number))

def abs (value):
    """
        return = sqrt(value^2)
    """
    return math.sqrt(value**2)

def _if (test, value_1, value_2):
    """
        return = (test)(value_1) -(test -1)(value_2)
    """
    if (test):
        return value_1
    else:
        return value_2

def _and (value_1, value_2):
    """
        return = value_1 * value_2
    """
    return value_1 and value_2

def _or (value_1, value_2):
    """
    
    """
    return _if(_and(equalZero(value_1), equalZero(value_2)), 0, 1)
