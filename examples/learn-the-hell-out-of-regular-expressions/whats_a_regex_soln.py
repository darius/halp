# <<TOC.py>>   Back: <<whats_a_regex.py>>   Next: <<.py>>
"""
XXX blah blah blah
"""

def matching_strings(re, length):
    return re(length)

def lit(c):
    return lambda n: [c] if n == 1 else []

def alt(re1, re2):
    return lambda n: re1(n) + re2(n)

def empty(n):
    return [''] if n == 0 else []

def seq(re1, re2):
    def me(n):
        return [s1+s2 for i in range(n+1) for s1 in re1(i) for s2 in re2(n-i)]
    return me

def many(re):
    def me(n):
        if n == 0: return ['']
        return [s1+s2 for i in range(1, n+1) for s1 in re(i) for s2 in me(n-i)]
    return me


## def gen(re, length): return sorted(matching_strings(re, length))

## gen(empty, 0)
#. ['']
## gen(empty, 1)
#. []
## gen(lit('A'), 0)
#. []
## gen(lit('A'), 1)
#. ['A']
## gen(lit('A'), 2)
#. []
## gen(alt(empty, lit('B')), 0)
#. ['']
## gen(alt(empty, lit('B')), 1)
#. ['B']
## gen(alt(lit('A'), lit('B')), 0)
#. []
## gen(alt(lit('A'), lit('B')), 1)
#. ['A', 'B']
## gen(seq(empty, empty), 0)
#. ['']
## gen(seq(empty, lit('B')), 0)
#. []
## gen(seq(empty, lit('B')), 1)
#. ['B']
## gen(seq(empty, lit('B')), 2)
#. []
## gen(seq(lit('A'), lit('B')), 2)
#. ['AB']
## gen(seq(alt(lit('A'), lit('C')), lit('B')), 2)
#. ['AB', 'CB']
## gen(many(empty), 0)
#. ['']
## gen(many(empty), 1)
#. []
## gen(many(lit('A')), 0)
#. ['']
## gen(many(lit('A')), 1)
#. ['A']
## gen(many(lit('A')), 5)
#. ['AAAAA']
## gen(seq(lit('A'), seq(many(alt(lit('B'), lit('C'))), lit('D'))), 5)
#. ['ABBBD', 'ABBCD', 'ABCBD', 'ABCCD', 'ACBBD', 'ACBCD', 'ACCBD', 'ACCCD']

# <<TOC.py>>   Back: <<whats_a_regex.py>>   Next: <<.py>>
