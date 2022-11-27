/*
  Implementation of the Boyer-Moore algorithm.

  This is based heavily on the code given in chapter 14 of the book, "Handbook
  of Exact String-Matching Algorithms," by Christian Charras and Thierry Lecroq.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/param.h>

#include "run.h"

// Define the alphabet size, part of the Boyer-Moore pre-processing. Here, we
// are just using ASCII characters, so 128 is fine.
#define ASIZE 128

/*
  Preprocessing step: calculate the bad-character shifts.
*/
void calc_bad_char(unsigned char *pat, int m, int bad_char[]) {
  int i;
  for (i = 0; i < ASIZE; ++i)
    bad_char[i] = m;
  for (i = 0; i < m - 1; ++i)
    bad_char[pat[i]] = m - i - 1;

  return;
}

/*
  Preprocessing step: calculate suffixes for good-suffix shifts.
*/
void calc_suffixes(unsigned char *pat, int m, int suffix_list[]) {
  int f = 0, g, i;
  suffix_list[m - 1] = m;

  g = m - 1;
  for (i = m - 2; i >= 0; --i) {
    if (i > g && suffix_list[i + m - 1 - f] < i - g)
      suffix_list[i] = suffix_list[i + m - 1 - f];
    else {
      if (i < g)
        g = i;
      f = i;
      while (g >= 0 && pat[g] == pat[g + m - 1 - f])
        --g;
      suffix_list[i] = f - g;
    }
  }

  return;
}

/*
  Preprocessing step: calculate the good-suffix shifts.
*/
void calc_good_suffix(unsigned char *pat, int m, int good_suffix[]) {
  int i, j, *suffixes;
  suffixes = (int *)calloc(m, sizeof(int));

  calc_suffixes(pat, m, suffixes);

  for (i = 0; i < m; ++i)
    good_suffix[i] = m;
  j = 0;
  for (i = m - 1; i >= -1; --i)
    if (i == -1 || suffixes[i] == i + 1)
      for (; j < m - 1 - i; ++j)
        if (good_suffix[j] == m)
          good_suffix[j] = m - 1 - i;
  for (i = 0; i <= m - 2; ++i)
    good_suffix[m - 1 - suffixes[i]] = m - 1 - i;

  free(suffixes);
  return;
}

/*
  Initialize the pattern data for the given pattern. This will return a void**
  structure with the elements that the actual `boyer_moore` function will need
  to find matches.
*/
void **init_boyer_moore(unsigned char *pattern) {
  // Allocate one pointer-slot more than is needed, as the final NULL will be
  // the signal to the loop that is freeing memory.
  void **return_val = (void **)calloc(4, sizeof(void *));
  int m = strlen((const char *)pattern);
  // Allocate space for the good-suffix/bad-char tables:
  int *good_suffix = (int *)calloc(m, sizeof(int));
  int *bad_char = (int *)calloc(ASIZE, sizeof(int));

  /* Preprocessing */
  calc_good_suffix(pattern, m, good_suffix);
  calc_bad_char(pattern, m, bad_char);

  // Save these three values in the void** structure. The `boyer_moore`
  // function will unpack them in the same order, for use.
  return_val[0] = (void *)strdup((const char *)pattern);
  return_val[1] = (void *)good_suffix;
  return_val[2] = (void *)bad_char;

  return return_val;
}

/*
  Perform the Boyer-Moore algorithm on the given pattern of length m,
  against the sequence of length n.
*/
int boyer_moore(void **pat_data, unsigned char *sequence) {
  int i, j;

  // Unpack pat_data:
  unsigned char *pattern = (unsigned char *)pat_data[0];
  int *good_suffix = (int *)pat_data[1];
  int *bad_char = (int *)pat_data[2];

  int matches = 0;

  // Sizes of pattern and sequence.
  int m = strlen((const char *)pattern);
  int n = strlen((const char *)sequence);

  // Perform the searching:
  j = 0;
  while (j <= n - m) {
    for (i = m - 1; i >= 0 && pattern[i] == sequence[i + j]; --i)
      ;
    if (i < 0) {
      matches++;
      j += good_suffix[0];
    } else {
      j += MAX(good_suffix[i], bad_char[sequence[i + j]] - m + 1 + i);
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
  int return_code =
      run(&init_boyer_moore, &boyer_moore, "boyer_moore", argc, argv);

  return return_code;
}
