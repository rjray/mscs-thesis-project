/*
  Implementation of the Aho-Corasick algorithm for multi-pattern matching.

  Unlike the single-pattern algorithms, this is not taken from prior art. This
  is coded directly from the algorithm pseudo-code in the Aho-Corasick paper.
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

// The "fail" value is used to determine certain states in the goto function.
#define FAIL -1

/*
  For the creation of the failure function, we *would* loop over all of the
  values [0, ASIZE] looking for those that are non-fail. That would be very
  inefficient, given that our alphabet is actually just four characters. Use
  this array to shorten those loops.
*/
#define OFFSETS_COUNT 4
static int ALPHA_OFFSETS[] = {65, 67, 71, 84};

/*
  Need a simple implementation of a set with just a few operations (add, grow,
  create, and clean up).
*/

// How big to create the set-storage, and how much to grow it by.
#define SET_SIZE 8
struct _Set {
  int *elements;
  int size;
  int used;
};

typedef struct _Set Set;

/*
  Create a new set instance.
*/
Set *create_set(void) {
  Set *new_set = (Set *)malloc(sizeof(Set));
  if (new_set == NULL) {
    fprintf(stderr, "create_set: malloc failed\n");
    exit(-1);
  }

  new_set->elements = (int *)calloc(SET_SIZE, sizeof(int));
  if (new_set->elements == NULL) {
    fprintf(stderr, "create_set: calloc failed\n");
    exit(-1);
  }
  new_set->size = SET_SIZE;
  new_set->used = 0;

  return new_set;
}

/*
  Delete the given set (freeing all dynamic memory).
*/
void delete_set(Set *set) {
  free(set->elements);
  free(set);

  return;
}

/*
  "Grow" the set by an extra block of SET_SIZE.
*/
void grow_set(Set *set) {
  set->size += SET_SIZE;
  set->elements = realloc(set->elements, set->size);
  if (set->elements == NULL) {
    fprintf(stderr, "grow_set: realloc failed\n");
    exit(-1);
  }

  return;
}

/*
  Add the given int to the set.
*/
void add_to_set(Set *set, const int num) {
  if (set->used == set->size)
    grow_set(set);

  set->elements[set->used++] = num;

  return;
}

/*
  Test whether the given value is in the set already.
*/
int value_in_set(Set *set, const int value) {
  int found = 0;

  for (int i = 0; i < set->used; i++)
    if (set->elements[i] == value) {
      found = 1;
      break;
    }

  return found;
}

/*
  Derive the union of the two sets, updating the first set.
*/
void set_union(Set *set1, Set *set2) {
  for (int i = 0; i < set2->used; i++) {
    int value = set2->elements[i];
    if (!value_in_set(set1, value))
      add_to_set(set1, value);
  }

  return;
}

/*
  Also need a simple integer queue to use for building the failure function. I
  can't predict the size that will be needed, so it too will have to grow
  dynamically as needed.
*/

// The initial queue size, and how much it grows by:
#define QUEUE_SIZE 16
struct _Queue {
  int *elements;
  int size;
  int head;
  int rear;
};

typedef struct _Queue Queue;

/*
  Create a new queue instance.
*/
Queue *create_queue(void) {
  Queue *new_queue = (Queue *)malloc(sizeof(Queue));
  if (new_queue == NULL) {
    fprintf(stderr, "create_queue: malloc failed\n");
    exit(-1);
  }

  new_queue->elements = (int *)calloc(QUEUE_SIZE, sizeof(int));
  if (new_queue->elements == NULL) {
    fprintf(stderr, "create_queue: calloc failed\n");
    exit(-1);
  }
  new_queue->size = QUEUE_SIZE;
  new_queue->head = new_queue->rear = -1;

  return new_queue;
}

/*
  Delete the given queue (freeing all dynamic memory).
*/
void delete_queue(Queue *queue) {
  free(queue->elements);
  free(queue);

  return;
}

/*
  Grow the storage of the queue as needed.
*/
void grow_queue(Queue *queue) {
  queue->size += QUEUE_SIZE;
  queue->elements = realloc(queue->elements, queue->size * sizeof(int));
  if (queue->elements == NULL) {
    fprintf(stderr, "grow_queue: realloc failed\n");
    exit(-1);
  }

  return;
}

/*
  Enqueue a value.
*/
void enqueue(Queue *queue, const int value) {
  // Check to see if the queue needs to be expanded:
  if (queue->rear == queue->size - 1)
    grow_queue(queue);

  if (queue->head == -1)
    queue->head = 0;

  queue->rear++;
  queue->elements[queue->rear] = value;

  return;
}

/*
  Remove the head value from the queue.
*/
int dequeue(Queue *queue) {
  if (queue->head == -1 || queue->head > queue->rear) {
    fprintf(stderr, "dequeue: Queue underflow\n");
    exit(-1);
  }

  return queue->elements[queue->head++];
}

/*
  Test if the queue is empty.
*/
int queue_empty(Queue *queue) { return (queue->head > queue->rear) ? 1 : 0; }

/*
  Enter the given pattern into the given goto-function, creating new states as
  needed. When done, add the index of the pattern into the partial output
  function for the state of the last character.
*/
void enter_pattern(unsigned char *pat, int idx, int **goto_fn,
                   Set **output_fn) {
  int len = strlen((char *)pat);
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

  add_to_set(output_fn[state], idx);

  return;
}

