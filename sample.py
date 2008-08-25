# Hello, this is a sample. 

import operator

def fact(n):
    if n <= 0:
        return 1
    else:
        return n * fact(n - 1)

# When you hit M-i you should see '#| 120' appear below the following line:

## fact(2 + 3)

# OK.
