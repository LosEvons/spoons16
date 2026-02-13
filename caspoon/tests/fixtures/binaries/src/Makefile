CC=gcc
CFLAGS=-Wall

all: test_hello_x64 test_hello_x86 test_stripped test_with_pie

test_hello_x64: hello_world.c
	$(CC) $(CFLAGS) -o ../test_hello_x64 hello_world.c

test_hello_x86: hello_world.c
	$(CC) $(CFLAGS) -m32 -o ../test_hello_x86 hello_world.c 2>/dev/null || echo "32-bit compilation not available"

test_stripped: hello_world.c
	$(CC) $(CFLAGS) -s -o ../test_stripped hello_world.c

test_with_pie: hello_world.c
	$(CC) $(CFLAGS) -fPIE -pie -fstack-protector-all -Wl,-z,relro,-z,now -o ../test_with_pie hello_world.c

clean:
	rm -f ../test_hello_x64 ../test_hello_x86 ../test_stripped ../test_with_pie

.PHONY: all clean
