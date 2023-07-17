#!/usr/bin/env python3
"""
Run a Halp-extended .py sourcefile from stdin; write to stdout an
encoding of the same sourcefile with evaluation results placed inline.
The encoding is a kind of diff against the input, expected by halp.el.
"""

# We want this module to work in either Python 2 or 3. Thus this awkwardness:
try:
    from cStringIO import StringIO
except ModuleNotFoundError:
    from io import StringIO

import bisect
import difflib
import os
import sys
import traceback


# Evaluation

source_filename = '<string>'  # Default

current_line_number = None

def halp(module_text):
    """Given a module's code as a string, produce the Halp output as a
    string."""
    input_lines = module_text.splitlines()
    input, old_outputs = strip_old_outputs(input_lines)
    env = set_up_globals(Halp(old_outputs))
    output = format_part(eval_module(input, env))
    return diff(output.splitlines(), input_lines)

def set_up_globals(halp_object):
    if source_filename.endswith('.py'):
        module_name = source_filename[:-3]
    else:
        module_name = '<string>'
    return {'__name__': module_name,
            '__file__': source_filename,
            '__doc__': None,
            'halp': halp_object}

def eval_module(input, module_dict):
    """Given a module's code as a list of lines, produce the Halp
    output as a 'part'."""
    global current_line_number
    current_line_number = None

    # The "+ '\n'" seems to fix a weird bug where we'd get a
    # syntax error sometimes if the last line was a '## ' line not
    # ending in a newline character. I still don't understand it.
    def thunk(): exec('\n'.join(input) + '\n', module_dict)
    output, _, exc_info, is_syn  = capturing_stdout(thunk)
    if exc_info is not None:
        lineno = get_lineno(exc_info)
        parts = map(InputPart, input)
        parts.insert(lineno, format_exception(exc_info))
    else:
        parts = []
        for i, line in enumerate(input):
            parts.append(InputPart(line))
            if line.startswith('## '):
                code = line[len('## '):]
                current_line_number = i + 1
                parts.extend(eval_line(code, module_dict))
        if output:
            parts.append(OutputPart(output))
    return CompoundPart(parts)

def eval_line(code, module_dict):
    """Given a string that may be either an expression or a statement,
    evaluate it and return a list of parts for output."""
    output, result, exc_info, is_syn = \
        capturing_stdout(lambda: eval(code, module_dict))
    if exc_info is not None:
        # If a line failed to parse as an expression, it might be the
        # line was meant as a statement. (Properly we should first try
        # to *parse* instead of *eval*, above. XXX Distinguishing them
        # in this way instead is a lazy hack which will misbehave in
        # rare cases.)
        if is_syn:
            def thunk(): exec(code, module_dict)
            output, result, exc_info, is_syn = capturing_stdout(thunk)
    parts = []
    if output: parts.append(OutputPart(output))
    if result is not None: parts.append(OutputPart(repr(result)))
    if exc_info is not None: parts.append(format_exception(exc_info))
    return parts

def capturing_stdout(thunk):
    """Run thunk() and return either (output, result, None, None) or
    (output, None, exc_info, is_syntax_error) -- the latter if thunk
    raised an exception."""
    # XXX ugly interface to preserve tricky exception/traceback
    #  capture logic to do with stack frames and line numbers.
    #  Come back to this -- hopefully could be cleaner.
    stdout = sys.stdout
    sys.stdout = stringio = StringIO()
    try:
        result = thunk()
    except SyntaxError:
        return stringio.getvalue(), None, sys.exc_info(), True
    except:
        return stringio.getvalue(), None, sys.exc_info(), False
    else:
        return stringio.getvalue(), result, None, None
    finally:
        sys.stdout = stdout

## strip_old_outputs('hello\n#. world\n#. universe'.split('\n'))
#. (['hello'], {1: ['world', 'universe']})

def strip_old_outputs(input_lines):
    stripped = []
    old_outputs = {}
    for line in input_lines:
        if line.startswith('#. '):
            old_outputs.setdefault(len(stripped), []).append(line[len('#. '):])
        else:
            stripped.append(line)
    return stripped, old_outputs


# Halp "system-call interface"
# This lets you feed back your command's previous output with 'halp.read()'.

class Halp:
    def __init__(self, old_outputs):
        self._old_outputs = old_outputs
    def read(self):
        return '\n'.join(self._old_outputs.get(current_line_number, []))


# Exception capture

