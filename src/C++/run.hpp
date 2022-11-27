/*
  Header file for the runner module.
*/

#ifndef _RUN_HPP
#define _RUN_HPP

#include <regex>
#include <set>
#include <string>
#include <variant>
#include <vector>

// Typedefs for the function-pointer signatures, and the extern definition of,
// the single-pattern, exact-matching runner.
typedef std::variant<std::string, std::vector<int>, unsigned long,
                     std::vector<unsigned long>>
    PatternData;
typedef int (*algorithm)(std::vector<PatternData> const &, std::string const &);
typedef std::vector<PatternData> (*initializer)(std::string const &);
extern int run(initializer init, algorithm algo, std::string name, int argc,
               char *argv[]);

// Typedefs for the function-pointer signatures, and the extern definition of,
// the multi-pattern, exact-matching runner.
typedef std::variant<int, std::vector<int>, std::vector<std::vector<int>>,
                     std::vector<std::set<int>>>
    MultiPatternData;
typedef std::vector<int> (*mp_algorithm)(std::vector<MultiPatternData> const &,
                                         std::string const &);
typedef std::vector<MultiPatternData> (*mp_initializer)(
    std::vector<std::string> const &);
extern int run_multi(mp_initializer init, mp_algorithm algo, std::string name,
                     int argc, char *argv[]);

// Typedefs for the function-pointer signatures, and the extern definition of,
// the single-pattern, approximate-matching runner.
typedef std::variant<int, std::vector<std::vector<int>>, void *>
    ApproxPatternData;
typedef int (*am_algorithm)(std::vector<ApproxPatternData> const &,
                            std::string const &);
typedef std::vector<ApproxPatternData> (*am_initializer)(std::string const &,
                                                         int);
extern int run_approx(am_initializer init, am_algorithm algo, std::string name,
                      int argc, char *argv[]);

#endif // !_RUN_HPP
