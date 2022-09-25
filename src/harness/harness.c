/*
  Main code for the harness, adapted from:
  https://github.com/greensoftwarelab/Energy-Languages
 */

#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "rapl.h"

const int CORE = 0;

int main(int argc, char **argv) {
  int opt, run_count = 10;
  int show_info = 0;
  char *output_file = (char *)calloc(256, sizeof(char));
  char **exec_argv = (char **)calloc(4, sizeof(char *));
  char *program = (char *)calloc(256, sizeof(char));
  FILE *file;

  while ((opt = getopt(argc, argv, "in:f:")) != -1) {
    switch (opt) {
    case 'i':
      show_info = 1;
      break;
    case 'n':
      run_count = atoi(optarg);
      break;
    case 'f':
      strcpy(output_file, optarg);
      break;
    default:
      fprintf(stderr, "Usage: %s [ -i ] [ -n count ] [ -f output ] <files>\n",
              argv[0]);
      exit(EXIT_FAILURE);
    }
  }
  // Default output_file if it wasn't given:
  if (output_file[0] == '\0')
    strcpy(output_file, "experiments_data.yml");

  // Make sure there are enough arguments still in argv:
  int remaining = argc - optind;
  if (!show_info && (remaining < 3 || remaining > 4)) {
    fprintf(stderr, "Wrong number of arguments (%d) given to %s\n", remaining,
            argv[0]);
    exit(EXIT_FAILURE);
  }

  // Don't do these if show_info was passed, as there probably aren't any args.
  if (!show_info) {
    // Copy the program argument
    strcpy(program, argv[optind]);
    // Copy the input file arguments' pointers to exec_argv:
    exec_argv[0] = argv[optind + 1]; // sequences
    exec_argv[1] = argv[optind + 2]; // patterns
    if (remaining == 4)
      exec_argv[2] = argv[optind + 3];
  }

  rapl_init(CORE, show_info);

  // If the user passed -i, just show some CPU/core info and exit.
  if (show_info) {
    show_power_info(CORE);
    show_power_limit(CORE);
    exit(EXIT_SUCCESS);
  }

  file = fopen(output_file, "a");

  for (int i = 0; i < run_count; i++) {
    rapl_before(CORE);

    // system(command);

    rapl_after(file, CORE);
  }

  fclose(file);

  free(output_file);
  free(program);
  free(exec_argv);

  return 0;
}
