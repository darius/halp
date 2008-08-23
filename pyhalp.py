#!/usr/bin/env python
"""
Run a Halp-extended .py sourcefile from stdin; write to stdout the
same sourcefile with evaluation results placed inline.
"""

import sys

dbg = False

ext = '.py'
out = '#| '

input = sys.stdin.read()

md = {'__name__': '', '__doc__': None, '__file__': ''}

exec input in md

output = []
for line in input.split('\n'):
    if line.startswith('#| '):
        pass
    elif line.startswith('## '):
        output.append(line + '\n')
        expr = line[len('## '):]
        output.append('#| %r\n' % eval(expr, md)) # XXX
    else:
        output.append(line + '\n')

sys.stdout.write(''.join(output))
