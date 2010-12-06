# <<TOC.py>>   Prev: <<README.py>>   Next: <<trivial_match.py>>
"""
You've probably used regular expressions via Python's 're' module,
grep, etc. We'll build them from scratch, but skipping, for now, the
bells and whistles that'd distract from the core ideas.

A regular expression denotes a set of strings. We have five ways to
build one:

       Concrete syntax          Example           Constructor
       ===============          =======           ===========
re ::= <the empty string>       r''               empty
     | <literal character>      r'A'              lit(c)
     | re '|' re                r'X|Y'            alt(re1, re2)
     | re re                    r'Hello'          seq(re1, re2)
     | re '*'                   r'A*'             many(re)

'empty' matches the empty string.

lit(c) matches the single-character string c. (Longer literals can be
matched using seq, below.)

seq(re1, re2) matches any string with a head matching re1 and a tail
matching re2, with the head immediately abutting the tail. For
example, seq(lit('a'), lit('b')) matches 'ab' and nothing else. re1
and re2 must themselves be regular expressions. (We'll assume the same
by convention for variables named like 're' from now on implicitly.)

alt(re1, re2) matches any string that matches either of re1 or re2.

many(re) matches when 0 or more copies of re in sequence would
match. For example, many(lit('A')) matches '', 'A', 'AA', 'AAA', and
so on.

Define a function matching_strings(re, length) that returns a set of
all of re's matching strings of exactly the given length. Here's a
skeleton and test cases to work from.
"""

def matching_strings(re, length):
    pass

empty = 'TBD'

def lit(c):
    TBD

def alt(re1, re2):
    TBD

def seq(re1, re2):
    TBD

def many(re):
    TBD

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

"""
You can compare to my solution at <<whats_a_regex_soln.py>>.

WRITEME exhortation to actually try and write the code yourself first,
with quotes from Feynman, example of Turing, etc. Much of the point of
this new medium of active essays, I'm supposing.
"""
# <<TOC.py>>   Prev: <<README.py>>   Next: <<trivial_match.py>>
