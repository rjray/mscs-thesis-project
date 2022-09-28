/*
  Header file for the runner module.
*/

#ifndef _RUN_HPP
#define _RUN_HPP

#include <string>

typedef int (*runnable)(std::string, int, std::string, int);

extern int run(runnable algorithm, std::string name, int argc, char *argv[]);

#endif // !_RUN_HPP
