#!/usr/bin/env python
"""
Run a Halp-extended .py sourcefile from stdin; write to stdout the
same sourcefile with evaluation results placed inline.
"""

import sys
import traceback


# Evaluation

halp_filename = '<string>'   # Default

def halp(module_text):
    """Given a module's code as a string, produce the Halp output as a
    string."""
    input = [line for line in module_text.split('\n')
             if not line.startswith('#| ')]
    return format_part(eval_module(input))

def eval_module(input):
    """Given a module's code as a list of lines, produce the Halp
    output as a 'part'."""
    if halp_filename.endswith('.py'):
        module_name = halp_filename[:-3]
    else:
        module_name = '<string>'
    module_dict = {'__name__': module_name,
                   '__file__': halp_filename,
                   '__doc__': None}
    try:
        exec '\n'.join(input) in module_dict
    except:
        lineno = get_lineno(sys.exc_info())
        parts = map(InputPart, input)
        parts.insert(lineno, format_exc()) # XXX could fail if lineno bad
    else:
        parts = []
        for line in input:
            parts.append(InputPart(line))
            if line.startswith('## '):
                code = line[len('## '):]
                opt_part = eval_line(code, module_dict)
                if opt_part is not None:
                    parts.append(opt_part)
    return CompoundPart(parts)

def eval_line(code, module_dict):
    """Given a string that may be either an expression or a statement,
    evaluate it and return a part for output, or None."""
    try:
        return OutputPart(repr(eval(code, module_dict)))
    except SyntaxError:
        try:
            exec code in module_dict
            return None
        except:
            return format_exc()
    except:
        return format_exc()


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
             # [1:] drops the top frame (which is Halp internals)
             TracebackPart(traceback.extract_tb(tb, limit)[1:]),
             OutputPart(exc_only)]
    return CompoundPart(parts)

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
    # TODO: faster algorithm
    def __init__(self):
        self.input_lines = []
        self.inserts = []
    def add_input_line(self, line):
        self.input_lines.append(line)
    def get_input_line(self, lineno):
        try:
            return self.input_lines[lineno - 1]
        except IndexError:
            return None
    def count_output(self, n_lines):
        self.inserts.append((1 + len(self.input_lines), n_lines))
    def fix_lineno(self, lineno):
        delta = sum(n for (i, n) in self.inserts if i < lineno)
        return lineno + delta

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
    "Some output lines, with a #| prefix."
    def __init__(self, text):
        self.text = text
    def count_lines(self, lnmap):
        lnmap.count_output(1 + self.text.count('\n'))
    def format(self, lnmap):
        return format_result(self.text)

class TracebackPart:
    """An output traceback with a #| prefix and with the stack frames
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
    "Prefix each line of s with '#| '."
    return '#| %s' % s.replace('\n', '\n#| ')

def format_traceback(tb_items):
    "Turn a list of traceback items into a string."
    return ''.join(traceback.format_list(tb_items)).rstrip('\n')


# Main program

if __name__ == '__main__':
    if 2 <= len(sys.argv):
        halp_filename = sys.argv[1]
    sys.stdout.write(halp(sys.stdin.read()))
