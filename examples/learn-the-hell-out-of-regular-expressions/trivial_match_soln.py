# <<TOC.py>>   Prev: <<trivial_match.py>>   Next: <<>>
"""
WRITEME
"""

from whats_a_regex_soln import *

def match(re, input):
    "Does input match re? Return a boolean."
    return input in matching_strings(re, len(input))

## match(empty, '')
#. True
## match(empty, 'A')
#. False
## match(lit('x'), '')
#. False
## match(lit('x'), 'y')
#. False
## match(lit('x'), 'x')
#. True
## match(lit('x'), 'xx')
#. False
## match(seq(lit('a'), lit('b')), '')
#. False
## match(seq(lit('a'), lit('b')), 'ab')
#. True
## match(alt(lit('a'), lit('b')), 'b')
#. True
## match(alt(lit('a'), lit('b')), 'a')
#. True
## match(alt(lit('a'), lit('b')), 'x')
#. False
## match(many(lit('a')), '')
#. True
## match(many(lit('a')), 'a')
#. True
## match(many(lit('a')), 'x')
#. False
## match(many(lit('a')), 'aa')
#. True
## complicated = seq(many(alt(seq(lit('a'), lit('b')), seq(lit('a'), seq(lit('x'), lit('y'))))), lit('z'))
## match(complicated, '')
#. False
## match(complicated, 'z')
#. True
## match(complicated, 'abz')
#. True
## match(complicated, 'ababaxyab')
#. False
## match(complicated, 'ababaxyabz')
#. True
## match(complicated, 'ababaxyaxz')
#. False

# <<TOC.py>>   Prev: <<trivial_match.py>>   Next: <<>>
