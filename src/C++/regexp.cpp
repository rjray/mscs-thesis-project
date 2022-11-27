/*
  C++ implementation of the (tentatively-titled) DFA-Gap algorithm for
  approximate string matching, regular expression version.
*/

#include <regex>
#include <sstream>
#include <string>
#include <vector>

/*
  This file comes from the GitHub repo: https://github.com/jpcre2/jpcre2
*/
#include "jpcre2.hpp"
#include "run.hpp"
typedef jpcre2::select<char> jp;

jp::Regex re;

/*
  Initialize the pattern given. This is a break from the usual init/algorithm
  pattern, because adding the jp::Regex type to one of the std::variant defs
  in `run.hpp` would have required all algorithm experiments to link against
  the PCRE2 library. So, for here, I just use a global.
*/
std::vector<ApproxPatternData> init_regexp(std::string const &pattern, int k) {
  std::vector<ApproxPatternData> return_val;
  return_val.reserve(1);

  std::ostringstream re_buf;
  re_buf << "(?=(" << pattern[0];
  for (unsigned int i = 1; i < pattern.length(); i++) {
    re_buf << "[^" << pattern[i] << "]{0," << k << "}" << pattern[i];
  }
  re_buf << "))";

  re.setPattern(re_buf.str()).compile();

  return return_val;
}

/*
  Perform the DFA-Gap-Regexp algorithm on the given (processed) pattern against
  the given sequence.
*/
int regexp(std::vector<ApproxPatternData> const &pat_data,
           std::string const &sequence) {
  // The pat_data vector is not actually used in this instance.
  jp::VecNum match_vec;
  jp::RegexMatch matcher;

  size_t matches = matcher.setRegexObject(&re)
                       .setSubject(&sequence)
                       .addModifier("g")
                       .setNumberedSubstringVector(&match_vec)
                       .match();

  return (int)matches;
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
