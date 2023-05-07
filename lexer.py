import malang

def diffZero (n):
    return (malang.OP_DIFFZERO, [n])

def add (a, b):
    return (malang.OP_ADD, [a, b])

def sub (a, b):
    return (malang.OP_SUB, [a, b])

def mul (a, b):
    return (malang.OP_MUL, [a, b])

def div (a, b):
    return (malang.OP_DIV, [a, b])

def idiv (a, b):
    return (malang.OP_IDIV, [a, b])

def pow (a, b):
    return (malang.OP_POW, [a, b])

def sqrt (n):
    return (malang.OP_SQRT, [n])

def ln (n):
    return (malang.OP_LN, [n])

def sin (n):
    return (malang.OP_SIN, [n])

def cos (n):
    return (malang.OP_COS, [n])

###################################

def _not (boolean):
    return div(sub(boolean, 1), -1)

def equalZero (x):
    return _not(diffZero(x))

def null (x):
    return equalZero(x)

def diffNumber (a, b):
    return diffZero(sub(a, b))

def equalNumber (a, b):
    return _not(diffNumber(a, b))

def abs (x):
    return sqrt(pow(x, 2))

def tan (x):
    return div(sin(x), cos(x))

def log (x, base):
    return div(ln(x), ln(base))

def _if (boolean, a, b):
    return sub(mul(boolean, a), mul(sub(boolean, 1), b))

def _and (boolean_1, boolean_2):
    return mul(boolean_1, boolean_2)

def _or (boolean_1, boolean_2):
    return _if(_and(null(boolean_1), null(boolean_2)), 0, 1)

def xor (boolean_1, boolean_2):
    return _if(_and(boolean_1, boolean_2), 0, _or(boolean_1, boolean_2))

def nand (boolean_1, boolean_2):
    return _not(_and(boolean_1, boolean_2))

def nor (boolean_1, boolean_2):
    return _not(_or(boolean_1, boolean_2))

def xnor (boolean_1, boolean_2):
    return _not(xor(boolean_1, boolean_2))

def diffSign (a, b):
    return _if(_and(null(a), null(b)), 0, _if(_or(null(a), null(b)), 1, diffNumber(mul(a, b), mul(abs(a), abs(b)))))

def sameSign (a, b):
    return _not(diffSign(a, b))

def greaterZero (x):
    return _if(null(x),0 , diffSign(x, -1))

def positive (x):
    return greaterZero(x)

def greater (a, b):
    return greaterZero(sub(a, b))

def lessZero (x):
    return _if(null(x), 0, diffSign(x, 1))

def negative (x):
    return lessZero(x)

def less (a, b):
    return lessZero(sub(a, b))

def greaterEqualZero (x):
    return _or(null(x), greaterZero(x))

def greaterEqual (a, b):
    return greaterEqualZero(sub(a, b))

def lessEqualZero (x):
    return _or(null(x), lessZero(x))

def lessEqual (a, b):
    return lessEqualZero(sub(a, b))

def sign (x):
    return _if(negative(x), -1, _if(null(x), 0, 1))

def max (a, b):
    return _if(greater(a, b), a, b)

def min (a, b):
    return _if(less(a, b), a, b)

def mod (a, b):
    return _if(negative(a), sub(b, sub(abs(a), mul(idiv(abs(a), b), b))), sub(a, mul(idiv(a, b), b)))

def floor (x):
    return sub(x, mod(x, 1))

def ceil (x):
    return add(floor(x), 1)

def _int (x):
    return mul(sign(x), floor(abs(x)))

def decimal (x):
    return sub(x, _int(x))

def round (x):
    return mul(sign(x), _if(less(decimal(abs(x)), 0.5), _int(abs(x)), add(_int(abs(x)), 1)))

def divisible (a, b):
    return null(mod(a, b))

def even (x):
    return divisible(x, 2)

def odd (x):
    return _not(even(x))


program = max(max(max(max(max(max(69, 420), 666), 1000), 2), 5), 9999)
# print(program)

import time
start = time.time()

out = malang.evaluateOP(program[0], program[1])

end = time.time()

print(f"Outputed {out}\nComputed in {end -start} sec")
