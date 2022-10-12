/*
  This is the "runner" module. It provides the function that will handle running
  an experiment.
*/

#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <sys/time.h>
#include <vector>

#include "run.hpp"
#include "setup.hpp"

#if defined(__llvm__)
#define LANG "cpp-llvm"
#elif defined(__GNUC__)
#define LANG "cpp-gcc"
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
  instances in all sequences, and the number of misses otherwise. An exception
  is thrown on non-recoverable errors.
*/
int run(initializer init, algorithm code, std::string name, int argc,
        char *argv[]) {
  if (argc < 3 || argc > 4) {
    std::ostringstream error;
    error << "Usage: " << argv[0] << " <sequences> <patterns> [ <answers> ]";
    throw std::runtime_error{error.str()};
  }

  // Read the three data files. Any of these that encounter an error will
  // throw an exception. The filenames are in the order: sequences patterns
  // answers.
  std::vector<std::string> sequences_data = read_sequences(argv[1]);
  int sequences_count = sequences_data.size();
  std::vector<std::string> patterns_data = read_patterns(argv[2]);
  int patterns_count = patterns_data.size();
  std::vector<std::vector<int>> answers_data;
  if (argc == 4) {
    answers_data = read_answers(argv[3]);
    int answers_count = answers_data.size();
    if (answers_count != patterns_count)
      throw std::runtime_error{
          "Count mismatch between patterns file and answers file"};
  }

  // Run it. For each sequence, try each pattern against it. The code function
  // pointer will return the number of matches found, which will be compared to
  // the table of answers for that pattern. Report any mismatches.
  double start_time = get_time();
  int return_code = 0; // Used for noting if some number of matches fail
  for (int pattern = 0; pattern < patterns_count; pattern++) {
    std::string pattern_str = patterns_data[pattern];
    int pat_len = pattern_str.length();
    std::vector<PatternData> pat_data = (*init)(pattern_str, pat_len);

    for (int sequence = 0; sequence < sequences_count; sequence++) {
      std::string sequence_str = sequences_data[sequence];
      int seq_len = sequence_str.length();

      int matches = (*code)(pat_data, pat_len, sequence_str, seq_len);

      if (answers_data.size() && matches != answers_data[pattern][sequence]) {
        std::cerr << "Pattern " << pattern + 1 << " mismatch against sequence "
                  << sequence + 1 << " (" << matches
                  << " != " << answers_data[pattern][sequence] << ")\n";
        return_code++;
      }
    }
  }
  // Note the end time.
  double end_time = get_time();

  std::cout << "language: " << LANG << "\n"
            << "algorithm: " << name << "\n"
            << "runtime: " << std::setprecision(8) << end_time - start_time
            << "\n";

  return return_code;
}
