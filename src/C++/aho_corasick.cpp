/*
  Implementation of the Aho-Corasick algorithm for multi-pattern matching.

  Unlike the single-pattern algorithms, this is not taken from prior art. This
  is coded directly from the algorithm pseudo-code in the Aho-Corasick paper.
*/

#include <algorithm>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <sys/time.h>
#include <vector>

#include "setup.hpp"

#if defined(__INTEL_LLVM_COMPILER)
#define LANG "cpp-intel"
#elif defined(__llvm__)
#define LANG "cpp-llvm"
#elif defined(__GNUC__)
#define LANG "cpp-gcc"
#endif

// Rather than implement a translation table for the four characters in the DNA
// alphabet, for now just let the alphabet be the full ASCII range and only use
// those four.
#define ASIZE 128

// The "fail" value is used to determine certain states in the goto function.
#define FAIL -1

/*
  For the creation of the failure function, we *would* loop over all of the
  values [0, ASIZE] looking for those that are non-fail. That would be very
  inefficient, given that our alphabet is actually just four characters. Use
  this array to shorten those loops.
*/
#define OFFSETS_COUNT 4
static std::vector<int> ALPHA_OFFSETS = {65, 67, 71, 84};

/*
  Need a simple implementation of a set with just a few operations (add,
  contains, create, and union).
*/

// How big to create the initial set-storage.
#define SET_SIZE 8

class Set {
public:
  std::vector<int> elements;

  Set() { elements.reserve(SET_SIZE); }

  void add(const int num) { elements.push_back(num); }

  bool has(const int num) {
    bool found = false;

    for (int value : elements) {
      if (value == num) {
        found = true;
        break;
      }
    }

    return found;
  }

  void set_union(const Set &b) {
    for (int value : b.elements) {
      if (!has(value))
        add(value);
    }

    return;
  }
};

/*
  Also need a simple integer queue to use for building the failure function.
*/

// The initial queue size, and how much it grows by:
#define QUEUE_SIZE 16

class Queue {
public:
  std::vector<int> elements;
  unsigned int head;

  Queue() {
    elements.reserve(QUEUE_SIZE);
    head = 0;
  }

  bool is_empty() { return head == elements.size(); }

  void enqueue(const int value) { elements.push_back(value); }

  int dequeue() {
    if (is_empty())
      throw std::runtime_error{"dequeue: Queue underflow"};

    return elements[head++];
  }
};

/*
  Enter the given pattern into the given goto-function, creating new states as
  needed. When done, add the index of the pattern into the partial output
  function for the state of the last character.
*/
void enter_pattern(std::string pat, int idx,
                   std::vector<std::vector<int>> &goto_fn,
                   std::vector<Set> &output_fn) {
  int len = pat.length();
  int j = 0, state = 0;
  static int new_state = 0;

  // Find the first leaf corresponding to a character in `pat`. From there is
  // where a new state (if needed) will be added. Note that the original
  // algorithm did not account for pattern `pat` being a substring of an
  // existing pattern in the goto function. The break-test is added to avoid
  // the counter `j` going past the end of `pat`.
  while (goto_fn[state][pat[j]] != FAIL) {
    state = goto_fn[state][pat[j]];
    j++;
    if (j == len)
      break;
  }

  // At this point, `state` points to the leaf in the automaton. Create new
  // states from here on for the remaining characters in `pat` that weren't
  // already in the automaton.
  for (int p = j; p < len; p++) {
    new_state++;
    goto_fn[state][pat[p]] = new_state;
    state = new_state;
  }

  output_fn[state].add(idx);

  return;
}

/*
  Build the goto function and the (partial) output function.
*/
void build_goto(std::vector<std::string> pats, int num_pats,
                std::vector<std::vector<int>> &goto_fn,
                std::vector<Set> &output_fn) {
  std::vector<std::vector<int>> new_goto;
  std::vector<Set> new_output;
  int max_states = 0;

  // Calculate the maximum number of states as being the sum of the lengths of
  // patterns. This is overkill, but a more "serious" implementation would
  // have a more "serious" graph implementation for the goto function.
  for (int i = 0; i < num_pats; i++)
    max_states += pats[i].length();

  // Allocate for the goto function
  new_goto.resize(max_states, std::vector<int>(ASIZE));
  for (int i = 0; i < max_states; i++)
    std::fill_n(new_goto[i].begin(), ASIZE, FAIL);

  // Allocate for the output function
  new_output.resize(max_states, Set());

  // OK, now actually build the goto function and output function.

  // Add each pattern in turn:
  for (int i = 0; i < num_pats; i++)
    enter_pattern(pats[i], i, new_goto, new_output);

  // Set the unused transitions in state 0 to point back to state 0:
  for (int i = 0; i < ASIZE; i++)
    if (new_goto[0][i] == FAIL)
      new_goto[0][i] = 0;

  goto_fn = new_goto;
  output_fn = new_output;
  return;
}

