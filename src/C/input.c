/*
  Input code used by all the C programs to read the various data files and
  return viable data structures.
*/

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "input.h"

/*
  Read the numbers from the first line of the file pointed to by `input`. Store
  them in the provided int[] pointer.
*/
void read_header(FILE *input, int numbers[]) {
  char line[80] = {0};
  char *s;

  // The first line of a file is only ever the 2-3 integers we're expecting, so
  // it's safe to assume that 80 characters is enough.
  if (fgets(line, 80, input) == NULL) {
    fprintf(stderr, "Error reading file's header line, stopped\n");
    exit(-1);
  }

  // Use strtok() with " " as the separator.
  s = strtok(line, " ");
  int idx = 0;
  while (s != NULL) {
    numbers[idx++] = (int)strtol(s, NULL, 10);
    s = strtok(NULL, " ");
  }

  return;
}

/*
  Read the sequence data from the given filename. Stuff it into `data`. The
  return value will indicate the number of sequences read.

  The first line indicates the number of data-lines and their maximum length:

    100000 1040

  The max-length does not include the newline character.
*/
int read_sequences(const char *fname, char ***data) {
  FILE *input = fopen(fname, "r");
  if (input == NULL) {
    int err = errno;
    fprintf(stderr, "Error opening %s for reading: %s\n", fname, strerror(err));
    return 0;
  }

  int numbers[2] = {0};
  read_header(input, numbers);
  int num_lines = numbers[0], max_length = numbers[1];

  // Allocate the list of pointers in `table`:
  char **table = (char **)calloc(num_lines, sizeof(char *));
  if (table == NULL) {
    fprintf(stderr, "Error allocating data pointer table\n");
    return 0;
  }
  // Add two to `max_length` to allow for the \n and the \0.
  int line_length = max_length + 2;

  int count = 0;
  char *line = (char *)calloc(line_length, sizeof(char));
  if (line == NULL) {
    fprintf(stderr, "Error allocating line for file-reading\n");
    return 0;
  }

  while (fgets(line, line_length, input) != NULL) {
    // Strip the trailing newline if it exists:
    if (line[strlen(line) - 1] == '\n')
      line[strlen(line) - 1] = '\0';

    // Allocate memory and copy the line to it:
    char *ptr = (char *)calloc(strlen(line) + 1, sizeof(char));
    if (ptr == NULL) {
      fprintf(stderr, "Error allocating pointer for storing data\n");
      return 0;
    }
    strcpy(ptr, line);
    table[count] = ptr;

    count++;
  }

  fclose(input);
  free(line);

  // Simple check to make sure we read as many lines as expected:
  if (count != num_lines) {
    fprintf(stderr, "Incorrect number of lines read from %s: %d/%d\n", fname,
            count, num_lines);
    return 0;
  }

  *data = table;
  return count;
}

/*
  Read the pattern data from the given filename. For now, the pattern data is
  the same format as the sequence data so just fall through to read_sequences.
*/
int read_patterns(const char *fname, char ***data) {
  return read_sequences(fname, data);
}

/*
  Read the answers data from the given filename. This data is different from
  the DNA-based data. The first line tells how many data-lines there are (one
  for each pattern read) and how many comma-separated numbers there are on
  each data-line (one for each sequence read). As with the others, the return
  value indicates the number of data-lines read and parsed.
*/
int read_answers(const char *fname, int ***data, int *k) {
  FILE *input = fopen(fname, "r");
  if (input == NULL) {
    int err = errno;
    fprintf(stderr, "Error opening %s for reading: %s\n", fname, strerror(err));
    return 0;
  }

  int numbers[3] = {0};
  read_header(input, numbers);
  int num_lines = numbers[0], num_ints = numbers[1];

  // If the k pointer is not null, there is an expected third value that will
  // be the value of k for approximate matching.
  if (k != NULL)
    *k = numbers[2];

  // Allocate the list of pointers in `table`:
  int **table = (int **)calloc(num_lines, sizeof(int *));
  if (table == NULL) {
    fprintf(stderr, "Error allocating answer pointer table\n");
    return 0;
  }
  // For line_length, we can no longer assume that all the numbers are single
  // digits. For up to k=5, a multiplication factor of 3 and extra padding of
  // 1500 seems to be safe.
  int line_length = num_ints * 3 + 1500;

  int count = 0;
  char *line = (char *)calloc(line_length, sizeof(char));
  while (fgets(line, line_length, input) != NULL) {
    // Strip the trailing newline if it exists. Confuses strtok().
    if (line[strlen(line) - 1] == '\n')
      line[strlen(line) - 1] = '\0';

    // Allocate memory for the integers in the line:
    int *answers = (int *)calloc(num_ints, sizeof(int));
    if (answers == NULL) {
      fprintf(stderr, "Error allocating answer table row\n");
      return 0;
    }

    // Placeholder for strtok():
    char *token;
    // Index within answers:
    int idx = 0;

    // Parse the line.
    token = strtok(line, ",");
    while (token != NULL) {
      if (idx == num_ints) {
        fprintf(stderr, "Answers line %d: too many numbers in data line\n",
                count + 1);
        return 0;
      }

      answers[idx++] = (int)strtol(token, NULL, 10);
      token = strtok(NULL, ",");
    }
    // Verify that there are enough numbers in this line:
    if (idx != num_ints) {
      fprintf(stderr, "Answers line %d: too few numbers in data line\n",
              count + 1);
    }

    table[count++] = answers;
  }

  fclose(input);
  free(line);

  // Simple check to make sure we read as many lines as expected:
  if (count != num_lines) {
    fprintf(stderr, "Incorrect number of lines read from %s: %d/%d\n", fname,
            count, num_lines);
    return 0;
  }

  *data = table;
  return count;
}
