# <<TOC.py>>   Next: <<whats_a_regex.py>>
"""
Regular expressions, how do they work? I'll show you with Python code
you can run and modify right in your editor as you read about it. For
example:
"""

## fgrep(r'cat|dog|whale', ['My elephant is sad because', 'my cat has fleas.'])
#. ['my cat has fleas.']

def fgrep(pattern, lines):
    "Return the lines that match pattern."
    strings = pattern.split('|')
    return [line for line in lines if any(string in line for string in strings)]

"""
Change some of this code and hit M-i; the output will change
accordingly.  You can put it back then, if you want, using Emacs's
Undo command, but you're encouraged to mess it up, add notes, try your
own ideas, instead.

There's more on the mechanics of Halp at <<../sample.py>>.

In this essay we'll survey regular expressions and how to match them
in several ways: naively, by backtracking like classic Unix grep, with
NFAs like Ken Thompson, with Brzozowski derivatives like the Ragel
state machine compiler; and by variations of these. We'll draw out the
connections between the methods and try to make it natural to invent
them.

I'm going to assume you're pretty good with Python and can get around
in Emacs. So let's go: <<whats_a_regex.py>>
"""
# <<TOC.py>>   Next: <<whats_a_regex.py>>
