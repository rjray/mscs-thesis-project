/*
  Header file for the runner module.
*/

#ifndef _RUN_H
#define _RUN_H

// Typedefs for the function-pointer signatures, and the extern definition of,
// the single-pattern, exact-matching runner.
typedef int (*algorithm)(void **, unsigned char *);
typedef void **(*initializer)(unsigned char *);
extern int run(initializer init, algorithm algo, char *name, int argc,
               char *argv[]);

// Typedefs for the function-pointer signatures, and the extern definition of,
// the multi-pattern, exact-matching runner.
typedef int *(*mp_algorithm)(void **, unsigned char *);
typedef void **(*mp_initializer)(unsigned char **, int);
extern int run_multi(mp_initializer init, mp_algorithm algo, char *name,
                     int argc, char *argv[]);

// Typedefs for the function-pointer signatures, and the extern definition of,
// the single-pattern, approximate-matching runner.
typedef int (*am_algorithm)(void **, unsigned char *);
typedef void **(*am_initializer)(unsigned char *, int);
extern int run_approx(am_initializer init, am_algorithm algo, char *name,
                      int argc, char *argv[]);

#endif // !_RUN_H
