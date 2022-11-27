/*
    Rust implementation of the (tentatively-title) DFA-Gap algorithm for
    approximate string matching.
*/

use common::run::{run_approx, ApproxPatternData};
use std::env;
use std::process::exit;

// Rather than implement a translation table for the four characters in the DNA
// alphabet, for now just let the alphabet be the full ASCII range and only use
// those four.
const ASIZE: usize = 128;

// The "fail" value is used to determine when to start over.
const FAIL: i32 = -1;

/*
    The ALPHABET values are used when setting up the transitions around the
    "gap" states in the DFA. Since we're being lazy about translating ACGT to
    0-3 and using an alphabet of 128 instead, this will save some time in loops
    during the creation of the DFA.
*/
const ALPHABET: &[usize] = &[65, 67, 71, 84];

fn create_dfa(
    pattern: &[u8],
    m: usize,
    k: u32,
    dfa: &mut Vec<Vec<i32>>,
) -> usize {
    // We know that the number of states will be 1 + m + k(m - 1).
    let max_states: usize = 1 + m + k as usize * (m - 1);

    // Allocate the DFA
    for _ in 0..max_states {
        dfa.push(vec![FAIL; ASIZE]);
    }

    // First step: set dfa[0][pattern[0]] = state(1)
    dfa[0][pattern[0] as usize] = 1;

    // Start `state` and `new_state` both at 1
    let mut state: usize = 1;
    let mut new_state: usize = 1;

    // Loop over remaining `pattern` (index 1 to the end). Because we know the
    // size of the DFA, there is no need to initialize each new state, that's
    // been done already.
    for i in 1..m {
        // Move `new_state` to the next place.
        new_state += 1;
        // The previous `state` maps to `new_state` on `pattern[i]`
        dfa[state][pattern[i] as usize] = new_state as i32;
        // `last_state` is used to control setting transitions for other values
        let mut last_state = state;
        for j in 1..=k {
            // For each of 1..k, we start a new state for which `pattern[i]`
            // maps to `new_state`.
            dfa[(new_state + j as usize)][pattern[i] as usize] =
                new_state as i32;
            for n in ALPHABET {
                if *n == pattern[i] as usize {
                    continue;
                }
                // Every character that isn't `pattern[i]` needs to map
                // `last_state` to this new state-value.
                dfa[last_state][*n] = (new_state + j as usize) as i32;
            }
            // Shift `last_state` for the next iteration.
            last_state = new_state + j as usize;
        }
        // Current `state` becomes the value of `new_state`.
        state = new_state;
        // And `new_state` advances by `k`.
        new_state += k as usize;
    }

    // At completion, the value of `state` is our terminal.
    state
}

/*
    Initialize the DFA for the pattern and store the data in the packed form
    that will be passed to `dfa_gap` for each sequence being matched.
*/
fn init_dfa_gap(pattern: &[u8], k: u32) -> Vec<ApproxPatternData> {
    let mut pattern_data: Vec<ApproxPatternData> = Vec::with_capacity(3);

    // Initialize the elements for the multi-patterns structure.
    let mut dfa: Vec<Vec<i32>> = Vec::new();
    let m = pattern.len();
    let terminal = create_dfa(pattern, m, k, &mut dfa);

    // Pack the return structure.
    pattern_data.push(ApproxPatternData::PatternIntVecVec(dfa));
    pattern_data.push(ApproxPatternData::PatternUsize(terminal));
    pattern_data.push(ApproxPatternData::PatternUsize(m));

    pattern_data
}

/*
    Perform the DFA-Gap algorithm on the given sequence, using the pattern data
    passed in.
*/
fn dfa_gap(pat_data: &[ApproxPatternData], sequence: &[u8]) -> i32 {
    // Unpack pat_data:
    let dfa = match &pat_data[0] {
        ApproxPatternData::PatternIntVecVec(val) => val,
        _ => panic!("Incorrect value at pat_data slot 0"),
    };
    let terminal = match &pat_data[1] {
        ApproxPatternData::PatternUsize(val) => val,
        _ => panic!("Incorrect value at pat_data slot 1"),
    };
    let m = match &pat_data[2] {
        ApproxPatternData::PatternUsize(val) => val,
        _ => panic!("Incorrect value at pat_data slot 2"),
    };

    let mut matches = 0;
    let n = sequence.len();

    let end = n - m;
    // Note that we have to examine from 0 to `end` inclusive, or we could miss
    // an exact pattern match at the very end of `sequence`.
    for i in 0..=end {
        let mut state: usize = 0;
        let mut ch: usize = 0;

        while (i + ch) < n && dfa[state][sequence[i + ch] as usize] != FAIL {
            state = dfa[state][sequence[i + ch] as usize] as usize;
            ch += 1;
        }

        if state == *terminal {
            matches += 1;
        }
    }

    matches
}

/*
    All that is done here is call the run_approx() function with the values.
*/
fn main() {
    let argv: Vec<String> = env::args().collect();
    exit(run_approx(&init_dfa_gap, &dfa_gap, "dfa_gap", argv));
}
