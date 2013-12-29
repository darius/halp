"""
Prototype of a Sokoban game. It's missing the main program that
would load a starting board, read keys, update the screen, etc.; but
you can still test it interactively inside Halp, and that's how I
developed it. Here we see it at the point it's working and I've played
a whole game through. (And then I simplified the code.)
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
# initial board above, and the keystrokes line below was empty. Then I
# added a keystroke ('d') to the keystrokes line and hit M-i to
# evaluate, and it updated the board. Continuing with more keystrokes
# (making it 'dd', then 'ddl', 'ddlu', ...) and hitting M-i after each
# addition, I played the game (albeit clumsily). After the last M-i,
# the final line further below changed to 'WIN'. (You can keep hitting
# M-i with no change now because 'd' for down is blocked in this
# position.)

## keystrokes = halp.read(); print keystrokes,
#. ddlurrddrruullrdrdl
## board = transform(keystrokes, halp.read()); print board,
#. # # # # # # #
#. # @     #   #
#. #   @       #
#. #           #
#. #   @ @ i   #
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

def push((width, grid), direction):
    "Update board, trying to move the player in the direction."
    i = find_me(grid)
    d = direction((width, grid))
    move(grid, 'o@', i+d, i+d+d)
    move(grid, 'iI', i, i+d)

def find_me(grid):
    "Return the player's index in the board's array."
    return grid.index('i' if 'i' in grid else 'I')

def move(grid, thing, src, dst):
    "Move thing from src to dst if possible, or leave them unchanged."
    # N.B. dst is always in bounds when grid[src] in thing because our
    # boards have '#'-borders.
    if grid[src] in thing and grid[dst] in ' .':
        clear(grid, src)
        drop(grid, dst, thing)

def clear(grid, i):
    "Remove any thing (box or player) from position i."
    grid[i] = ' .'[grid[i] in '.@I']

def drop(grid, i, thing):
    "At a clear position, put thing."
    grid[i] = thing['.' == grid[i]]
