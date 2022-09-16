/*
  This is the "runner" module. It provides the function that will handle running
  an experiment.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>

#include "run.h"
#include "setup.h"

#if defined(__llvm__)
#define LANG "c-llvm"
#elif defined(__GNUC__)
#define LANG "c-gcc"
#endif

/*
  Simple measure of the wall-clock down to the usec. Adapted from StackOverflow.
*/
double get_time() {
  struct timeval t;
  gettimeofday(&t, NULL);
  return t.tv_sec + t.tv_usec * 1e-6;
}

/*
  The "runner" function. This takes a pointer to an algorithm implementation,
  the name of the algorithm, argc and argv from the invocation, and runs the
  experiment over the given algorithm.

  The return value is 0 if the experiment correctly identified all pattern
  instances in all sequences, and the number of misses otherwise.
*/
int run(runnable code, char *name, int argc, char *argv[]) {
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

  // Run it. For each sequence, try each pattern against it. The code function
  // pointer will return the number of matches found, which will be compared to
  // the table of answers for that pattern. Report any mismatches.
  double start_time = get_time();
  int return_code = 0; // Used for noting if some number of matches fail
  for (int sequence = 0; sequence < sequences_count; sequence++) {
#ifdef DEBUG
    fprintf(stderr, "Starting sequence #%d:\n", sequence + 1);
#endif // DEBUG
    char *sequence_str = sequences_data[sequence];
    int seq_len = strlen(sequence_str);

    for (int pattern = 0; pattern < patterns_count; pattern++) {
#ifdef DEBUG
      fprintf(stderr, "  Starting pattern #%d:\n", pattern + 1);
#endif // DEBUG
      char *pattern_str = patterns_data[pattern];
      int pat_len = strlen(pattern_str);
      int matches = (*code)(pattern_str, pat_len, sequence_str, seq_len);

      if (matches != answers_data[pattern][sequence]) {
        fprintf(stderr, "Pattern %d mismatch against sequences %d (%d != %d)\n",
                pattern + 1, sequence + 1, matches,
                answers_data[pattern][sequence]);
        return_code++;
      }
    }
  }
  // Note the end time, before freeing memory.
  double end_time = get_time();
  fprintf(stdout, "---\nlanguage: %s\nalgorithm: %s\n", LANG, name);
  fprintf(stdout, "runtime: %.6g\n", end_time - start_time);

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

  return return_code;
}
