/*
  Implementation of the Boyer-Moore algorithm.

  This is based heavily on the code given in chapter 14 of the book, "Handbook
  of Exact String-Matching Algorithms," by Christian Charras and Thierry Lecroq.
*/

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/param.h>
#include <sys/time.h>

#include "setup.h"

// Define the alphabet size, part of the Boyer-Moore pre-processing. Here, we
// are just using ASCII characters, so 128 is fine.
#define ASIZE 128

/*
  Simple measure of the wall-clock down to the usec. Adapted from StackOverflow.
*/
double get_time() {
  struct timeval t;
  gettimeofday(&t, NULL);
  return t.tv_sec + t.tv_usec * 1e-6;
}

/*
  Preprocessing step: calculate the bad-character shifts.
*/
void calc_bad_char(char *pat, int m, int bad_char[]) {
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
void calc_suffixes(char *pat, int m, int suffix_list[]) {
  int f, g, i;
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
void calc_good_suffix(char *pat, int m, int good_suffix[]) {
  int i, j, *suffixes;
  suffixes = (int *)calloc(strlen(pat), sizeof(int));

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
  Perform the Boyer-Moore algorithm on the given pattern of length m, against
  the sequence of length n.
*/
int boyer_moore(char *pattern, int m, char *sequence, int n) {
  int i, j, *good_suffix, *bad_char;
  int matches = 0;

  // Allocate space for the good-suffix/bad-char tables:
  good_suffix = (int *)calloc(strlen(pattern), sizeof(int));
  bad_char = (int *)calloc(ASIZE, sizeof(int));

  /* Preprocessing */
  calc_good_suffix(pattern, m, good_suffix);
  calc_bad_char(pattern, m, bad_char);

  // Perform the searching:
  j = 0;
  while (j <= n - m) {
    for (i = m - 1; i >= 0 && pattern[i] == sequence[i + j]; --i)
      ;
    if (i < 0) {
      matches++;
#ifdef DEBUG
      fprintf(stderr, "    Pattern found at location %d\n", j);
#endif // DEBUG
      j += good_suffix[0];
    } else {
      j += MAX(good_suffix[i], bad_char[sequence[i + j]] - m + 1 + i);
    }
  }

  free(good_suffix);
  free(bad_char);
  return matches;
}

int main(int argc, char *argv[]) {
  if (argc != 4) {
    fprintf(stderr, "Usage: %s <sequences> <patterns> <answers>\n", argv[0]);
    exit(-1);
  }

  // The filenames are in the order: sequences patterns answers
  const char *sequences_file = argv[1];
  const char *patterns_file = argv[2];
  const char *answers_file = argv[3];

  // These will be alloc'd by the routines that read the files.
  char **sequences_data, **patterns_data;
  int **answers_data;

  // Read the three data files. Any of these that return 0 means an error.
  // Any error has already been reported to stderr.
  int sequences_count = read_sequences(sequences_file, &sequences_data);
  if (sequences_count == 0)
    exit(-1);
  int patterns_count = read_patterns(patterns_file, &patterns_data);
  if (patterns_count == 0)
    exit(-1);
  int answers_count = read_answers(answers_file, &answers_data);
  if (answers_count == 0)
    exit(-1);

  // Run it. For each sequence, try each pattern against it. The kmp()
  // routine will return the number of matches found, which will be compared
  // to the table of answers for that pattern. Report any mismatches.
  double start_time = get_time();
  int return_code = 0; // Used for noting that some number of matches failed
  for (int sequence = 0; sequence < sequences_count; sequence++) {
#ifdef DEBUG
    fprintf(stderr, "Starting sequence #%d:\n", sequence + 1);
#endif // DEBUG
    char *sequence_str = sequences_data[sequence];
    int sequence_len = strlen(sequence_str);

    for (int pattern = 0; pattern < patterns_count; pattern++) {
#ifdef DEBUG
      fprintf(stderr, "  Starting pattern #%d:\n", pattern + 1);
#endif // DEBUG
      char *pattern_str = patterns_data[pattern];
      int pattern_len = strlen(pattern_str);
      int matches =
          boyer_moore(pattern_str, pattern_len, sequence_str, sequence_len);

      if (matches != answers_data[pattern][sequence]) {
        fprintf(stderr, "Pattern %d mismatch against sequences %d (%d != %d)\n",
                pattern + 1, sequence + 1, matches,
                answers_data[pattern][sequence]);
        return_code = -1;
      }
    }
  }
  // Note the end time, before freeing memory.
  double end_time = get_time();
  fprintf(stdout, "%.6g\n", end_time - start_time);

  // Free all the memory that was allocated by the routines in setup.c:
  for (int i = 0; i < patterns_count; i++) {
    free(patterns_data[i]);
    free(answers_data[i]);
  }
  free(patterns_data);
  free(answers_data);
  for (int i = 0; i < sequences_count; i++)
    free(sequences_data[i]);
  free(sequences_data);

  exit(return_code);
}