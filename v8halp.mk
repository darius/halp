v8halp: v8halp.cc libv8.a
	g++ -m32 -Iinclude v8halp.cc  -o v8halp libv8.a -lpthread
