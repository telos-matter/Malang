
def evaluate (stack: list, index: int= 0):
    token = stack.pop(index)
    print(f'\tIndex: {index} -> {token}')
    
    if token == '(':
        stack.insert(index, evaluate(stack, index))
        return evaluate(stack, index +1)

    elif token == ')':
        return stack.pop(index -1)

    elif token == '-':
        a = stack.pop(index -1)
        b = evaluate(stack, index -1)
        stack.insert(index -1, a - b)
        return evaluate(stack, index -1)

    elif token == '+':
        a = stack.pop(index -1)
        b = evaluate(stack, index -1)
        stack.insert(index -1, a + b)
        return evaluate(stack, index -1)
    
    elif token == '*':
        a = stack.pop(index -1)
        b = evaluate(stack, index -1)
        stack.insert(index -1, a * b)
        return evaluate(stack, index -1)

    elif token == '/':
        a = stack.pop(index -1)
        b = evaluate(stack, index -1)
        stack.insert(index -1, a / b)
        return evaluate(stack, index -1)

    elif token == '^':
        a = stack.pop(index -1)
        b = evaluate(stack, index -1)
        stack.insert(index -1, a ** b)
        return evaluate(stack, index -1)

    elif token == 'sqrt':
        assert False,' Nope'
        a = stack.pop(index -1)
        b = evaluate(stack, index -1)
        stack.insert(index -1, a ** b)
        return evaluate(stack, index -1)

    elif token == '!=':
        a = stack.pop(index -1)    
        b = evaluate(stack, index -1)
        stack.insert(index -1, int(a != b))
        return evaluate(stack, index -1)

    elif token == '==':
        a = stack.pop(index -1)    
        b = evaluate(stack, index -1)
        stack.insert(index -1, int(a == b))
        return evaluate(stack, index -1)

    else:
        try:
            if int(token) == float(token):
                return int(token)
            else:
                return float(token)
        except ValueError:
            assert False, f'Unknown token: {token}'


def parse (input: str):
    stack = input.split()

    while len(stack) > 1:
        print(f'Before: {stack}')
        try:
            float(stack[0])
            value = evaluate(stack, 1)
        except ValueError:
            value = evaluate(stack, 0)
        print(f'Returned: {value}\n\n')
        stack.insert(0, value)

    print(stack[0])



parse('( ( 10 - 2 ) + ( ( 2 ^ 2 ) * 4 ) ) / 12')
