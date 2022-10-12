/*
  Header file for the runner module.
*/

#ifndef _RUN_HPP
#define _RUN_HPP

#include <string>
#include <vector>

union PatternData {
  std::string str;
  std::vector<int> vec;
  unsigned long ul;
};

typedef int (*algorithm)(std::vector<PatternData>, int, std::string, int);
typedef std::vector<PatternData> (*initializer)(std::string, int);

extern int run(initializer init, algorithm algo, std::string name, int argc,
               char *argv[]);

#endif // !_RUN_HPP
