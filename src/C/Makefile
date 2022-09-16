KMP_TARGETS := kmp-gcc kmp-llvm
BOYER_MOORE_TARGETS := boyer_moore-gcc boyer_moore-llvm

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

# Rules for building with LLVM:
run-llvm.o: run.c run.h setup.h
	$(CLANG) $(CFLAGS) -c -o run-llvm.o run.c

setup-llvm.o: setup.c setup.h
	$(CLANG) $(CFLAGS) -c -o setup-llvm.o setup.c

kmp-llvm.o: kmp.c
	$(CLANG) $(CFLAGS) -c -o kmp-llvm.o kmp.c

kmp-llvm: kmp-llvm.o run-llvm.o setup-llvm.o
	$(CLANG) $(CFLAGS) -o kmp-llvm kmp-llvm.o run-llvm.o setup-llvm.o

boyer_moore-llvm.o: boyer_moore.c
	$(CLANG) $(CFLAGS) -c -o boyer_moore-llvm.o boyer_moore.c

boyer_moore-llvm: boyer_moore-llvm.o run-llvm.o setup-llvm.o
	$(CLANG) $(CFLAGS) -o boyer_moore-llvm boyer_moore-llvm.o run-llvm.o setup-llvm.o
