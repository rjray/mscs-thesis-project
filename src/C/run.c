/*
  This is the "runner" module. It provides the functions that will handle
  running the experiments. There are three primary runner functions here:

    * run() - Runs a single-pattern, exact-matching algorithm
    * run_multi() - Runs a multi-pattern, exact-matching algorithm
    * run_approx() - Runs a single-pattern, approximate-matching algorithm

  These are mostly identical, but just different-enough to require separate
  functions. The data-input handling is brought in from `input.c`.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>

#include "input.h"
#include "run.h"

// Identify the language by the compiler.
#if defined(__INTEL_LLVM_COMPILER)
#define LANG "c-intel"
#elif defined(__llvm__)
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
  The basic "runner" function. This takes pointers to the algorithm initializer
  and implementation, the name of the algorithm, argc and argv from the
  invocation, and runs the experiment over the given algorithm.

  The return value is 0 if the experiment correctly identified all pattern
  instances in all sequences, and the number of misses otherwise.
*/
int run(initializer init, algorithm code, char *name, int argc, char *argv[]) {
  if (argc < 3 || argc > 4) {
    fprintf(stderr, "Usage: %s <sequences> <patterns> [ <answers> ]\n",
            argv[0]);
    exit(-1);
  }

  // These will be alloc'd by the routines that read the files.
  char **sequences_data, **patterns_data;
  int **answers_data = NULL;

  // Read the three data files. Any of these that return 0 means an error. Any
  // error has already been reported to stderr. The filenames are in the order:
  // sequences patterns answers.
  int sequences_count = read_sequences(argv[1], &sequences_data);
  if (sequences_count == 0)
    exit(-1);
  int patterns_count = read_patterns(argv[2], &patterns_data);
  if (patterns_count == 0)
    exit(-1);
  if (argc == 4) {
    int answers_count = read_answers(argv[3], &answers_data, NULL);
    if (answers_count == 0)
      exit(-1);
    if (answers_count != patterns_count) {
      fprintf(stderr,
              "Count mismatch between patterns file and answers file\n");
      exit(-1);
    }
  }

  // Run it. For each sequence, try each pattern against it. The code function
  // pointer will return the number of matches found, which will be compared to
  // the table of answers for that pattern. Report any mismatches.
  double start_time = get_time();
  int return_code = 0; // Used for noting if some number of matches fail

  for (int pattern = 0; pattern < patterns_count; pattern++) {
    char *pattern_str = patterns_data[pattern];
    void **pat_data = (*init)((unsigned char *)pattern_str);

    for (int sequence = 0; sequence < sequences_count; sequence++) {
      char *sequence_str = sequences_data[sequence];

      int matches = (*code)(pat_data, (unsigned char *)sequence_str);

      if (answers_data && matches != answers_data[pattern][sequence]) {
        fprintf(stderr, "Pattern %d mismatch against sequence %d (%d != %d)\n",
                pattern + 1, sequence + 1, matches,
                answers_data[pattern][sequence]);
        return_code++;
      }
    }

    for (int i = 0; pat_data[i] != (void *)NULL; i++)
      free(pat_data[i]);
    free(pat_data);
  }

  // Note the end time, before freeing memory.
  double end_time = get_time();
  fprintf(stdout, "language: %s\nalgorithm: %s\n", LANG, name);
  fprintf(stdout, "runtime: %.8g\n", end_time - start_time);

  // Free all the memory that was allocated by the routines in input.c:
  for (int i = 0; i < patterns_count; i++)
    free(patterns_data[i]);
  free(patterns_data);

  if (answers_data) {
    for (int i = 0; i < patterns_count; i++)
      free(answers_data[i]);
    free(answers_data);
  }

  for (int i = 0; i < sequences_count; i++)
    free(sequences_data[i]);
  free(sequences_data);

  return return_code;
}

