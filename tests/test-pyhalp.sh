python ../pyhalp.py <../sample.py >tmp &&
diff -u expected.sample.py tmp &&

python ../pyhalp.py </dev/null >tmp &&
diff -u /dev/null tmp &&

true
