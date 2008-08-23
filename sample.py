# Hello, this is a sample. 

import operator

def fact(n):
    return reduce(operator.mul, range(1, n+1), 1)

# When you hit M-i you should see '#| 120' appear below the following line:

## fact(2 + 3)

# OK.
