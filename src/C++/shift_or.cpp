/*
  Implementation of the Shift-Or algorithm.

  This is based heavily on the code given in chapter 5 of the book, "Handbook
  of Exact String-Matching Algorithms," by Christian Charras and Thierry Lecroq.
*/

#include <iostream>
#include <string>
#include <vector>

#include "run.hpp"

// Define the alphabet size, part of the Shift-Or pre-processing. Here, we
// are just using ASCII characters, so 128 is fine.
#define ASIZE 128

// We need to also know the word size in bits. For this, we're going to use
// `unsigned long` values. This allows a search pattern of up to 64 characters,
// even though the experimental data doesn't go nearly this high. This is a
// sort of "insurance" against adding other experiments that might push this
// limit.
#define WORD 64
#define WORD_TYPE unsigned long

/*
  Preprocessing step: Calculate the positions of each character of the
  alphabet within the pattern `pat`.
*/
WORD_TYPE calc_s_positions(std::string pat, int m,
                           std::vector<WORD_TYPE> &s_positions) {
  WORD_TYPE j, lim;
  int i;

  for (i = 0; i < ASIZE; ++i)
    s_positions[i] = ~0;
  for (lim = i = 0, j = 1; i < m; ++i, j <<= 1) {
    s_positions[pat[i]] &= ~j;
    lim |= j;
  }
  lim = ~(lim >> 1);

  return lim;
}

/*
  Perform the Shift-Or algorithm on the given pattern of length m, against
  the sequence of length n.
*/
int shift_or(std::string pattern, int m, std::string sequence, int n) {
  WORD_TYPE lim, state;
  std::vector<WORD_TYPE> s_positions;
  int matches = 0;
  int j;
  s_positions.reserve(ASIZE);

  if (m > WORD) {
    std::cerr << "shift_or: pattern size must be <= " << WORD << "\n";
    return 0;
  }

  /* Preprocessing */
  lim = calc_s_positions(pattern, m, s_positions);

  /* Searching */
  for (state = ~0, j = 0; j < n; ++j) {
    state = (state << 1) | s_positions[sequence[j]];
    if (state < lim)
      matches++;
  }

  return matches;
}

/*
  All that is done here is call the run() function with a pointer to the
  algorithm implementation, the label for the algorithm, and the argc/argv
  values.
*/
int main(int argc, char *argv[]) {
  int return_code = run(&shift_or, "shift_or", argc, argv);

  return return_code;
}
