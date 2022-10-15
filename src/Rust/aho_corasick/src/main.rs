/*
    Implementation of the Aho-Corasick algorithm for multi-pattern matching.

    Unlike the single-pattern algorithms, this is not taken from prior art.
    This is coded directly from the algorithm pseudo-code in the Aho-Corasick
    paper. (This Rust implementation is based on the C implementation
    previously done.)
*/

use common::setup::*;
use std::env;
use std::process::exit;
use std::time::Instant;

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
    // where a new state (if needed) will be added. Note that the original
    // algorithm did not account for pattern `pat` being a substring of an
    // existing pattern in the goto function. The break-test is added to avoid
    // the counter `j` going past the end of `pat`.
    while goto_fn[state][pat[j] as usize] != FAIL {
        state = goto_fn[state][pat[j] as usize] as usize;
        j += 1;
        if j == len {
            break;
        }
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
#[inline(never)]
fn build_goto(
    patterns: &[String],
    goto_fn: &mut Vec<Vec<i32>>,
    output_fn: &mut Vec<Set>,
) {
    // Convert the vector of strings into arrays of `u8`.
    let pats: Vec<&[u8]> = patterns.iter().map(|p| p.as_bytes()).collect();
    // This value tracks the current high state number and is used in
    // successive calls to enter_pattern() to know what index new states are
    // created at.
    let mut new_state: usize = 0;

    // Initialize state 0 for goto_fn and output_fn.
    goto_fn.push(create_new_state());
    output_fn.push(Set::new());

    // Add each pattern in turn:
    for (i, pattern) in pats.iter().enumerate() {
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
#[inline(never)]
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
    Perform the Aho-Corasick algorithm against the given sequence. No pattern
    is passed in, as the machine of goto_fn/failure_fn/output_fn will handle
    all the patterns in a single pass.

    Instead of returning a single u32, this returns a Vec<u32> with size equal
    to `pattern_count`.
*/
#[inline(never)]
fn aho_corasick(
    sequence: &String,
    pattern_count: usize,
    goto_fn: &[Vec<i32>],
    failure_fn: &[usize],
    output_fn: &[Set],
) -> Vec<u32> {
    let sequence = sequence.as_bytes();
    let mut matches: Vec<u32> = vec![0; pattern_count];
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
    This is a customization of the runner function used for the single-pattern
    matching algorithms. This one sets up the structures needed for the A-C
    algorithm, then iterates over the sequences (since iterating over the
    patterns is not necessary).

    The return value is 0 if the experiment correctly identified all pattern
    instances in all sequences, and the number of misses otherwise.
*/
pub fn run(argv: Vec<String>) -> i32 {
    let argc = argv.len();
    if !(3..=4).contains(&argc) {
        eprintln!("Usage: {} <sequences> <patterns> [ <answers> ]", &argv[0]);
        return -1;
    }

    // Read the data files using the routines from common::setup. The answers
    // data uses Option<> since it does not have to be provided.
    let sequences_data: Vec<String> = read_sequences(&argv[1]);
    let patterns_data: Vec<String> = read_patterns(&argv[2]);
    let answers_data: Option<Vec<Vec<u32>>> = if argc == 4 {
        Some(read_answers(&argv[3]))
    } else {
        None
    };

    // If answers were provided, check that the number of lines matches the
    // number of patterns.
    if let Some(ref answers) = answers_data {
        if answers.len() != patterns_data.len() {
            eprintln!("Count mismatch between patterns file and answers file");
            return -1;
        }
    }

    // Run the given code. For each sequence, try each pattern against it. The
    // `code` function pointer will return the number of matches found, which
    // will be compared to the table of answers for that pattern. Report any
    // mismatches.
    let start_time = Instant::now();
    let mut return_code: i32 = 0;

    // Initialize the multi-patterns structure.
    let mut goto_fn: Vec<Vec<i32>> = Vec::new();
    let mut output_fn: Vec<Set> = Vec::new();
    build_goto(&patterns_data, &mut goto_fn, &mut output_fn);
    let failure_fn = build_failure(&goto_fn, &mut output_fn);

    for (sequence, sequence_str) in sequences_data.iter().enumerate() {
        // Here, we don't iterate over the patterns. We just call the matching
        // function and pass it the three "machine" elements set up in the
        // initialization code, above.
        let matches = aho_corasick(
            sequence_str,
            patterns_data.len(),
            &goto_fn,
            &failure_fn,
            &output_fn,
        );

        if let Some(ref answers) = answers_data {
            for pattern in 0..patterns_data.len() {
                if matches[pattern] != answers[pattern][sequence] {
                    eprintln!(
                        "Pattern {} mismatch against sequence {} ({} != {})",
                        pattern + 1,
                        sequence + 1,
                        matches[pattern],
                        answers[pattern][sequence]
                    );

                    return_code += 1;
                }
            }
        }
    }

    // Note the end time before doing anything else.
    let elapsed = start_time.elapsed();
    println!("language: rust\nalgorithm: aho_corasick");
    println!("runtime: {:.8}", elapsed.as_secs_f64());

    return_code
}

/*
    All that is done here is call the run() function with the argv values.
*/
fn main() {
    let argv: Vec<String> = env::args().collect();
    exit(run(argv));
}
