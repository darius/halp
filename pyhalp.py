#!/usr/bin/env python
"""
Run a Halp-extended .py sourcefile from stdin; write to stdout the
same sourcefile with evaluation results placed inline.
"""

import bisect
from cStringIO import StringIO
import difflib
import sys
import traceback


# Evaluation

halp_filename = '<string>'   # Default
current_line_number = None

def halp(module_text):
    """Given a module's code as a string, produce the Halp output as a
    string."""
    input_lines = module_text.split('\n')
    input, old_outputs = strip_old_outputs(input_lines)
    env = set_up_globals(Halp(old_outputs))
    output = format_part(eval_module(input, env))
    return diff(output.split('\n'), input_lines)

def set_up_globals(halp_object):
    if halp_filename.endswith('.py'):
        module_name = halp_filename[:-3]
    else:
        module_name = '<string>'
    return {'__name__': module_name,
            '__file__': halp_filename,
            '__doc__': None,
            'halp': halp_object}

def eval_module(input, module_dict):
    """Given a module's code as a list of lines, produce the Halp
    output as a 'part'."""
    global current_line_number
    current_line_number = None
    try:
        # The "+ '\n'" seems to fix a weird bug where we'd get a
        # syntax error sometimes if the last line was a '## ' line not
        # ending in a newline character. I still don't understand it.
        def thunk(): exec '\n'.join(input) + '\n' in module_dict
        _, output = capturing_stdout(thunk)
    except:
        lineno = get_lineno(sys.exc_info())
        parts = map(InputPart, input)
        parts.insert(lineno, format_exc())
    else:
        parts = []
        for i, line in enumerate(input):
            parts.append(InputPart(line))
            if line.startswith('## '):
                code = line[len('## '):]
                current_line_number = i + 1
                opt_part = eval_line(code, module_dict)
                if opt_part is not None:
                    parts.append(opt_part)
        if output:
            parts.append(OutputPart(output))
    return CompoundPart(parts)

def eval_line(code, module_dict):
    """Given a string that may be either an expression or a statement,
    evaluate it and return a part for output, or None."""
    try:
        result, output = capturing_stdout(lambda: eval(code, module_dict))
    except SyntaxError:
        try:
            def thunk(): exec code in module_dict
            result, output = capturing_stdout(thunk)
        except:
            return format_exc()
    except:
        return format_exc()
    if output:
        if result is not None:
            output = '%s\n%r' % (output, result)
        return OutputPart(output)
    elif result is not None:
        return OutputPart(repr(result))
    else:
        return None

def capturing_stdout(thunk):
    stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        return thunk(), sys.stdout.getvalue()
    finally:
        sys.stdout = stdout


# Halp "System-call interface"

def strip_old_outputs(input_lines):
    stripped = []
    old_outputs = {}
    for line in input_lines:
        if line.startswith('#. '):
            old_outputs.setdefault(len(stripped), []).append(line[len('#| '):])
        else:
            stripped.append(line)
    return stripped, old_outputs

## strip_old_outputs('hello\n#. world\n#. universe'.split('\n'))
#. (['hello'], {1: ['world', 'universe']})

class Halp:
    def __init__(self, old_outputs):
        self._old_outputs = old_outputs
    def read(self):
        return '\n'.join(self._old_outputs.get(current_line_number, []))


# Exception capture

def format_exc(limit=None):
    "Like traceback.format_exc() but returning a 'part'."
    try:
        etype, value, tb = sys.exc_info()
        return format_exception(etype, value, tb, limit)
    finally:
        etype = value = tb = None

def format_exception(etype, value, tb, limit=None):
    "Like traceback.format_exception() but returning a 'part'."
    exc_lines = traceback.format_exception_only(etype, value)
    exc_only = ''.join(exc_lines).rstrip('\n')
    parts = [OutputPart('Traceback (most recent call last):'),
             TracebackPart(extract_censored_tb(tb, limit)),
             OutputPart(exc_only)]
    return CompoundPart(parts)

