ALGORITHMS := kmp boyer_moore shift_or
GCC_TARGETS := kmp-gcc boyer_moore-gcc shift_or-gcc
LLVM_TARGETS := kmp-llvm boyer_moore-llvm shift_or-llvm

# Default this to unset
DEBUG=

# Determine CFLAGS based on DEBUG:
ifeq ($(DEBUG),)
CFLAGS=-O3
else
CFLAGS=-g
endif

GCC=gcc
CLANG=clang

all: gcc llvm

gcc: $(GCC_TARGETS)

llvm: $(LLVM_TARGETS)

clean:
	$(RM) *.o
	$(RM) $(GCC_TARGETS) $(LLVM_TARGETS)

# Rules for building with gcc:
run-gcc.o: run.c run.h setup.h
	$(GCC) $(CFLAGS) -c -o run-gcc.o run.c

setup-gcc.o: setup.c setup.h
	$(GCC) $(CFLAGS) -c -o setup-gcc.o setup.c

kmp-gcc.o: kmp.c run.h
	$(GCC) $(CFLAGS) -c -o kmp-gcc.o kmp.c

kmp-gcc: kmp-gcc.o run-gcc.o setup-gcc.o
	$(GCC) $(CFLAGS) -o kmp-gcc kmp-gcc.o run-gcc.o setup-gcc.o

boyer_moore-gcc.o: boyer_moore.c run.h
	$(GCC) $(CFLAGS) -c -o boyer_moore-gcc.o boyer_moore.c

boyer_moore-gcc: boyer_moore-gcc.o run-gcc.o setup-gcc.o
	$(GCC) $(CFLAGS) -o boyer_moore-gcc boyer_moore-gcc.o run-gcc.o setup-gcc.o

shift_or-gcc.o: shift_or.c run.h
	$(GCC) $(CFLAGS) -c -o shift_or-gcc.o shift_or.c

shift_or-gcc: shift_or-gcc.o run-gcc.o setup-gcc.o
	$(GCC) $(CFLAGS) -o shift_or-gcc shift_or-gcc.o run-gcc.o setup-gcc.o

# Rules for building with LLVM:
run-llvm.o: run.c run.h setup.h
	$(CLANG) $(CFLAGS) -c -o run-llvm.o run.c

setup-llvm.o: setup.c setup.h
	$(CLANG) $(CFLAGS) -c -o setup-llvm.o setup.c

kmp-llvm.o: kmp.c run.h
	$(CLANG) $(CFLAGS) -c -o kmp-llvm.o kmp.c

kmp-llvm: kmp-llvm.o run-llvm.o setup-llvm.o
	$(CLANG) $(CFLAGS) -o kmp-llvm kmp-llvm.o run-llvm.o setup-llvm.o

boyer_moore-llvm.o: boyer_moore.c run.h
	$(CLANG) $(CFLAGS) -c -o boyer_moore-llvm.o boyer_moore.c

boyer_moore-llvm: boyer_moore-llvm.o run-llvm.o setup-llvm.o
	$(CLANG) $(CFLAGS) -o boyer_moore-llvm boyer_moore-llvm.o run-llvm.o setup-llvm.o

shift_or-llvm.o: shift_or.c run.h
	$(CLANG) $(CFLAGS) -c -o shift_or-llvm.o shift_or.c

shift_or-llvm: shift_or-llvm.o run-llvm.o setup-llvm.o
	$(CLANG) $(CFLAGS) -o shift_or-llvm shift_or-llvm.o run-llvm.o setup-llvm.o
