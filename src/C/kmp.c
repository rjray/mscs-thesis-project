/*
  Implementation of the Knuth-Morris-Pratt algorithm.

  This is based heavily on the code given in chapter 7 of the book, "Handbook
  of Exact String-Matching Algorithms," by Christian Charras and Thierry Lecroq.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "run.h"

/*
  Initialize the jump-table that KMP uses.
*/
void make_next_table(unsigned char *pat, int m, int next_table[]) {
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
  Initialize the pattern given. Return a two-element array of the processed
  pattern and the `next_table`.
*/
void **init_kmp(unsigned char *pattern) {
  // Allocate one pointer-slot more than is needed, as the final NULL will be
  // the signal to the loop that is freeing memory.
  void **return_val = (void **)calloc(3, sizeof(void *));

  // Set up the next_table array for the algorithm to use:
  int m = strlen((const char *)pattern);
  int *next_table = (int *)calloc(m + 1, sizeof(int));
  make_next_table(pattern, m, next_table);

  // Save these values in the void** structure. The `kmp` function will unpack
  // them in the same order, for use.
  return_val[0] = (void *)strdup((const char *)pattern);
  return_val[1] = (void *)next_table;

  return return_val;
}

/*
  Perform the KMP algorithm on the given pattern of length m, against the
  sequence of length n.
*/
int kmp(void **pat_data, unsigned char *sequence) {
  int i, j;

  // Unpack pat_data:
  unsigned char *pattern = (unsigned char *)pat_data[0];
  int *next_table = (int *)pat_data[1];

  int matches = 0;

  // Sizes of pattern and sequence.
  int m = strlen((const char *)pattern);
  int n = strlen((const char *)sequence);

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
