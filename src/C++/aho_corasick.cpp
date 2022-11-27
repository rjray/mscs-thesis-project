/*
  Implementation of the Aho-Corasick algorithm for multi-pattern matching.

  Unlike the single-pattern algorithms, this is not taken from prior art. This
  is coded directly from the algorithm pseudo-code in the Aho-Corasick paper.
*/

#include <queue>
#include <set>
#include <string>
#include <vector>

#include "run.hpp"

// Rather than implement a translation table for the four characters in the DNA
// alphabet, for now just let the alphabet be the full ASCII range and only use
// those four.
constexpr int ASIZE = 128;

// The "fail" value is used to determine certain states in the goto
// function.
constexpr int FAIL = -1;

/*
  For the creation of the failure function, we *would* loop over all of
  the values [0, ASIZE] looking for those that are non-fail. That would
  be very inefficient, given that our alphabet is actually just four
  characters. Use this array to shorten those loops.
*/
constexpr int OFFSETS_COUNT = 4;
static std::vector<int> ALPHA_OFFSETS = {65, 67, 71, 84};

/*
  Enter the given pattern into the given goto-function, creating new states as
  needed. When done, add the index of the pattern into the partial output
  function for the state of the last character.
*/
void enter_pattern(std::string const &pat, int idx,
                   std::vector<std::vector<int>> &goto_fn,
                   std::vector<std::set<int>> &output_fn) {
  int len = pat.length();
  int j = 0, state = 0;
  static int new_state = 0;

  // Find the first leaf corresponding to a character in `pat`. From there is
  // where a new state (if needed) will be added.
  while (goto_fn[state][pat[j]] != FAIL) {
    state = goto_fn[state][pat[j]];
    j++;
  }

  // At this point, `state` points to the leaf in the automaton. Create new
  // states from here on for the remaining characters in `pat` that weren't
  // already in the automaton.
  for (int p = j; p < len; p++) {
    new_state++;
    goto_fn[state][pat[p]] = new_state;
    state = new_state;
  }

  output_fn[state].insert(idx);
}

/*
  Build the goto function and the (partial) output function.
*/
void build_goto(std::vector<std::string> const &pats, int num_pats,
                std::vector<std::vector<int>> &goto_fn,
                std::vector<std::set<int>> &output_fn) {
  int max_states = 0;

  // Calculate the maximum number of states as being the sum of the lengths of
  // patterns. This is overkill, but a more "serious" implementation would
  // have a more "serious" graph implementation for the goto function.
  for (int i = 0; i < num_pats; i++)
    max_states += pats[i].length();

  // Allocate for the goto function
  goto_fn.resize(max_states, std::vector<int>(ASIZE, FAIL));

  // Allocate for the output function
  output_fn.resize(max_states, std::set<int>());

  // OK, now actually build the goto function and output function.

  // Add each pattern in turn:
  for (int i = 0; i < num_pats; i++)
    enter_pattern(pats[i], i, goto_fn, output_fn);

  // Set the unused transitions in state 0 to point back to state 0:
  for (int i = 0; i < OFFSETS_COUNT; i++)
    if (goto_fn[0][ALPHA_OFFSETS[i]] == FAIL)
      goto_fn[0][ALPHA_OFFSETS[i]] = 0;
}

/*
  Build the failure function and complete the output function.
*/
std::vector<int> build_failure(std::vector<std::vector<int>> const &goto_fn,
                               std::vector<std::set<int>> &output_fn) {
  // Need a simple queue of state numbers.
  std::queue<int> queue;

  // Allocate the failure function storage. This also needs to be as long as
  // goto_fn is, for safety. Initializing all of its slots to 0 will allow a
  // shortcut or two in the rest of the algorithm.
  std::vector<int> failure_fn;
  failure_fn.resize(goto_fn.size(), 0);

  // The queue starts out empty. Set it to be all states reachable from state 0
  // and set failure(state) for those states to be 0.
  for (int i = 0; i < OFFSETS_COUNT; i++) {
    int state = goto_fn[0][ALPHA_OFFSETS[i]];
    if (state == 0)
      continue;

    queue.push(state);
  }

  // This uses some single-letter variable names that match the published
  // algorithm. Their mnemonic isn't clear, or else I'd use more meaningful
  // names.
  while (!queue.empty()) {
    int r = queue.front();
    queue.pop();
    for (int i = 0; i < OFFSETS_COUNT; i++) {
      int a = ALPHA_OFFSETS[i];
      int s = goto_fn[r][a];
      if (s == FAIL)
        continue;

      queue.push(s);
      int state = failure_fn[r];
      while (goto_fn[state][a] == FAIL)
        state = failure_fn[state];
      failure_fn[s] = goto_fn[state][a];
      output_fn[s].insert(output_fn[failure_fn[s]].begin(),
                          output_fn[failure_fn[s]].end());
    }
  }

  return failure_fn;
}

/*
  Initialize the structure for Aho-Corasick. Here, that means merging the list
  of patterns into a single DFA. The return value is a vector of the
  `MultiPatternData` type, which is a type-safe union of sorts that covers the
  different types that have to be returned.
*/
std::vector<MultiPatternData>
init_aho_corasick(std::vector<std::string> const &patterns_data) {
  std::vector<MultiPatternData> return_val;
  return_val.reserve(4);
  int patterns_count = patterns_data.size();

  // Initialize the multi-pattern structure.
  std::vector<std::vector<int>> goto_fn;
  std::vector<std::set<int>> output_fn;
  build_goto(patterns_data, patterns_count, goto_fn, output_fn);
  std::vector<int> failure_fn = build_failure(goto_fn, output_fn);

  return_val.push_back(patterns_count);
  return_val.push_back(goto_fn);
  return_val.push_back(failure_fn);
  return_val.push_back(output_fn);

  return return_val;
}

/*
  Perform the Aho-Corasick algorithm against the given sequence. No pattern is
  passed in, as the machine of goto_fn/failure_fn/output_fn will handle all the
  patterns in a single pass.

  Instead of returning a single int, returns an array of ints as long as the
  number of patterns (pattern_count).
*/
std::vector<int> aho_corasick(std::vector<MultiPatternData> const &pat_data,
                              std::string const &sequence) {
  // Unpack pat_data
  int pattern_count = std::get<int>(pat_data[0]);
  auto const &goto_fn = std::get<std::vector<std::vector<int>>>(pat_data[1]);
  auto const &failure_fn = std::get<std::vector<int>>(pat_data[2]);
  auto const &output_fn = std::get<std::vector<std::set<int>>>(pat_data[3]);

  int state = 0;
  int n = sequence.length();
  std::vector<int> matches;
  matches.resize(pattern_count, 0);

  for (int i = 0; i < n; i++) {
    while (goto_fn[state][sequence[i]] == FAIL)
      state = failure_fn[state];

    state = goto_fn[state][sequence[i]];
    for (std::set<int>::iterator idx = output_fn[state].begin();
         idx != output_fn[state].end(); idx++)
      matches[*idx]++;
  }

  return matches;
}

/*
  All that is done here is call the run() function with the argc/argv values.
*/
int main(int argc, char *argv[]) {
  int return_code =
      run_multi(&init_aho_corasick, &aho_corasick, "aho_corasick", argc, argv);

  return return_code;
}