def format_exception(exc, limit=None):
    "Like traceback.format_exception() but returning a 'part'."
    (etype, value, tb) = exc
    exc_lines = traceback.format_exception_only(etype, value)
    exc_only = ''.join(exc_lines).rstrip('\n')
    items = extract_censored_tb(tb, limit)
    if items:
        return CompoundPart([OutputPart('Traceback (most recent call last):'),
                             TracebackPart(items),
                             OutputPart(exc_only)])
    else:
        return OutputPart(exc_only)

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

def get_lineno(exc):
    "Return the line number where this exception should be reported."
    (etype, value, tb) = exc
    if isinstance(value, SyntaxError) and value.filename == '<string>':
        return value.lineno
    items = traceback.extract_tb(tb)
    if items:
        filename, lineno, func_name, text = items[-1]
        if filename == '<string>':
            return lineno
    return 0


# Formatting output with tracebacks fixed up.
# 
# The problem: we want to get useful tracebacks as in an ordinary Python REPL.
# But when we insert outputs and errors into the halped *source* file, the line
# numbers in the tracebacks get out of sync with the source lines.
# 
# It'd be nice if the eval/exec above could take inputs whose line
# numbers were already correct; but this implies two subproblems:
#   1. Getting these line numbers into the eval/exec inputs.
#      (You could hack it: prefix k-1 newlines to the string we're evaling for line k.)
#   2. What if a traceback from evaluating a `## ` line references
#      lines in the overall module which appear *after* the traceback
#      (whose length might differ from that of the previous '#. ' output)?
#      This problem might be hackable too by re-evaluating and hoping the
#      length stays the same, but ehhh forget it.
#
# So, every exec/eval will appear to Python to be starting at line 1,
# and then here we correct the line numbers in the tracebacks. The
# correction pass waits until after all outputs have been collected.

def format_part(part):
    "Return part expanded into a string, with line numbers corrected."
    lnmap = LineNumberMap()
    part.count_lines(lnmap)
    return '\n'.join(part.format(lnmap))

class LineNumberMap:
    "Tracks line-number changes and applies them to old line numbers."
    def __init__(self):
        self.input_lines = []
        self.output_positions = [0] # The line numbers where output is inserted
        self.fixups = [0]
        # self.fixups[i] is the count of all output lines preceding input lines
        # numbered in the range
        #   self.output_positions[i] < lineno <= self.output_positions[i+1]
        # Invariant:
        #   len(self.output_positions) == len(self.fixups)
        #   self.output_positions is sorted
    def add_input_line(self, line):
        self.input_lines.append(line)
    def get_input_line(self, lineno):
        """Tracebacks sometimes have None for the text of a line,
        so we have to supply it ourselves."""
        try: return self.input_lines[lineno - 1]
        except IndexError: return None
    def count_output(self, n_lines):
        self.output_positions.append(1 + len(self.input_lines))
        self.fixups.append(self.fixups[-1] + n_lines)
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
        return sum((part.format(lnmap) for part in self.parts), [])

class InputPart:
    "An input line, passed to the output unchanged."
    def __init__(self, text):
        self.text = text
    def count_lines(self, lnmap):
        lnmap.add_input_line(self.text)
    def format(self, lnmap):
        return [self.text]

class OutputPart:
    "Some output lines, with a #. prefix."
    def __init__(self, text):
        self.lines = text.splitlines()
    def count_lines(self, lnmap):
        lnmap.count_output(len(self.lines))
    def format(self, lnmap):
        return ['#. ' + line for line in self.lines]

class TracebackPart:
    """An output traceback with a #. prefix and with the stack frames
    corrected when they refer to the code being halped."""
    def __init__(self, tb_items):
        self.items = tb_items
    def count_lines(self, lnmap):
        def item_len(item):
            (filename, lineno, name, line) = item
            # XXX how to make sure this count is consistent with format_traceback()?
            if line: return 2
            else: return 1
        lnmap.count_output(sum(map(item_len, self.items)))
    def format(self, lnmap):
        def fix_item(item):
            (filename, lineno, name, line) = item
            if filename == '<string>':
                filename = source_filename
                line = lnmap.get_input_line(lineno)
                lineno = lnmap.fix_lineno(lineno)
            return (filename, lineno, name, line)
        return format_traceback(map(fix_item, self.items))

def format_traceback(tb_items):
    "Turn a list of traceback items into a string."
    return ['#. ' + line.rstrip('\n').replace('\n', '\n#. ')
            for line in traceback.format_list(tb_items)]


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
    if 2 <= len(sys.argv): source_filename = sys.argv[1]
    if 3 <= len(sys.argv): sys.path[0] = os.path.dirname(sys.argv[2])
    sys.stdout.write(halp(sys.stdin.read()))
