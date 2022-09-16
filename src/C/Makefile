KMP_TARGETS := kmp-gcc kmp-clang
BOYER_MOORE_TARGETS := boyer_moore-gcc boyer_moore-clang

TARGETS := $(KMP_TARGETS) $(BOYER_MOORE_TARGETS)

CFLAGS=-g

GCC=gcc
CLANG=clang

all: $(TARGETS)

clean:
	$(RM) *.o
	$(RM) $(TARGETS)

# Rules for building with gcc:
setup-gcc.o: setup.c setup.h
	$(GCC) $(CFLAGS) -c -o setup-gcc.o setup.c

kmp-gcc.o: kmp.c setup.h
	$(GCC) $(CFLAGS) -c -o kmp-gcc.o kmp.c

kmp-gcc: kmp-gcc.o setup-gcc.o
	$(GCC) $(CFLAGS) -o kmp-gcc kmp-gcc.o setup-gcc.o

boyer_moore-gcc.o: boyer_moore.c setup.h
	$(GCC) $(CFLAGS) -c -o boyer_moore-gcc.o boyer_moore.c

boyer_moore-gcc: boyer_moore-gcc.o setup-gcc.o
	$(GCC) $(CFLAGS) -o boyer_moore-gcc boyer_moore-gcc.o setup-gcc.o

# Rules for building with clang:
setup-clang.o: setup.c setup.h
	$(CLANG) $(CFLAGS) -c -o setup-clang.o setup.c

kmp-clang.o: kmp.c setup.h
	$(CLANG) $(CFLAGS) -c -o kmp-clang.o kmp.c

kmp-clang: kmp-clang.o setup-clang.o
	$(CLANG) $(CFLAGS) -o kmp-clang kmp-clang.o setup-clang.o

boyer_moore-clang.o: boyer_moore.c setup.h
	$(CLANG) $(CFLAGS) -c -o boyer_moore-clang.o boyer_moore.c

boyer_moore-clang: boyer_moore-clang.o setup-clang.o
	$(CLANG) $(CFLAGS) -o boyer_moore-clang boyer_moore-clang.o setup-clang.o
