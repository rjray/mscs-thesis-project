/*
  C++ implementation of the (tentatively-titled) DFA-Gap algorithm for
  approximate string matching, regular expression version.
*/

#include <iterator>
#include <regex>
#include <sstream>
#include <string>
#include <vector>

#include "run.hpp"

/*
  Initialize the pattern given. Return a single-element vector of the regexp
  from processing the pattern. The original pattern will not be needed for
  matching.
*/
std::vector<ApproxPatternData> init_regexp(std::string const &pattern, int k) {
  std::vector<ApproxPatternData> return_val;
  return_val.reserve(1);

  std::ostringstream re;
  re << "(?=" << pattern[0];
  for (unsigned int i = 1; i < pattern.length(); i++) {
    re << "[^" << pattern[i] << "]{0," << k << "}" << pattern[i];
  }
  re << ")";

  std::regex regexp(re.str());
  return_val.push_back(regexp);

  return return_val;
}

/*
  Perform the DFA-Gap algorithm on the given (processed) pattern against the
  given sequence.
*/
int regexp(std::vector<ApproxPatternData> const &pat_data,
           std::string const &sequence) {
  // Unpack pat_data:
  auto const &re = std::get<std::regex>(pat_data[0]);

  auto matches_begin =
      std::sregex_iterator(sequence.begin(), sequence.end(), re);
  auto matches_end = std::sregex_iterator();
  int matches = std::distance(matches_begin, matches_end);

  return matches;
}

/*
  All that is done here is call the run_approx() function with a pointer to the
  algorithm initializer, a pointer to the algorithm implementation, the label
  for the algorithm, and the argc/argv values.
*/
int main(int argc, char *argv[]) {
  int return_code = run_approx(&init_regexp, &regexp, "regexp", argc, argv);

  return return_code;
}
