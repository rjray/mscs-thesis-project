/*
  This is the "runner" module. It provides the functions that will handle
  running the experiments. There are three primary runner functions here:

    * run() - Runs a single-pattern, exact-matching algorithm
    * run_multi() - Runs a multi-pattern, exact-matching algorithm
    * run_approx() - Runs a single-pattern, approximate-matching algorithm

  These are mostly identical, but just different-enough to require separate
  functions. The data-input handling is brought in from `input.cpp`.
*/

#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <sys/time.h>
#include <vector>

#include "input.hpp"
#include "run.hpp"

// Identify the language by the compiler.
#if defined(__INTEL_LLVM_COMPILER)
#define LANG "cpp-intel"
#elif defined(__llvm__)
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
  The basic "runner" function. This takes pointers to the algorithm initializer
  and implementation, the name of the algorithm, argc and argv from the
  invocation, and runs the experiment over the given algorithm.

  The return value is 0 if the experiment correctly identified all pattern
  instances in all sequences, and the number of misses otherwise. An exception
  is thrown on any non-recoverable errors.
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
    answers_data = read_answers(argv[3], nullptr);
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
    // Pre-process the pattern before applying it to all sequences.
    std::vector<PatternData> pat_data = (*init)(pattern_str);

    for (int sequence = 0; sequence < sequences_count; sequence++) {
      std::string sequence_str = sequences_data[sequence];

      int matches = (*code)(pat_data, sequence_str);

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

/*
  This is a variation of "run" that handles algorithms that do multi-pattern
  matching.
*/
int run_multi(mp_initializer init, mp_algorithm code, std::string name,
              int argc, char *argv[]) {
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
    answers_data = read_answers(argv[3], nullptr);
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

  // Pre-process the patterns before applying to all sequences.
  std::vector<MultiPatternData> pat_data = (*init)(patterns_data);

  for (int sequence = 0; sequence < sequences_count; sequence++) {
    std::string sequence_str = sequences_data[sequence];

    std::vector<int> matches = (*code)(pat_data, sequence_str);

    if (answers_data.size()) {
      for (int pattern = 0; pattern < patterns_count; pattern++) {
        if (matches[pattern] != answers_data[pattern][sequence]) {
          std::cerr << "Pattern " << pattern + 1
                    << " mismatch against sequence " << sequence + 1 << " ("
                    << matches[pattern]
                    << " != " << answers_data[pattern][sequence] << ")\n";
          return_code++;
        }
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

/*
  This is a variation of `run` that handles algorithms that do approximate
  matching. It has the same signature as `run`, above. Here, we have to contend
  with an additional command-line parameter that specifies the value of k for
  the approximate-matching process.
*/
int run_approx(am_initializer init, am_algorithm code, std::string name,
               int argc, char *argv[]) {
  if (argc < 4 || argc > 5) {
    std::ostringstream error;
    error << "Usage: " << argv[0]
          << " <k> <sequences> <patterns> [ <answers> ]";
    throw std::runtime_error{error.str()};
  }

  // Read the initial integer and three data files. Any of these that encounter
  // an error will throw an exception. The filenames are in the order: sequences
  // patterns answers.
  int k = std::stoi(argv[1]);
  std::vector<std::string> sequences_data = read_sequences(argv[2]);
  int sequences_count = sequences_data.size();
  std::vector<std::string> patterns_data = read_patterns(argv[3]);
  int patterns_count = patterns_data.size();
  std::vector<std::vector<int>> answers_data;
  if (argc == 5) {
    int k_read;
    char answers_file[256];
    sprintf(answers_file, argv[4], k);
    answers_data = read_answers(answers_file, &k_read);
    int answers_count = answers_data.size();
    if (answers_count != patterns_count)
      throw std::runtime_error{
          "Count mismatch between patterns file and answers file"};
    if (k != k_read)
      throw std::runtime_error{"Mismatch in k value in answers file"};
  }

  // Run it. For each sequence, try each pattern against it. The code
  // function pointer will return the number of matches found, which will be
  // compared to the table of answers for that pattern. Report any
  // mismatches.
  double start_time = get_time();
  int return_code = 0; // Used for noting if some number of matches fail
  for (int pattern = 0; pattern < patterns_count; pattern++) {
    std::string pattern_str = patterns_data[pattern];
    // Pre-process the pattern before applying it to all sequences.
    std::vector<ApproxPatternData> pat_data = (*init)(pattern_str, k);

    for (int sequence = 0; sequence < sequences_count; sequence++) {
      std::string sequence_str = sequences_data[sequence];

      int matches = (*code)(pat_data, sequence_str);

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
            << "algorithm: " << name << "(" << k << ")\n"
            << "runtime: " << std::setprecision(8) << end_time - start_time
            << "\n";

  return return_code;
}
