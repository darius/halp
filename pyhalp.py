#!/usr/bin/env python
"""
Run a Halp-extended .py sourcefile from stdin; write to stdout the
same sourcefile with evaluation results placed inline.
"""

import sys
import traceback

dbg = False

def format_result(s):
    return '#| %s' % s.replace('\n', '\n#| ')

def format_exc(limit=None):
    """Like traceback.format_exc() but I'll be fiddling with it."""
    try:
        etype, value, tb = sys.exc_info()
        lines = format_exception(etype, value, tb, limit)
        return ''.join(lines)
    finally:
        etype = value = tb = None

def format_exception(etype, value, tb, limit=None):
     return (['Traceback (most recent call last):\n']
             + traceback.format_tb(tb, limit)[1:]
             + traceback.format_exception_only(etype, value))

def get_lineno((etype, value, tb)):
    if isinstance(value, SyntaxError) and value.filename == '<string>':
        return value.lineno
    items = traceback.extract_tb(tb)
    if items:
        filename, lineno, func_name, text = items[-1]
        if filename == '<string>':
            return lineno
    return 1

input = [line for line in sys.stdin.read().split('\n')
         if not line.startswith('#| ')]

mod_dict = {'__name__': '', '__file__': '<stdin>', '__doc__': None}

try:
    exec '\n'.join(input) in mod_dict
except:
    lineno = get_lineno(sys.exc_info())
    input.insert(lineno, format_result(format_exc()))
    sys.stdout.write('\n'.join(input))
    sys.exit(0)

def interpret(code):
    """Given a string that may be either an expression or a statement,
    evaluate it and return a string of the outcome, or None."""
    try:
        return repr(eval(code, mod_dict))
    except SyntaxError:
        try:
            exec code in mod_dict
            return None
        except:
            return format_exc()
    except:
        return format_exc()

output = []
for line in input:
    if line.startswith('## '):
        output.append(line)
        outcome = interpret(line[len('## '):])
        if outcome is not None:
            output.append(format_result(outcome))
    else:
        output.append(line)

sys.stdout.write('\n'.join(output))
