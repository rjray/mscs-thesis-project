/*
  C++ implementation of the (tentatively-title) DFA-Gap algorithm for
  approximate string matching.
*/

#include <array>
#include <string>
#include <vector>

#include "run.hpp"

// Rather than implement a translation table for the four characters in the DNA
// alphabet, for now just let the alphabet be the full ASCII range and only use
// those four.
constexpr int ASIZE = 128;

// The "fail" value is used to determine when to start over.
constexpr int FAIL = -1;

/*
  The ALPHABET/ALPHABET_COUNT values are used when setting up the transitions
  around the "gap" states in the DFA. Since we're being lazy about translating
  ACGT to 0-3 and using an alphabet of 128 instead, this will save some time in
  loops during the creation of the DFA.
*/
constexpr int ALPHABET_COUNT = 4;
static const std::array<int, ALPHABET_COUNT> ALPHABET = {65, 67, 71, 84};

void create_dfa(std::string const &pattern, int m, int k,
                std::vector<std::vector<int>> &dfa, int &terminal) {
  // We know that the number of states will be 1 + m + k(m - 1).
  int max_states = 1 + m + k * (m - 1);

  // Allocate for the DFA
  dfa.resize(max_states, std::vector<int>(ASIZE, FAIL));

  // Start building the DFA. Start with state 0 and iterate through the
  // characters of `pattern`.

  // First step: Set d(0, p_0) = state(1)
  dfa[0][pattern[0]] = 1;

  // Start `state` and `new_state` both at 1
  int state = 1, new_state = 1;

  // Loop over remaining `pattern` (index 1 to the end). Because we know the
  // size of the DFA, there is no need to initialize each new state, that's
  // been done already.
  for (int i = 1; i < m; i++) {
    // Move `new_state` to the next place.
    new_state++;
    // The previous `state` maps to `new_state` on `pattern[i]`
    dfa[state][pattern[i]] = new_state;
    // `last_state` is used to control setting transitions for other values
    int last_state = state;
    for (int j = 1; j <= k; j++) {
      // For each of 1..k, we start a new state for which `pattern[i]` maps to
      // `new_state`.
      dfa[(new_state + j)][pattern[i]] = new_state;
      for (int n = 0; n < ALPHABET_COUNT; n++) {
        if (ALPHABET[n] == pattern[i])
          continue;
        // Every character that isn't `pattern[i]` needs to map `last_state` to
        // this new state-value.
        dfa[last_state][ALPHABET[n]] = new_state + j;
      }
      // Shift `last_state` for the next iteration.
      last_state = new_state + j;
    }
    // Current `state` becomes the value of `new_state`.
    state = new_state;
    // And `new_state` advances by `k`.
    new_state += k;
  }

  // At completion, the value of `state` is our terminal.
  terminal = state;
  return;
}

/*
  Initialize the pattern given. Return a 3-element array of the DFA from
  processing the pattern, the terminal state, and the pattern length m. The
  original pattern will not be needed for matching.
*/
std::vector<ApproxPatternData> init_dfa_gap(std::string const &pattern, int k) {
  std::vector<ApproxPatternData> return_val;
  return_val.reserve(3);

  // Set up the DFA structure for the algorithm to use:
  int m = pattern.length();
  int terminal;
  std::vector<std::vector<int>> dfa;
  create_dfa(pattern, m, k, dfa, terminal);

  return_val.push_back(dfa);
  return_val.push_back(terminal);
  return_val.push_back(m);

  return return_val;
}

/*
  Perform the DFA-Gap algorithm on the given (processed) pattern against the
  given sequence.
*/
int dfa_gap(std::vector<ApproxPatternData> const &pat_data,
            std::string const &sequence) {
  // Unpack pat_data:
  auto const &dfa = std::get<std::vector<std::vector<int>>>(pat_data[0]);
  int terminal = std::get<int>(pat_data[1]);
  int m = std::get<int>(pat_data[2]);

  int matches = 0;
  int n = sequence.length();

  int end = n - m;
  // Note that we have to examine from 0 to `end` inclusive, or we could miss
  // an exact pattern match at the very end of `sequence`.
  for (int i = 0; i <= end; i++) {
    int state = 0;
    int ch = 0;
    while ((i + ch) < n && dfa[state][sequence[i + ch]] != FAIL)
      state = dfa[state][sequence[i + ch++]];

    if (state == terminal)
      matches++;
  }

  return matches;
}

/*
  All that is done here is call the run() function with a pointer to the
  algorithm implementation, the label for the algorithm, and the argc/argv
  values.
*/
int main(int argc, char *argv[]) {
  int return_code = run_approx(&init_dfa_gap, &dfa_gap, "dfa_gap", argc, argv);

  return return_code;
}
