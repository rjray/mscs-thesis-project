/*
  "Setup" code used by all the C programs to read the various data files and
  return viable data structures.
*/

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Prototypes:
int read_sequences(char *, char **);
int read_patterns(char *, char **);
int read_answers(char *, int **);

/*
  Read two numbers from a line of the file pointed to by `input`. Store them in
  the pointers `first` and `second`.
*/
void read_two_ints(FILE *input, int *first, int *second) {
  char line[80] = {0};
  char *s;

  fgets(line, 80, input);
  s = strtok(line, " ");
  *first = (int)strtol(s, NULL, 10);
  s = strtok(NULL, " ");
  *second = (int)strtol(s, NULL, 10);

  return;
}

/*
  Read the sequence data from the given filename. Stuff it into `data`. The
  `count` parameter will indicate the number of sequences read.

  The first line indicates the number of data-lines and their maximum length:

    100000 1040

  The max-length does not include the newline character.
*/
int read_sequences(char *fname, char **data) {
  FILE *input = fopen(fname, "r");
  if (input == NULL) {
    int err = errno;
    fprintf(stderr, "Error opening %s for reading: %s\n", fname, strerror(err));
    return 1;
  }

  int num_lines, max_length;
  read_two_ints(input, &num_lines, &max_length);

  // Allocate the list of pointers in `data`:
  *data = calloc(num_lines, sizeof(char *));

  int count = 0;
  char *line = calloc(max_length + 1, sizeof(char));
  while (fgets(line, max_length + 1, input) != NULL) {

    count++;
  }

  fclose(input);
  free(line);
  return 0;
}
