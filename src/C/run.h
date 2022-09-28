/*
  Header file for the runner module.
*/

#ifndef _RUN_H
#define _RUN_H

typedef int (*runnable)(unsigned char *, int, unsigned char *, int);

extern int run(runnable algorithm, char *name, int argc, char *argv[]);

#endif // !_RUN_H
