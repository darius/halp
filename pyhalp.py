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

def get_lineno((etype, value, tb)):
    if etype is SyntaxError and value.filename == '<string>':
        return value.lineno
    items = traceback.extract_tb(tb)
    if items:
        filename, lineno, func_name, text = items[-1]
        if filename == '<string>':
            return lineno
    return 1

input = sys.stdin.read()

mod_dict = {'__name__': '', '__file__': '<stdin>', '__doc__': None}

try:
    exec input in mod_dict
except:
    lineno = get_lineno(sys.exc_info())
    lines = input.split('\n')
    def keep_source_lines(lines):
        return [line for line in lines if not line.startswith('#| ')]
    def write(lines):
        sys.stdout.write('\n'.join(lines))
    write(keep_source_lines(lines[:lineno])
          + [format_result(traceback.format_exc())]
          + keep_source_lines(lines[lineno:]))
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
            result = traceback.format_exc()
        output.append(format_result(result))
    else:
        output.append(line)

sys.stdout.write('\n'.join(output))
