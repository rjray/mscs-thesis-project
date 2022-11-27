/*
    Implementation of the Shift-Or algorithm.

    This is based heavily on the C code given in chapter 5 of the book,
    "Handbook of Exact String-Matching Algorithms," by Christian Charras and
    Thierry Lecroq.
*/

use common::run::{run, PatternData, WordType};
use std::env;
use std::process::exit;

// Define the alphabet size, part of the Shift-Or pre-processing. Here, we
// are just using ASCII characters, so 128 is fine.
const ASIZE: usize = 128;

// We need to also know the word size in bits. For this, we're going to use
// `u64` values. This allows a search pattern of up to 64 characters, even
// though the experimental data doesn't go nearly this high. This is a sort of
// "insurance" against adding other experiments that might push this limit.
const WORD: usize = 64;

/*
    Preprocessing step: Calculate the positions of each character of the
    alphabet within the pattern `pat`. Unlike other algorithms' pre-processing,
    here it is necessary to pass s_positions[] in as a mutable parameter,
    because the algorithm needs this function to return the `limit` value.
*/
fn calc_s_positions(
    pat: &[u8],
    m: usize,
    s_positions: &mut [WordType],
) -> WordType {
    let mut j: WordType = 1;
    let mut lim: WordType = 0;

    // Assuming s_positions has already been initialized when it was created.

    for i in 0..m {
        s_positions[pat[i] as usize] &= !j;
        lim |= j;
        j <<= 1;
    }
    lim = !(lim >> 1);

    lim
}

/*
    Initialize the pattern for Shift-Or. Here, that means getting the vector
    `s_positions` set up and packing that along with `lim` into the data that
    will get passed to `shift_or` for each sequence.
*/
fn init_shift_or(pat: &[u8]) -> Vec<PatternData> {
    let mut pattern_data: Vec<PatternData> = Vec::with_capacity(2);
    let mut s_positions: Vec<WordType> = vec![!0; ASIZE];
    let m = pat.len();

    // Verify that the pattern is not too long:
    if m > WORD {
        panic!("shift_or: Pattern size must be <= {}", WORD);
    }

    // Preprocessing. Set up s_positions and lim.
    let lim: WordType = calc_s_positions(pat, m, &mut s_positions);

    pattern_data.push(PatternData::PatternWord(lim));
    pattern_data.push(PatternData::PatternWordVec(s_positions));

    pattern_data
}

/*
    Perform the Shift-Or algorithm on the given pattern of length m, against
    the sequence of length n.
*/
fn shift_or(pat_data: &[PatternData], sequence: &[u8]) -> i32 {
    let mut matches: i32 = 0;
    let mut state: WordType = !0;

    // Unpack pat_data:
    let lim = match &pat_data[0] {
        PatternData::PatternWord(val) => val,
        _ => panic!("Incorrect value at pat_data slot 0"),
    };
    let s_positions = match &pat_data[1] {
        PatternData::PatternWordVec(arr) => arr,
        _ => panic!("Incorrect value at pat_data slot 1"),
    };

    // Sizes of the sequence.
    let n = sequence.len();

    // Perform the search:
    for j in 0..n {
        state = (state << 1) | s_positions[sequence[j] as usize];
        if state < *lim {
            matches += 1;
        }
    }

    matches
}

/*
    All that is done here is call the run() function with a pointer to the
    algorithm implementation, the label for the algorithm, and the argv values.
*/
fn main() {
    let argv: Vec<String> = env::args().collect();
    exit(run(&init_shift_or, &shift_or, "shift_or", argv));
}
