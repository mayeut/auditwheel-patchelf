.PHONY: all clean

all: libfoo.so.1 foo

libfoo.so.1: source.c
	gcc -fPIC -shared -Wl,-soname,$@ -Wl,-rpath,/opt/foo/lib -Wl,-rpath,'$$ORIGIN' -o $@ $< -lm -lc
	#readelf -a $@

foo: source.c
	gcc -fPIC -o $@ $< -lm -lc
	#readelf -a $@

clean:
	-rm *foo*

#-soname
#
