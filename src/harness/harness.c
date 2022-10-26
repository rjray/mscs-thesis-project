/*
  Main code for the harness, adapted from:
  https://github.com/greensoftwarelab/Energy-Languages
 */

#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <unistd.h>

#include "rapl.h"
/*
  This header file comes from the following GitHub repository:
  https://github.com/sheredom/subprocess.h

  See the file itself for its license information, which differs from the
  license the rest of this repository is under.
 */
#include "subprocess.h"

const int CORE = 0;

/*
  Simple measure of the wall-clock down to the usec. Adapted from StackOverflow.
*/
double get_time() {
  struct timeval t;
  gettimeofday(&t, NULL);
  return t.tv_sec + t.tv_usec * 1e-6;
}

int main(int argc, char **argv) {
  int opt, run_count = 10, show_info = 0, verbose = 0, skip0 = 0;
  char *output_file = (char *)calloc(256, sizeof(char));
  char **exec_argv = (char **)calloc(12, sizeof(char *));
  FILE *file;

  while ((opt = getopt(argc, argv, "vin:f:s")) != -1) {
    switch (opt) {
    case 'i':
      show_info = 1;
      break;
    case 'v':
      verbose = 1;
      break;
    case 'n':
      run_count = atoi(optarg);
      break;
    case 'f':
      strcpy(output_file, optarg);
      break;
    case 's':
      skip0 = 1;
      break;
    default:
      fprintf(
          stderr,
          "Usage: %s [ -v ] [ -i ] [ -s ] [ -n count ] [ -f output ] <files>\n",
          argv[0]);
      exit(EXIT_FAILURE);
    }
  }
  // Default output_file if it wasn't given:
  if (output_file[0] == '\0')
    strcpy(output_file, "experiments_data.yml");

  // Make sure there are enough arguments still in argv:
  int remaining = argc - optind;
  if (!show_info && remaining < 3) {
    fprintf(stderr, "Wrong number of arguments (%d) given to %s\n", remaining,
            argv[0]);
    exit(EXIT_FAILURE);
  }

  // Don't do these if show_info was passed, as there probably aren't any args.
  if (!show_info) {
    int idx = 0;
    // Start with the elements that will run it under /bin/time for mem usage:
    exec_argv[idx++] = "/bin/time";
    exec_argv[idx++] = "-f";
    exec_argv[idx++] = "max_memory: %M";
    // Copy the program elements' pointers to exec_argv:
    for (int i = 0; i < remaining; i++) {
      exec_argv[idx++] = argv[optind + i];
    }
  }

  rapl_init(CORE, show_info);

  // If the user passed -i, just show some CPU/core info and exit.
  if (show_info) {
    show_power_info(CORE);
    show_power_limit(CORE);
    exit(EXIT_SUCCESS);
  }

  file = fopen(output_file, "a");
  if (verbose)
    fprintf(stdout, "Starting run of %d iterations of %s\n",
            run_count + 1 - skip0, argv[optind]);

  for (int i = skip0; i <= run_count; i++) {
    int result, ret;
    struct subprocess_s process;
    char *line = (char *)calloc(80, sizeof(char));

    if (verbose)
      fprintf(stdout, "  Iteration %d/%d\n", i, run_count);

    rapl_before(CORE);
    double start_time = get_time();

    result = subprocess_create((const char *const *)exec_argv, 0, &process);
    if (0 != result) {
      fprintf(stderr, "harness: Error creating subprocess: %d\n", result);
      exit(EXIT_FAILURE);
    }
    result = subprocess_join(&process, &ret);
    if (0 != result) {
      fprintf(stderr, "harness: Error joining subprocess: %d\n", result);
      exit(EXIT_FAILURE);
    }

    if (i != 0) {
      // Note the end time.
      double end_time = get_time();
      fprintf(file, "---\n");
      fprintf(file, "iteration: %d\n", i);
      fprintf(file, "success: %s\n", ret == 0 ? "true" : "false");
      fprintf(file, "total_runtime: %.8g\n", end_time - start_time);

      // Capture the stdout of the process.
      FILE *stdout_file = subprocess_stdout(&process);
      while (fgets(line, 80, stdout_file) != NULL)
        fputs(line, file);

      // Capture the stderr and add it.
      FILE *stderr_file = subprocess_stderr(&process);
      while (fgets(line, 80, stderr_file) != NULL) {
        if (strstr(line, "max_memory: "))
          fputs(line, file);
      }

      // Capture the energy readings.
      rapl_after(file, CORE);
    }

    subprocess_destroy(&process);
    fflush(file);
  }

  fclose(file);

  free(output_file);
  free(exec_argv);

  return 0;
}
