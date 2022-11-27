/*
    Implementation of the Aho-Corasick algorithm for multi-pattern matching.

    Unlike the single-pattern algorithms, this is not taken from prior art.
    This is coded directly from the algorithm pseudo-code in the Aho-Corasick
    paper. (This Rust implementation is based on the C implementation
    previously done.)
*/

use common::run::{run_multi, MultiPatternData};
use std::env;
use std::process::exit;

// Rather than implement a translation table for the four characters in the DNA
// alphabet, for now just let the alphabet be the full ASCII range and only use
// those four.
const ASIZE: usize = 128;

// The "fail" value is used to determine certain states in the goto function.
const FAIL: i32 = -1;

/*
    For the creation of the failure function, we *would* loop over all of the
    values [0, ASIZE] looking for those that are non-fail. That would be very
    inefficient, given that our alphabet is actually just four characters. Use
    this array to shorten those loops.
*/
const ALPHA_OFFSETS: &[usize] = &[65, 67, 71, 84];

/*
    This basic "set" implementation was provided by Andrew Gallant when helping
    me determine the reason for this version being so much slower than the C
    and C++ versions.
*/
#[derive(Clone, Debug)]
struct Set {
    elements: Vec<usize>,
}

impl Set {
    fn new() -> Set {
        Set {
            elements: Vec::with_capacity(8),
        }
    }

    fn insert(&mut self, element: usize) {
        self.elements.push(element);
    }

    fn contains(&self, element: usize) -> bool {
        self.elements.contains(&element)
    }

    fn iter(&self) -> core::slice::Iter<'_, usize> {
        self.elements.iter()
    }

    fn union(&mut self, other: &Set) {
        for &element in other.elements.iter() {
            if !self.contains(element) {
                self.insert(element);
            }
        }
    }
}

/*
    As with the "set", above, I implemented the simple queue in the same basic
    fashion, as the standard-library implementation (Vec::Deque) slowed the
    program down.
*/
#[derive(Clone, Debug)]
struct Queue {
    elements: Vec<usize>,
    head: usize,
}

impl Queue {
    fn new() -> Queue {
        Queue {
            elements: Vec::with_capacity(32),
            head: 0,
        }
    }

    fn is_empty(&self) -> bool {
        self.head == self.elements.len()
    }

    fn enqueue(&mut self, element: usize) {
        self.elements.push(element);
    }

    fn dequeue(&mut self) -> usize {
        if self.is_empty() {
            panic!("Queue::dequeue: underflow");
        }
        let value = self.elements[self.head];
        self.head += 1;
        value
    }
}

/*
    Simple function to create a new state for the goto_fn.
*/
fn create_new_state() -> Vec<i32> {
    let new_state = vec![FAIL; ASIZE];
    new_state
}

/*
    Enter the given pattern into the given goto-function, creating new states
    as needed. When done, add the index of the pattern into the partial output
    function for the state of the last character.

    Because Rust's equivalent of C's `static` data requires using `unsafe` to
    update it (which I don't want to do in these experiments), this function
    takes the current value of `new_state` and updates it as a mutable value.
*/
fn enter_pattern(
    new_state: &mut usize,
    pat: &[u8],
    idx: usize,
    goto_fn: &mut Vec<Vec<i32>>,
    output_fn: &mut Vec<Set>,
) {
    let len = pat.len();
    let mut j: usize = 0;
    let mut state: usize = 0;

    // Find the first leaf corresponding to a character in `pat`. From there is
    // where a new state (if needed) will be added.
    while goto_fn[state][pat[j] as usize] != FAIL {
        state = goto_fn[state][pat[j] as usize] as usize;
        j += 1;
    }

    // At this point, `state` points to the leaf in the automaton. Create new
    // states from here on for the remaining characters in `pat` that weren't
    // already in the automaton.
    for p in pat.iter().take(len).skip(j) {
        *new_state += 1;
        goto_fn[state][*p as usize] = *new_state as i32;
        state = *new_state;
        // Unlike the C code, the availability of Vec as a native type allows
        // the automaton to be dynamically grown as needed. So we have to
        // create the new state and append it to goto_fn. Also have to create
        // a new set object and add it to output_fn.
        goto_fn.push(create_new_state());
        output_fn.push(Set::new());
    }

    // Add the index of this pattern to the output_fn set for this state:
    output_fn[state].insert(idx);
}

/*
    Build the goto function and the (partial) output function.
*/
fn build_goto(
    patterns: &[&[u8]],
    goto_fn: &mut Vec<Vec<i32>>,
    output_fn: &mut Vec<Set>,
) {
    // This value tracks the current high state number and is used in
    // successive calls to enter_pattern() to know what index new states are
    // created at.
    let mut new_state: usize = 0;

    // Initialize state 0 for goto_fn and output_fn.
    goto_fn.push(create_new_state());
    output_fn.push(Set::new());

    // Add each pattern in turn:
    for (i, pattern) in patterns.iter().enumerate() {
        enter_pattern(&mut new_state, pattern, i, goto_fn, output_fn);
    }

    // Set any unused transitions in state 0 to point back to state 0:
    for i in 0..ASIZE {
        if goto_fn[0][i] == FAIL {
            goto_fn[0][i] = 0;
        }
    }
}

