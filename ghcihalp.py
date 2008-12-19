#!/usr/bin/env python
"""
Run a Halp-extended .lhs sourcefile from stdin; write to stdout the
same sourcefile with evaluation results placed inline.
"""

import os
import re
import subprocess
import sys
import tempfile

dbg = False

ext = sys.argv[1]

input = [line for line in sys.stdin if not line.startswith('-- | ')]
if input and not input[-1].endswith('\n'):
    input[-1] += '\n'
input.append('\n')
if ext == '.hs':
    input.append('aouhtnuoeahn = 0 -- Make sure the file has *some* code.\n')
else:
    input.append('> aouhtnuoeahn = 0 -- Make sure the file has *some* code.\n')

module_name = 'Main'
defn_lines = []
eval_line_numbers = []
eval_lines = []
for i, line in enumerate(input):
    if line.startswith('--- '):
        eval_line_numbers.append(i+1)
        eval_lines.append(line[len('--- '):])
    else:
        m = re.search(r'module (.*) where', line) # TODO: more specific
        if m:
            module_name = m.group(1)
        defn_lines.append(line)

if dbg:
    print eval_line_numbers
    print ''.join(eval_lines)

fd, main_lhs = tempfile.mkstemp(ext)
try:
    os.write(fd, ''.join(defn_lines))
    os.close(fd)
    ghci = subprocess.Popen(['ghci', main_lhs],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT) # for now
    ghci.stdin.write(''.join(eval_lines))
    results, foo = ghci.communicate()
finally:
    os.unlink(main_lhs)

if dbg:
    print results, foo
    print ''

def count(it):
    n = 0
    for flag in it:
        if flag:
            n += 1
    return n

prompt = '*%s> ' % module_name
result_lines = results.split('\n')
output = input[:-2]
for j, r in enumerate(result_lines):
    m = re.search(r'[.]lhs:(\d+):(\d+):', r)
    if m:
        error_line_num = int(m.group(1))
        output_line_num = (error_line_num
                           + count(lnum < error_line_num
                                   for lnum in eval_line_numbers))
        output.insert(output_line_num, '-- | At column %s:\n' % m.group(2))
        output_line_num += 1
        for plaint_line in result_lines[j+1:]:
            if plaint_line.startswith('Failed, modules loaded:'): break
            output.insert(output_line_num, '-- | %s\n' % plaint_line)
            output_line_num += 1
        break
    if r.startswith(prompt):
        i = 0
        for r in result_lines[j:]:
            if r.startswith(prompt):
                result = r[len(prompt):]
                if result.startswith('Leaving GHCi.'): break
                output.insert(eval_line_numbers[i] + i, '-- | %s\n' % result)
                i += 1
        break

sys.stdout.write(''.join(output).replace('\r\n', '\n'))
