/*
  Header file for the runner module.
*/

#ifndef _RUN_HPP
#define _RUN_HPP

#include <set>
#include <string>
#include <variant>
#include <vector>

typedef std::variant<std::string, std::vector<int>, unsigned long,
                     std::vector<unsigned long>>
    PatternData;
typedef int (*algorithm)(std::vector<PatternData>, std::string);
typedef std::vector<PatternData> (*initializer)(std::string);
extern int run(initializer init, algorithm algo, std::string name, int argc,
               char *argv[]);

typedef std::variant<int, std::vector<int>, std::vector<std::vector<int>>,
                     std::vector<std::set<int>>>
    MultiPatternData;
typedef std::vector<int> (*mp_algorithm)(std::vector<MultiPatternData>,
                                         std::string);
typedef std::vector<MultiPatternData> (*mp_initializer)(
    std::vector<std::string>);
extern int run_multi(mp_initializer init, mp_algorithm algo, std::string name,
                     int argc, char *argv[]);

#endif // !_RUN_HPP
