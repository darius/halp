v8halp: v8halp.cc libv8.a
	g++ -Iinclude v8halp.cc  -o v8halp libv8.a -lpthread
