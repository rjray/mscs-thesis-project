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
run-gcc.o: run.c run.h setup.h
	$(GCC) $(CFLAGS) -c -o run-gcc.o run.c

setup-gcc.o: setup.c setup.h
	$(GCC) $(CFLAGS) -c -o setup-gcc.o setup.c

kmp-gcc.o: kmp.c
	$(GCC) $(CFLAGS) -c -o kmp-gcc.o kmp.c

kmp-gcc: kmp-gcc.o run-gcc.o setup-gcc.o
	$(GCC) $(CFLAGS) -o kmp-gcc kmp-gcc.o run-gcc.o setup-gcc.o

boyer_moore-gcc.o: boyer_moore.c
	$(GCC) $(CFLAGS) -c -o boyer_moore-gcc.o boyer_moore.c

boyer_moore-gcc: boyer_moore-gcc.o run-gcc.o setup-gcc.o
	$(GCC) $(CFLAGS) -o boyer_moore-gcc boyer_moore-gcc.o run-gcc.o setup-gcc.o

# Rules for building with clang:
run-clang.o: run.c run.h setup.h
	$(CLANG) $(CFLAGS) -c -o run-clang.o run.c

setup-clang.o: setup.c setup.h
	$(CLANG) $(CFLAGS) -c -o setup-clang.o setup.c

kmp-clang.o: kmp.c
	$(CLANG) $(CFLAGS) -c -o kmp-clang.o kmp.c

kmp-clang: kmp-clang.o run-clang.o setup-clang.o
	$(CLANG) $(CFLAGS) -o kmp-clang kmp-clang.o run-clang.o setup-clang.o

boyer_moore-clang.o: boyer_moore.c
	$(CLANG) $(CFLAGS) -c -o boyer_moore-clang.o boyer_moore.c

boyer_moore-clang: boyer_moore-clang.o run-clang.o setup-clang.o
	$(CLANG) $(CFLAGS) -o boyer_moore-clang boyer_moore-clang.o run-clang.o setup-clang.o