/*
    Build the failure function and complete the output function.
*/
fn build_failure(goto_fn: &[Vec<i32>], output_fn: &mut [Set]) -> Vec<usize> {
    // Need a queue of state numbers:
    let mut queue = Queue::new();

    // The failure function is accessed more randomly than the goto function or
    // the output function. So, pre-allocate it to the size of goto_fn.
    let mut failure_fn: Vec<usize> = vec![0; goto_fn.len()];

    // The queue starts out empty. Set it to be all states reachable from state
    // 0 and set failure(state) for those states to be 0.
    for i in ALPHA_OFFSETS {
        let state = goto_fn[0][*i];
        if state == 0 {
            continue;
        }

        queue.enqueue(state as usize);
        failure_fn[state as usize] = 0;
    }

    // This uses some single-letter variable names that match the published
    // algorithm. Their mnemonic isn't clear, or else I'd use more meaningful
    // names.
    while !queue.is_empty() {
        let r = queue.dequeue();

        for a in ALPHA_OFFSETS {
            let s = goto_fn[r][*a];
            if s == FAIL {
                continue;
            }
            let ss = s as usize;

            queue.enqueue(ss);
            let mut state = failure_fn[r];
            while goto_fn[state][*a] == FAIL {
                state = failure_fn[state];
            }
            failure_fn[ss] = goto_fn[state][*a] as usize;
            let failure_set = output_fn[failure_fn[ss]].clone();
            output_fn[ss].union(&failure_set);
        }
    }

    failure_fn
}

/*
    Initialize the DFA structure for Aho-Corasick and pack it into a vector
    that can be passed to subsequent calls to `aho_corasick` itself.
*/
fn init_aho_corasick(patterns: &[&[u8]]) -> Vec<MultiPatternData<Set>> {
    let mut pattern_data: Vec<MultiPatternData<Set>> = Vec::with_capacity(4);

    // Initialize the multi-patterns structure.
    let mut goto_fn: Vec<Vec<i32>> = Vec::new();
    let mut output_fn: Vec<Set> = Vec::new();
    build_goto(patterns, &mut goto_fn, &mut output_fn);
    let failure_fn = build_failure(&goto_fn, &mut output_fn);

    pattern_data.push(MultiPatternData::PatternCount(patterns.len()));
    pattern_data.push(MultiPatternData::PatternIntVecVec(goto_fn));
    pattern_data.push(MultiPatternData::PatternUsizeVec(failure_fn));
    pattern_data.push(MultiPatternData::PatternTypeVec(output_fn));

    pattern_data
}

/*
    Perform the Aho-Corasick algorithm against the given sequence. No pattern
    is passed in, as the machine of goto_fn/failure_fn/output_fn given in the
    `pat_data` vector will handle all the patterns in a single pass.

    Instead of returning a single u32, this returns a Vec<u32> with size equal
    to `pattern_count`.
*/
fn aho_corasick(
    pat_data: &[MultiPatternData<Set>],
    sequence: &[u8],
) -> Vec<u32> {
    // Unpack pat_data:
    let pattern_count = match &pat_data[0] {
        MultiPatternData::PatternCount(val) => val,
        _ => panic!("Incorrect value at pat_data slot 0"),
    };
    let goto_fn = match &pat_data[1] {
        MultiPatternData::PatternIntVecVec(val) => val,
        _ => panic!("Incorrect value at pat_data slot 1"),
    };
    let failure_fn = match &pat_data[2] {
        MultiPatternData::PatternUsizeVec(val) => val,
        _ => panic!("Incorrect value at pat_data slot 2"),
    };
    let output_fn = match &pat_data[3] {
        MultiPatternData::PatternTypeVec(val) => val,
        _ => panic!("Incorrect value at pat_data slot 3"),
    };

    let mut matches: Vec<u32> = vec![0; *pattern_count];
    let mut state: usize = 0;

    for s in sequence.iter() {
        while goto_fn[state][*s as usize] == FAIL {
            state = failure_fn[state];
        }

        state = goto_fn[state][*s as usize] as usize;
        for j in output_fn[state].iter() {
            matches[*j] += 1;
        }
    }

    matches
}

/*
    All that is done here is call the run() function with the argv values.
*/
fn main() {
    let argv: Vec<String> = env::args().collect();
    exit(run_multi(
        &init_aho_corasick,
        &aho_corasick,
        "aho_corasick",
        argv,
    ));
}
