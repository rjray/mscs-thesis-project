/*
  Implementation of the Knuth-Morris-Pratt algorithm.

  This is based heavily on the code given in chapter 7 of the book, "Handbook
  of Exact String-Matching Algorithms," by Christian Charras and Thierry Lecroq.
*/

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>

#include "setup.h"

/*
  Simple measure of the wall-clock down the usec. Adapted from StackOverflow.
*/
double get_time() {
  struct timeval t;
  gettimeofday(&t, NULL);
  return t.tv_sec + t.tv_usec * 1e-6;
}

/*
  Initialize the jump-table that KMP uses.
*/
void init_kmp(char *pat, int m, int next_table[]) {
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
int kmp(char *pattern, int m, char *sequence, int n) {
  int i, j, *next_table;
  int matches = 0;

  // Set up the next_table array for the algorithm to use:
  next_table = (int *)calloc(m + 1, sizeof(int));
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
#ifdef DEBUG
      fprintf(stderr, "    Pattern found at location %d\n", j - i);
#endif // DEBUG
      i = next_table[i];
    }
  }

  free(next_table);
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

  // Read the three data files. Any of these that return 0 means an error. Any
  // error has already been reported to stderr.
  int sequences_count = read_sequences(sequences_file, &sequences_data);
  if (sequences_count == 0)
    exit(-1);
  int patterns_count = read_patterns(patterns_file, &patterns_data);
  if (patterns_count == 0)
    exit(-1);
  int answers_count = read_answers(answers_file, &answers_data);
  if (answers_count == 0)
    exit(-1);

  // Run it. For each sequence, try each pattern against it. The kmp() routine
  // will return the number of matches found, which will be compared to the
  // table of answers for that pattern. Report any mismatches.
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
      int matches = kmp(pattern_str, pattern_len, sequence_str, sequence_len);

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