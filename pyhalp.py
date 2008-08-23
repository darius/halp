#!/usr/bin/env python
"""
Run a Halp-extended .py sourcefile from stdin; write to stdout the
same sourcefile with evaluation results placed inline.
"""

import sys
import traceback

dbg = False

input = sys.stdin.read()

mod_dict = {'__name__': '', '__file__': '<stdin>', '__doc__': None}

def format_result(s):
    return '#| %s' % s.replace('\n', '\n#| ')

try:
    exec input in mod_dict
except:
    tb = traceback.format_exc()
    sys.stdout.write('%s\n%s' % (format_result(tb), input))
    sys.exit(0)

output = []
for line in input.split('\n'):
    if line.startswith('#| '):
        pass
    elif line.startswith('## '):
        output.append(line)
        expr = line[len('## '):]
        try:
            result = repr(eval(expr, mod_dict))
        except:
            # _, exception, _ = sys.exc_info()
            result = traceback.format_exc()
        output.append(format_result(result))
    else:
        output.append(line)

sys.stdout.write('\n'.join(output))
