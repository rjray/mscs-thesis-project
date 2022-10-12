/*
  Header file for the runner module.
*/

#ifndef _RUN_HPP
#define _RUN_HPP

#include <string>
#include <variant>
#include <vector>

typedef std::variant<std::string, std::vector<int>, unsigned long,
                     std::vector<unsigned long>>
    PatternData;
typedef int (*algorithm)(std::vector<PatternData>, int, std::string, int);
typedef std::vector<PatternData> (*initializer)(std::string, int);

extern int run(initializer init, algorithm algo, std::string name, int argc,
               char *argv[]);

#endif // !_RUN_HPP
