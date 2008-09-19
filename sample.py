# To use Halp, edit an ordinary Python source file like this one.

def fact(n):
    if n <= 0:
        return 1
    else:
        return n * fact(n - 1)

# Given comments starting with '## ' like this:
## 2 + 3

# Halp will evaluate them when you hit M-i, and insert their value
# below them in another comment (but prefixed with '#. ' instead. Try
# it now. You should see '#. 5' appear below the line above, and
# '#. 120' appear below the following line:

## fact(2 + 3)

# If you want, you can make those lines go away by hitting Undo. But
# you need not; since the outputs are comments they can be left in
# place, where the next M-i will replace them with any new results.

# Your ## lines can be statements, too:

## print 'hello\nworld'

# If they raise exceptions, a traceback appears:

## fact('notanumber')

# If there's an error loading this source file (never mind the ##
# lines) you'll get an error message inserted right at the point of
# the error, and no attempt to evaluate ## lines. You can see this
# happening by uncommenting the following line:

#foo

# Finally, you can make the output a function of the previous
# output using halp.read(). This makes it possible to make a 
# program's source code the 'user interface' to the program.

## 2 * int(halp.read())
#. 1
