TARGETS := kmp-gcc kmp-clang

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

# Rules for building with clang:
setup-clang.o: setup.c setup.h
	$(CLANG) $(CFLAGS) -c -o setup-clang.o setup.c

kmp-clang.o: kmp.c setup.h
	$(CLANG) $(CFLAGS) -c -o kmp-clang.o kmp.c

kmp-clang: kmp-clang.o setup-clang.o
	$(CLANG) $(CFLAGS) -o kmp-clang kmp-clang.o setup-clang.o