def extract_censored_tb(tb, limit=None):
    """Like traceback.extract_tb() but with Halp internals
    bowdlerized. (We assume the top-level halp() call is the top of
    our traceback.)"""
    # [3:] drops the top frames (which are Halp internals).
    items = traceback.extract_tb(tb, limit)[3:]
    if items and current_line_number:
        # The top item came from a '## ' line; fix its line number:
        filename, lineno, func_name, text = items[0]
        if filename == '<string>' and lineno == 1: # (should always be true)
            items[0] = filename, current_line_number, func_name, None
    return items

def get_lineno((etype, value, tb)):
    "Return the line number where this exception should be reported."
    if isinstance(value, SyntaxError) and value.filename == '<string>':
        return value.lineno
    items = traceback.extract_tb(tb)
    if items:
        filename, lineno, func_name, text = items[-1]
        if filename == '<string>':
            return lineno
    return 1


# Formatting output with tracebacks fixed up

def format_part(part):
    "Return part expanded into a string, with line numbers corrected."
    lnmap = LineNumberMap()
    part.count_lines(lnmap)
    return part.format(lnmap)

class LineNumberMap:
    "Tracks line-number changes and applies them to old line numbers."
    def __init__(self):
        self.input_lines = []
        self.output_positions = [0] # The line numbers where output is inserted
        self.fixups = [0]
        self.n_output = 0
        # self.fixups[i] is the difference between new and old line
        # numbers for old line numbers in the range
        #   self.output_positions[i] < lineno <= self.output_positions[i+1]
        # Invariant:
        #   len(self.output_positions) == len(self.fixups)
        #   self.output_positions is sorted
        #   self.n_output == sum(self.fixups)
    def add_input_line(self, line):
        self.input_lines.append(line)
    def get_input_line(self, lineno):
        try:
            return self.input_lines[lineno - 1]
        except IndexError:
            return None
    def count_output(self, n_lines):
        self.n_output += n_lines
        self.output_positions.append(1 + len(self.input_lines))
        self.fixups.append(self.n_output)
    def fix_lineno(self, lineno):
        i = bisect.bisect_right(self.output_positions, lineno) - 1
        return lineno + self.fixups[i]

class CompoundPart:
    "A part that's a sequence of subparts."
    def __init__(self, parts):
        self.parts = parts
    def count_lines(self, lnmap):
        for part in self.parts:
            part.count_lines(lnmap)
    def format(self, lnmap):
        return '\n'.join(part.format(lnmap) for part in self.parts)

class InputPart:
    "An input line, passed to the output unchanged."
    def __init__(self, text):
        self.text = text
    def count_lines(self, lnmap):
        lnmap.add_input_line(self.text)
    def format(self, lnmap):
        return self.text

class OutputPart:
    "Some output lines, with a #. prefix."
    def __init__(self, text):
        self.text = text
    def count_lines(self, lnmap):
        lnmap.count_output(1 + self.text.count('\n'))
    def format(self, lnmap):
        return format_result(self.text)

class TracebackPart:
    """An output traceback with a #. prefix and with the stack frames
    corrected when they refer to the code being halped."""
    def __init__(self, tb_items):
        self.items = tb_items
    def count_lines(self, lnmap):
        def item_len((filename, lineno, name, line)):
            return 2 if line else 1
        lnmap.count_output(sum(map(item_len, self.items)))
    def format(self, lnmap):
        def fix_item((filename, lineno, name, line)):
            if filename == '<string>':
                filename = halp_filename
                line = lnmap.get_input_line(lineno)
                lineno = lnmap.fix_lineno(lineno)
            return (filename, lineno, name, line)
        return format_result(format_traceback(map(fix_item, self.items)))

def format_result(s):
    "Prefix each line of s with '#. '."
    return '#. %s' % s.replace('\n', '\n#. ')

def format_traceback(tb_items):
    "Turn a list of traceback items into a string."
    return ''.join(traceback.format_list(tb_items)).rstrip('\n')


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
    if 2 <= len(sys.argv):
        halp_filename = sys.argv[1]
    sys.stdout.write(halp(sys.stdin.read()))
