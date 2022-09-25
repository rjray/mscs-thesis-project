all: harness

CC=gcc

harness: harness.o rapl.o
	$(CC) -O2 -Wall -o harness harness.o rapl.o -lm

harness.o: harness.c
	$(CC) -O2 -Wall -c harness.c

rapl.o: rapl.c rapl.h
	$(CC) -O2 -Wall -c rapl.c

clean:
	$(RM) *.o harness
