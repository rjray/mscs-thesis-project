# The is the Makefile for the harness application.
#
# This is just two C modules, with one "local" header file and the header file
# `subprocess.h` that is used by `harness.c` for subprocess manipulation.

all: harness

CC=gcc

harness: harness.o rapl.o
	$(CC) -O2 -Wall -o harness harness.o rapl.o -lm

harness.o: harness.c rapl.h subprocess.h
	$(CC) -O2 -Wall -c harness.c

rapl.o: rapl.c rapl.h
	$(CC) -O2 -Wall -c rapl.c

clean:
	$(RM) *.o harness
