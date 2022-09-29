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
void init_kmp(std::string pattern, int m, std::vector<int> &next_table) {
  std::string pat = pattern + "\0";
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

  return;
}

/*
  Perform the KMP algorithm on the given pattern of length m, against the
  sequence of length n.
*/
int kmp(std::string pattern, int m, std::string sequence, int n) {
  int i, j;
  int matches = 0;
  std::vector<int> next_table;

  // Set up the next_table array for the algorithm to use:
  next_table.reserve(m + 1);
  init_kmp(pattern, m, next_table);

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
  int return_code = run(&kmp, "kmp", argc, argv);

  return return_code;
}
