/*
  Header file for the runner module.
*/

#ifndef _RUN_H
#define _RUN_H

typedef int (*algorithm)(void **, int, unsigned char *, int);
typedef void **(*initializer)(unsigned char *, int);

extern int run(initializer init, algorithm algo, char *name, int argc,
               char *argv[]);

#endif // !_RUN_H
