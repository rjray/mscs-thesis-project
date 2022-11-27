/*
  Implementation of the Knuth-Morris-Pratt algorithm.

  This is based heavily on the code given in chapter 7 of the book, "Handbook
  of Exact String-Matching Algorithms," by Christian Charras and Thierry Lecroq.
*/

#include <string>
#include <vector>

#include "run.hpp"

/*
  Initialize the jump-table that KMP uses.
*/
void make_next_table(std::string const &pat, int m,
                     std::vector<int> &next_table) {
  int i, j;

  i = 0;
  j = next_table[0] = -1;

  while (i < m) {
    while (j > -1 && pat[i] != pat[j])
      j = next_table[j];
    i++;
    j++;
    if (pat[i] == pat[j])
      next_table[i] = next_table[j];
    else
      next_table[i] = j;
  }
}

/*
  Initialize the structure for Knuth-Morris-Pratt. Here, that means setting up
  the `next_table` array. The return value is a vector of the `PatternData`
  type, which is a type-safe union of sorts that covers the different types
  that have to be returned.
*/
std::vector<PatternData> init_kmp(std::string const &pattern) {
  std::vector<PatternData> return_val;
  return_val.reserve(2);
  int m = pattern.length();
  // Set up the next_table array for the algorithm to use:
  std::vector<int> next_table(m + 1, 0);
  // Set up a copy of pattern, with the sentinel character added:
  std::string pat(pattern + "\0");
  make_next_table(pat, m, next_table);

  return_val.push_back(pat);
  return_val.push_back(next_table);

  return return_val;
}

/*
  Perform the KMP algorithm on the given pattern of length m, against the
  sequence of length n.
*/
int kmp(std::vector<PatternData> const &pat_data, std::string const &sequence) {
  int i, j;
  int matches = 0;

  // Unpack pat_data:
  auto const &pattern = std::get<std::string>(pat_data[0]);
  auto const &next_table = std::get<std::vector<int>>(pat_data[1]);

  // Get the size of the pattern and the sequence.
  int m = pattern.length();
  int n = sequence.length();

  // Perform the searching:
  i = j = 0;
  while (j < n) {
    while (i > -1 && pattern[i] != sequence[j])
      i = next_table[i];

    i++;
    j++;
    if (i >= m) {
      matches++;
      i = next_table[i];
    }
  }

  return matches;
}

/*
  All that is done here is call the run() function with a pointer to the
  algorithm implementation, the label for the algorithm, and the argc/argv
  values.
*/
int main(int argc, char *argv[]) {
  int return_code = run(&init_kmp, &kmp, "kmp", argc, argv);

  return return_code;
}
