#!/usr/bin/env python
"""
Run a Halp-extended .js sourcefile from stdin; write to stdout the
same sourcefile with evaluation results placed inline.
"""

import difflib
import subprocess
import sys


# Evaluation

def halp(module_text):
    """Given a module's code as a string, produce the Halp output as a
    string."""
    input_lines = module_text.split('\n')
    input = [line for line in input_lines if not line.startswith('//. ')]
    output = eval_module(input)
    #print 'output', output
    return diff(output, input_lines)

def eval_module(input):
    """Given a module's code as a list of lines, produce the Halp
    output as a list of lines."""
    halp_lines = []
    halp_linenos = []
    for i, line in enumerate(input):
        if line.startswith('/// '):
            halp_lines.append(line[len('/// '):])
            halp_linenos.append(i+1)
    result_string = call_v8halp('\n'.join(input), halp_lines)
    result_lines = result_string.split('\n')
    result_chunks = []
    j = 0
    #print 'result_lines', result_lines
    while j < len(result_lines):
        if result_lines[j] == '': break
        nlines = int(result_lines[j])
        result_chunks.append(result_lines[j+1:j+1+nlines])
        j += 1 + nlines
    #print 'result_chunks', result_chunks
    #print 'halp_linenos', halp_linenos
    assert len(result_chunks) == len(halp_linenos)
    output = list(input)
    for lineno, chunk in reversed(zip(halp_linenos, result_chunks)):
        output[lineno:lineno] = ['//. ' + line for line in chunk]
    return output

def call_v8halp(text, halp_lines):
    #print 'halp_lines', halp_lines
    args = ['v8halp'] + halp_lines
    p = subprocess.Popen(args,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=None)
    stdout, stderr = p.communicate(input=text)
    #print 'stdout', repr(stdout)
    #print stderr
    return stdout


# Producing a diff between input and output

def diff(new_lines, old_lines):
    return format_diff(compute_diff(None, new_lines, old_lines))

def format_diff(triples):
    return ''.join('%d %d %d\n%s' % (lo+1, hi-lo, len(lines),
                                     ''.join(line + '\n' for line in lines))
                   for lines, lo, hi in triples)

def compute_diff(is_junk, a, b):
    """
    Pre: is_junk: None or (string -> bool)
         a, b: [string]
    Return a list of triples (lines, lo, hi) representing the edits
    to convert b to a. The ranges (lo,hi) are disjoint and in
    descending order. Setting each b[lo:hi] = lines, in order, yields a.
    """
    sm = difflib.SequenceMatcher(is_junk, a, b)
    i = j = 0
    triples = []
    for ai, bj, size in sm.get_matching_blocks():
        # Invariant: 
        #  triples is the diff for a[:i], b[:j]
        #  and the next matching block is a[ai:ai+size] == b[bj:bj+size].
        if i < ai or j < bj:
            triples.append((a[i:ai], j, bj))
        i, j = ai+size, bj+size
    triples.reverse()
    return triples


# Main program

if __name__ == '__main__':
    sys.stdout.write(halp(sys.stdin.read()))
