/*
  Implementation of the (tentatively-title) DFA-Gap algorithm for approximate
  string matching.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "run.h"

#if defined(__INTEL_LLVM_COMPILER)
#define LANG "c-intel"
#elif defined(__llvm__)
#define LANG "c-llvm"
#elif defined(__GNUC__)
#define LANG "c-gcc"
#endif

// Rather than implement a translation table for the four characters in the DNA
// alphabet, for now just let the alphabet be the full ASCII range and only use
// those four.
#define ASIZE 128

// The "fail" value is used to determine when to start over.
#define FAIL -1

/*
  For the creation of the failure function, we *would* loop over all of the
  values [0, ASIZE] looking for those that are non-fail. That would be very
  inefficient, given that our alphabet is actually just four characters. Use
  this array to shorten those loops.
*/
#define ALPHABET_COUNT 4
static int ALPHABET[] = {65, 67, 71, 84};

void create_dfa(unsigned char *pattern, int m, int k, int ***dfa, int *A) {
  // Create a template of a state that can be memcpy'd into new states.
  int initial_state[ASIZE];
  for (int i = 0; i < ASIZE; i++)
    initial_state[i] = FAIL;
  int state_size = ASIZE * sizeof(int);

  // We know that the number of states will be m + 1 + k(m - 1).
  int max_states = m + 1 + k * (m - 1);

  // Allocate for the DFA
  int **new_dfa = (int **)calloc(max_states, sizeof(int *));
  if (new_dfa == NULL) {
    fprintf(stderr, "build_goto: create_dfa calloc failed\n");
    exit(-1);
  }
  for (int i = 0; i < max_states; i++) {
    int *ptr = malloc(state_size);
    if (ptr == NULL) {
      fprintf(stderr, "build_goto: create_dfa malloc failed\n");
      exit(-1);
    } else {
      memcpy(ptr, (int *)initial_state, state_size);
      new_dfa[i] = ptr;
    }
  }

  // Start building the DFA. Start with state 0 and iterate through the
  // characters of pattern.

  // First step: Set d(0, p_0) = state(1)
  new_dfa[0][pattern[0]] = 1;

  // Start `state` and `new_state` both at 1
  int state = 1, new_state = 1;

  // Loop over remaining pattern (index 1 to the end). Because we know the size
  // of the DFA, there is no need to initialize each new state, that's been
  // done already.
  for (int i = 1; i < m; i++) {
    // Move `new_state` to the next place.
    new_state++;
    // The previous `state` maps to `new_state` on pattern[i]
    new_dfa[state][pattern[i]] = new_state;
    // `last_state` is used to control setting transitions for other values
    int last_state = state;
    for (int j = 1; j <= k; j++) {
      // For each of 1..k, we start a new state for which pattern[i] maps to
      // `new_state`.
      new_dfa[new_state + j][pattern[i]] = new_state;
      for (int n = 0; n < ALPHABET_COUNT; n++) {
        if (ALPHABET[n] == pattern[i])
          continue;
        // Every character that isn't pattern[i] needs to map `last_state` to
        // this new state-value.
        new_dfa[last_state][ALPHABET[n]] = new_state + j;
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
  *A = state;
  // Assign the new DFA to the given pointer to return it.
  *dfa = new_dfa;
  return;
}

/*
  Initialize the pattern given. Return a 3-element array of the DFA from
  processing the pattern, the terminal state, and the pattern length m. The
  original pattern will not be needed for matching.
*/
void **init_dfa_gap(unsigned char *pattern, int k) {
  void **return_val = (void **)calloc(4, sizeof(void *));

  // Set up the DFA structure for the algorithm to use:
  int *m = (int *)calloc(1, sizeof(int));
  *m = strlen((const char *)pattern);
  int **dfa;
  int *terminal = (int *)calloc(1, sizeof(int));
  create_dfa(pattern, *m, k, &dfa, terminal);

  return_val[0] = (void *)dfa;
  return_val[1] = (void *)terminal;
  return_val[2] = (void *)m;

  return return_val;
}

/*
  Perform the DFA-Gap algorithm on the given (processed) pattern against the
  given sequence.
*/
int dfa_gap(void **pat_data, unsigned char *sequence) {
  int **dfa = (int **)pat_data[0];
  int terminal = *((int *)pat_data[1]);
  int m = *((int *)pat_data[2]);
  int matches = 0;
  int n = strlen((const char *)sequence);

  int end = n - m;
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
