/*
  Implementation of the Shift-Or algorithm.

  This is based heavily on the code given in chapter 5 of the book, "Handbook
  of Exact String-Matching Algorithms," by Christian Charras and Thierry Lecroq.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "run.h"

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
WORD_TYPE calc_s_positions(unsigned char *pat, int m, WORD_TYPE s_positions[]) {
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
  Initialize the pattern given. Return a two-element array of the processed
  `s_positions` table and the value of `lim`. Note that once this pre-processing
  is done, the pattern itself is no longer needed.
*/
void **init_shift_or(unsigned char *pattern) {
  // Allocate one pointer-slot more than is needed, as the final NULL will be
  // the signal to the loop that is freeing memory.
  void **return_val = (void **)calloc(3, sizeof(void *));

  WORD_TYPE *lim = calloc(1, sizeof(WORD_TYPE));
  WORD_TYPE *s_positions = calloc(ASIZE, sizeof(WORD_TYPE));

  int m = strlen((const char *)pattern);

  if (m > WORD) {
    fprintf(stderr, "shift_or: pattern size must be <= %d\n", WORD);
    return 0;
  }

  /* Preprocessing */
  *lim = calc_s_positions(pattern, m, s_positions);

  // Save these values in the void** structure. The `shift_or` function will
  // unpack them in the same order, for use.
  return_val[0] = (void *)lim;
  return_val[1] = (void *)s_positions;

  return return_val;
}

/*
  Perform the Shift-Or algorithm on the given pattern of length m, against
  the sequence of length n.
*/
int shift_or(void **pat_data, unsigned char *sequence) {
  // Unpack pat_data:
  WORD_TYPE *lim = (WORD_TYPE *)pat_data[0];
  WORD_TYPE *s_positions = (WORD_TYPE *)pat_data[1];

  WORD_TYPE state;
  int matches = 0;
  int j;

  // Size of sequence. Pattern size not needed here.
  int n = strlen((const char *)sequence);

  /* Searching */
  for (state = ~0, j = 0; j < n; ++j) {
    state = (state << 1) | s_positions[sequence[j]];
    if (state < *lim) {
      matches++;
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
  int return_code = run(&init_shift_or, &shift_or, "shift_or", argc, argv);

  return return_code;
}