/*
  Build the goto function and the (partial) output function.
*/
void build_goto(unsigned char *pats[], int num_pats, int ***goto_fn,
                Set ***output_fn, int *num_states) {
  int **new_goto;
  Set **new_output;
  int max_states = 0;

  int initial_state[ASIZE];
  for (int i = 0; i < ASIZE; i++)
    initial_state[i] = -1;
  int state_size = ASIZE * sizeof(int);

  // Calculate the maximum number of states as being the sum of the lengths of
  // patterns. This is overkill, but a more "serious" implementation would
  // have a more "serious" graph implementation for the goto function.
  for (int i = 0; i < num_pats; i++)
    max_states += strlen((char *)pats[i]);
  *num_states = max_states;

  // Allocate for the goto function
  new_goto = (int **)calloc(max_states, sizeof(int *));
  if (new_goto == NULL) {
    fprintf(stderr, "build_goto: new_goto calloc failed\n");
    exit(-1);
  }
  for (int i = 0; i < max_states; i++) {
    int *ptr = malloc(state_size);
    if (ptr == NULL) {
      fprintf(stderr, "build_goto: new_goto malloc failed\n");
      exit(-1);
    } else {
      memcpy(ptr, (int *)initial_state, state_size);
      new_goto[i] = ptr;
    }
  }

  // Allocate for the output function
  new_output = (Set **)calloc(max_states, sizeof(Set *));
  if (new_output == NULL) {
    fprintf(stderr, "build_goto: new_output calloc failed\n");
    exit(-1);
  }
  for (int i = 0; i < max_states; i++)
    new_output[i] = create_set();

  // OK, now actually build the goto function and output function.

  // Add each pattern in turn:
  for (int i = 0; i < num_pats; i++)
    enter_pattern(pats[i], i, new_goto, new_output);

  // Set the unused transitions in state 0 to point back to state 0:
  for (int i = 0; i < ASIZE; i++)
    if (new_goto[0][i] == FAIL)
      new_goto[0][i] = 0;

  *goto_fn = new_goto;
  *output_fn = new_output;
  return;
}

/*
  Build the failure function and complete the output function.
*/
void build_failure(int **failure_fn, int **goto_fn, Set **output_fn,
                   int num_states) {
  // Need a simple queue of state numbers.
  Queue *queue = create_queue();

  // Allocate the failure function storage. This also needs to be as long as
  // goto_fn is, for safety.
  int *failure = (int *)malloc(num_states * sizeof(int));

  // The queue starts out empty. Set it to be all states reachable from state 0
  // and set failure(state) for those states to be 0.
  for (int i = 0; i < OFFSETS_COUNT; i++) {
    int state = goto_fn[0][ALPHA_OFFSETS[i]];
    if (state == 0)
      continue;

    enqueue(queue, state);
    failure[state] = 0;
  }

  // This uses some single-letter variable names that match the published
  // algorithm. Their mnemonic isn't clear, or else I'd use more meaningful
  // names.
  while (!queue_empty(queue)) {
    int r = dequeue(queue);
    for (int i = 0; i < OFFSETS_COUNT; i++) {
      int a = ALPHA_OFFSETS[i];
      int s = goto_fn[r][a];
      if (s == FAIL)
        continue;

      enqueue(queue, s);
      int state = failure[r];
      while (goto_fn[state][a] == FAIL)
        state = failure[state];
      failure[s] = goto_fn[state][a];
      set_union(output_fn[s], output_fn[failure[s]]);
    }
  }

  delete_queue(queue);
  *failure_fn = failure;
  return;
}

void **init_aho_corasick(unsigned char **patterns_data, int patterns_count) {
  void **return_val = (void **)calloc(5, sizeof(void *));
  int *pat_count = (int *)calloc(1, sizeof(int));
  *pat_count = patterns_count;

  // Initialize the multi-pattern structure.
  int **goto_fn;
  int *failure_fn;
  Set **output_fn;
  int num_states;
  build_goto((unsigned char **)patterns_data, patterns_count, &goto_fn,
             &output_fn, &num_states);
  build_failure(&failure_fn, goto_fn, output_fn, num_states);

  return_val[0] = (void *)pat_count;
  return_val[1] = (void *)goto_fn;
  return_val[2] = (void *)failure_fn;
  return_val[3] = (void *)output_fn;

  return return_val;
}

/*
  Perform the Aho-Corasick algorithm against the given sequence. No pattern is
  passed in, as the machine of goto_fn/failure_fn/output_fn will handle all the
  patterns in a single pass.

  Instead of returning a single int, returns an array of ints as long as the
  number of patterns (pattern_count).
*/
int *aho_corasick(void **pat_data, unsigned char *sequence) {
  int state = 0;
  int n = strlen((const char *)sequence);

  // Unpack pat_data:
  int *pattern_count = (int *)pat_data[0];
  int **goto_fn = (int **)pat_data[1];
  int *failure_fn = (int *)pat_data[2];
  Set **output_fn = (Set **)pat_data[3];

  int *matches = (int *)calloc(*pattern_count, sizeof(int));
  if (matches == NULL) {
    fprintf(stderr, "aho_corasick: matches calloc failed\n");
    exit(-1);
  }

  for (int i = 0; i < n; i++) {
    while (goto_fn[state][sequence[i]] == FAIL)
      state = failure_fn[state];

    state = goto_fn[state][sequence[i]];
    for (int m = 0; m < output_fn[state]->used; m++)
      matches[output_fn[state]->elements[m]]++;
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