/*
  This is a variation of `run` that handles algorithms that do multi-pattern
  matching. It has the same signature as `run`, above.
*/
int run_multi(mp_initializer init, mp_algorithm code, char *name, int argc,
              char *argv[]) {
  if (argc < 3 || argc > 4) {
    fprintf(stderr, "Usage: %s <sequences> <patterns> [ <answers> ]\n",
            argv[0]);
    exit(-1);
  }

  // These will be alloc'd by the routines that read the files.
  char **sequences_data, **patterns_data;
  int **answers_data = NULL;

  // Read the three data files. Any of these that return 0 means an error. Any
  // error has already been reported to stderr. The filenames are in the order:
  // sequences patterns answers.
  int sequences_count = read_sequences(argv[1], &sequences_data);
  if (sequences_count == 0)
    exit(-1);
  int patterns_count = read_patterns(argv[2], &patterns_data);
  if (patterns_count == 0)
    exit(-1);
  if (argc == 4) {
    int answers_count = read_answers(argv[3], &answers_data, NULL);
    if (answers_count == 0)
      exit(-1);
    if (answers_count != patterns_count) {
      fprintf(stderr,
              "Count mismatch between patterns file and answers file\n");
      exit(-1);
    }
  }

  // Run it. For each sequence, try the combined group of patterns against it.
  // The code function pointer will return the number of matches found, which
  // will be compared to the table of answers for that pattern. Report any
  // mismatches.
  double start_time = get_time();
  int return_code = 0; // Used for noting if some number of matches fail

  void **pat_data = (*init)((unsigned char **)patterns_data, patterns_count);

  for (int sequence = 0; sequence < sequences_count; sequence++) {
    char *sequence_str = sequences_data[sequence];

    int *matches = (*code)(pat_data, (unsigned char *)sequence_str);

    if (answers_data) {
      for (int pattern = 0; pattern < patterns_count; pattern++)
        if (matches[pattern] != answers_data[pattern][sequence]) {
          fprintf(stderr,
                  "Pattern %d mismatch against sequence %d (%d != %d)\n",
                  pattern + 1, sequence + 1, matches[pattern],
                  answers_data[pattern][sequence]);
          return_code++;
        }
    }

    free(matches);
  }

  for (int i = 0; pat_data[i] != (void *)NULL; i++)
    free(pat_data[i]);
  free(pat_data);

  // Note the end time, before freeing memory.
  double end_time = get_time();
  fprintf(stdout, "language: %s\nalgorithm: %s\n", LANG, name);
  fprintf(stdout, "runtime: %.8g\n", end_time - start_time);

  // Free all the memory that was allocated by the routines in input.c:
  for (int i = 0; i < patterns_count; i++)
    free(patterns_data[i]);
  free(patterns_data);

  if (answers_data) {
    for (int i = 0; i < patterns_count; i++)
      free(answers_data[i]);
    free(answers_data);
  }

  for (int i = 0; i < sequences_count; i++)
    free(sequences_data[i]);
  free(sequences_data);

  return return_code;
}

/*
  This is a variation of `run` that handles algorithms that do approximate
  matching. It has the same signature as `run`, above. Here, we have to contend
  with an additional command-line parameter that specifies the value of k for
  the approximate-matching process.
*/
int run_approx(am_initializer init, am_algorithm code, char *name, int argc,
               char *argv[]) {
  if (argc < 4 || argc > 5) {
    fprintf(stderr, "Usage: %s <k> <sequences> <patterns> [ <answers> ]\n",
            argv[0]);
    exit(-1);
  }

  // These will be alloc'd by the routines that read the files.
  char **sequences_data, **patterns_data;
  int **answers_data = NULL;
  int k;

  // Read the value of k from the command line.
  k = (int)strtol(argv[1], NULL, 10);
  // Read the three data files. Any of these that return 0 means an error. Any
  // error has already been reported to stderr. The filenames are in the order:
  // sequences patterns answers.
  int sequences_count = read_sequences(argv[2], &sequences_data);
  if (sequences_count == 0)
    exit(-1);
  int patterns_count = read_patterns(argv[3], &patterns_data);
  if (patterns_count == 0)
    exit(-1);
  if (argc == 5) {
    int k_read;
    char answers_file[256];
    sprintf(answers_file, argv[4], k);
    int answers_count = read_answers(answers_file, &answers_data, &k_read);
    if (answers_count == 0)
      exit(-1);
    if (answers_count != patterns_count) {
      fprintf(stderr,
              "Count mismatch between patterns file and answers file\n");
      exit(-1);
    }
    if (k != k_read) {
      fprintf(stderr, "Mismatch in k value in answers file (%d vs. %d)\n", k,
              k_read);
      exit(-1);
    }
  }

  // Run it. For each sequence, try each pattern against it. The code function
  // pointer will return the number of matches found, which will be compared to
  // the table of answers for that pattern. Report any mismatches.
  double start_time = get_time();
  int return_code = 0; // Used for noting if some number of matches fail

  for (int pattern = 0; pattern < patterns_count; pattern++) {
    char *pattern_str = patterns_data[pattern];
    void **pat_data = (*init)((unsigned char *)pattern_str, k);

    for (int sequence = 0; sequence < sequences_count; sequence++) {
      char *sequence_str = sequences_data[sequence];

      int matches = (*code)(pat_data, (unsigned char *)sequence_str);

      if (answers_data && matches != answers_data[pattern][sequence]) {
        fprintf(stderr, "Pattern %d mismatch against sequence %d (%d != %d)\n",
                pattern + 1, sequence + 1, matches,
                answers_data[pattern][sequence]);
        return_code++;
      }
    }

    for (int i = 0; pat_data[i] != (void *)NULL; i++)
      free(pat_data[i]);
    free(pat_data);
  }

  // Note the end time, before freeing memory.
  double end_time = get_time();
  fprintf(stdout, "language: %s\nalgorithm: %s(%d)\n", LANG, name, k);
  fprintf(stdout, "runtime: %.8g\n", end_time - start_time);

  // Free all the memory that was allocated by the routines in input.c:
  for (int i = 0; i < patterns_count; i++)
    free(patterns_data[i]);
  free(patterns_data);

  if (answers_data) {
    for (int i = 0; i < patterns_count; i++)
      free(answers_data[i]);
    free(answers_data);
  }

  for (int i = 0; i < sequences_count; i++)
    free(sequences_data[i]);
  free(sequences_data);

  return return_code;
}