/*
  Build the failure function and complete the output function.
*/
std::vector<int> build_failure(std::vector<std::vector<int>> goto_fn,
                               std::vector<Set> output_fn) {
  // Need a simple queue of state numbers.
  Queue queue = Queue();

  // Allocate the failure function storage. This also needs to be as long as
  // goto_fn is, for safety.
  std::vector<int> failure_fn;
  failure_fn.resize(goto_fn.size(), 0);

  // The queue starts out empty. Set it to be all states reachable from state 0
  // and set failure(state) for those states to be 0.
  for (int i = 0; i < OFFSETS_COUNT; i++) {
    int state = goto_fn[0][ALPHA_OFFSETS[i]];
    if (state == 0)
      continue;

    queue.enqueue(state);
    failure_fn[state] = 0;
  }

  // This uses some single-letter variable names that match the published
  // algorithm. Their mnemonic isn't clear, or else I'd use more meaningful
  // names.
  while (!queue.is_empty()) {
    int r = queue.dequeue();
    for (int i = 0; i < OFFSETS_COUNT; i++) {
      int a = ALPHA_OFFSETS[i];
      int s = goto_fn[r][a];
      if (s == FAIL)
        continue;

      queue.enqueue(s);
      int state = failure_fn[r];
      while (goto_fn[state][a] == FAIL)
        state = failure_fn[state];
      failure_fn[s] = goto_fn[state][a];
      output_fn[s].set_union(output_fn[failure_fn[s]]);
    }
  }

  return failure_fn;
}

/*
  Perform the Aho-Corasick algorithm against the given sequence. No pattern is
  passed in, as the machine of goto_fn/failure_fn/output_fn will handle all the
  patterns in a single pass.

  Instead of returning a single int, returns an array of ints as long as the
  number of patterns (pattern_count).
*/
std::vector<int> aho_corasick(const std::string &sequence, int n,
                              int pattern_count,
                              std::vector<std::vector<int>> &goto_fn,
                              std::vector<int> &failure_fn,
                              std::vector<Set> &output_fn) {
  int state = 0;
  std::vector<int> matches;
  matches.resize(pattern_count, 0);

  for (int i = 0; i < n; i++) {
    while (goto_fn[state][sequence[i]] == FAIL)
      state = failure_fn[state];

    state = goto_fn[state][sequence[i]];
    for (int idx : output_fn[state].elements)
      matches[idx]++;
  }

  return matches;
}

/*
  Simple measure of the wall-clock down to the usec. Adapted from StackOverflow.
*/
double get_time() {
  struct timeval t;
  gettimeofday(&t, NULL);
  return t.tv_sec + t.tv_usec * 1e-6;
}

/*
  This is a customization of the runner function used for the single-pattern
  matching algorithms. This one sets up the structures needed for the A-C
  algorithm, then iterates over the sequences (since iterating over the patterns
  is not necessary).

  The return value is 0 if the experiment correctly identified all pattern
  instances in all sequences, and the number of misses otherwise.
*/
int run(int argc, char *argv[]) {
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

  // Run it. First, prepare the data structures for the combined pattern that
  // will be used for matching. Then, for each sequence, try the combined
  // pattern against it. The aho_corasick() function will return an array of
  // integers for the count of matches of each pattern within the given
  // sequence. Report any mismatches (if we have answers data available).
  double start_time = get_time();
  int return_code = 0; // Used for noting if some number of matches fail

  // Initialize the multi-pattern structure.
  std::vector<std::vector<int>> goto_fn;
  std::vector<Set> output_fn;
  build_goto(patterns_data, patterns_count, goto_fn, output_fn);
  std::vector<int> failure_fn = build_failure(goto_fn, output_fn);

  for (int sequence = 0; sequence < sequences_count; sequence++) {
    const std::string sequence_str = sequences_data[sequence];
    int seq_len = sequence_str.length();

    // Here, we don't iterate over the patterns. We just call the matching
    // function and pass it the three "machine" elements set up in the
    // initialization code, above.
    std::vector<int> matches = aho_corasick(
        sequence_str, seq_len, patterns_count, goto_fn, failure_fn, output_fn);

    if (answers_data.size()) {
      for (int pattern = 0; pattern < patterns_count; pattern++)
        if (matches[pattern] != answers_data[pattern][sequence]) {
          std::cerr << "Pattern " << pattern + 1
                    << " mismatch against sequence " << sequence + 1 << " ("
                    << matches[pattern]
                    << " != " << answers_data[pattern][sequence] << ")\n";
          return_code++;
        }
    }
  }

  // Note the end time, before freeing memory.
  double end_time = get_time();

  std::cout << "language: " << LANG << "\n"
            << "algorithm: aho_corasick\n"
            << "runtime: " << std::setprecision(8) << end_time - start_time
            << "\n";

  return return_code;
}

/*
  All that is done here is call the run() function with the argc/argv values.
*/
int main(int argc, char *argv[]) {
  int return_code = run(argc, argv);

  return return_code;
}
