/*
    Implementation of the Shift-Or algorithm.

    This is based heavily on the C code given in chapter 5 of the book,
    "Handbook of Exact String-Matching Algorithms," by Christian Charras and
    Thierry Lecroq.
*/

use common::run::run;
use std::cmp::Ordering;
use std::env;

// Define the alphabet size, part of the Shift-Or pre-processing. Here, we
// are just using ASCII characters, so 128 is fine.
const ASIZE: usize = 128;

// We need to also know the word size in bits. For this, we're going to use
// `u64` values. This allows a search pattern of up to 64 characters, even
// though the experimental data doesn't go nearly this high. This is a sort of
// "insurance" against adding other experiments that might push this limit.
const WORD: usize = 64;
type WordType = u64;

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
    Perform the Shift-Or algorithm on the given pattern of length m, against
    the sequence of length n.
*/
fn shift_or(pattern: &String, m: usize, sequence: &String, n: usize) -> i32 {
    // For indexing that would be comparable to C's, convert the String objects
    // to arrays of bytes. This works because the UTF-8 data won't have any
    // wide characters.
    let pattern = pattern.as_bytes();
    let sequence = sequence.as_bytes();
    let mut matches: i32 = 0;
    let mut state: WordType = !0;
    let mut s_positions: Vec<WordType> = vec![state; ASIZE];

    // Verify that the pattern is not too long:
    if m > WORD {
        eprintln!("shift_or: Pattern size must be <= {}", WORD);
        return -1;
    }

    // Preprocessing. Set up s_positions and lim.
    let lim: WordType = calc_s_positions(pattern, m, &mut s_positions);

    // Perform the search:
    for j in 0..n {
        state = (state << 1) | s_positions[sequence[j] as usize];
        if state < lim {
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
    let code: i32 = run(&shift_or, "shift_or", &argv);

    match code.cmp(&0) {
        Ordering::Less => eprintln!("Program encountered internal error."),
        Ordering::Greater => {
            eprintln!("Program encountered {} mismatches.", code);
        }
        Ordering::Equal => (),
    };
}
