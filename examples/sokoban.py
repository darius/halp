"""
Prototype of a Sokoban game. It's missing the main program that
would load a starting board, read keys, update the screen, etc.; but
you can still test it interactively inside Halp, and that's how I
developed it. Here we see it at the point it's working and I've played
a whole game through.
"""

# Read an initial board state, and display it -- should leave it unchanged:

## print unparse(parse(halp.read())),
#. # # # # # # #
#. # . i   #   #
#. # o @   o   #
#. #       o   #
#. #   . .     #
#. #     @     #
#. # # # # # # #

# Below, I play through a game. At first the board was a copy of the
# initial board above, and the keystrokes line was empty. Then I added
# a keystroke ('d') and hit M-i to evaluate, and it updated the
# board. Continuing with more keystrokes (making it 'dd', then 'ddl',
# 'ddlu', ...) and hitting M-i after each addition, I played the game
# (albeit clumsily). After the last M-i, the final line below changed
# to 'WIN'. (You can keep hitting M-i with no change at this point because
# 'd' for down is blocked in this position.)

## keystrokes = halp.read(); print keystrokes,
#. ddlurrddrruullrrdluld
## board = transform(keystrokes, halp.read()); print board,
#. # # # # # # #
#. # @     #   #
#. #   @       #
#. #     i     #
#. #   @ @     #
#. #     @     #
#. # # # # # # #

## print ('' if 'o' in board else 'WIN'),
#. WIN

def transform(keystrokes, board):
    "Scaffolding for the above Halp stuff."
    b = parse(board)
    push(b, cmds[keystrokes[-1:]])
    return unparse(b)

# The Sokoban program proper

def parse(board):
    lines = [line.strip() for line in board.splitlines()]
    assert lines and all(len(line) == len(lines[0]) for line in lines)
    return len(lines[0]), list(''.join(lines))

def unparse((width, grid)):
    return '\n'.join(''.join(grid[i:i+width])
                     for i in range(0, len(grid), width))

def up   ((width, grid)): return -width
def down ((width, grid)): return  width
def left ((width, grid)): return -2
def right((width, grid)): return  2

cmds = dict(u=up, d=down, l=left, r=right)

def push(board, dir):
    "Update board, trying to move the actor in the direction."
    d = dir(board)
    _, grid = board
    g = ''.join(grid)
    i = find_me(g)
    a, b, c = push_squares(g[i], g[i+d], g[i+2*d:i+2*d+1])
    grid[i], grid[i+d], grid[i+2*d:i+2*d+1] = a, b, c

def find_me(g):
    "Return the actor's index in the board's array."
    return g.index('i' if 'i' in g else 'I')

def push_squares(a, b, c):
    """Given the actor, its neighbor in the direction to move, and the
    next square in that direction, return new values for the same
    squares after trying to move."""
    b, c = move(block, b, c)
    a, b = move(me, a, b)
    return a, b, c

def move(thing, src, dst):
    "Move thing from src to dst if possible, or leave them unchanged."
    if has(thing, src) and has(space, dst):
        src, dst = lift(thing, src), drop(thing, dst)
    return src, dst

space = (' ', '.')
block = ('o', '@')
me    = ('i', 'I')

def has ((on_space, on_target), s): return s in (on_space, on_target)
def lift((on_space, on_target), s): return {on_space: ' ', on_target: '.'}[s]
def drop((on_space, on_target), s): return {' ': on_space, '.': on_target}[s]