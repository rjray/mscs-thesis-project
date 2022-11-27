/*
    Implementation of the Knuth-Morris-Pratt algorithm.

    This is based heavily on the C code given in chapter 7 of the book,
    "Handbook of Exact String-Matching Algorithms," by Christian Charras and
    Thierry Lecroq.
*/

use common::run::{run, PatternData};
use std::env;
use std::process::exit;

/*
   Initialize the jump-table that KMP uses. Unlike the C code, which takes a
   pre-allocated pointer as an argument, this code returns a vector structure
   for the table. Rust's ownership mechanism will take care of freeing this
   when it is no longer needed.
*/
fn build_next_table(pat: &[u8], m: usize) -> Vec<i32> {
    let mut next_table: Vec<i32> = vec![0; m + 1];
    let mut i: usize = 0;
    let mut j: i32 = -1;
    next_table[0] = -1;

    while i < m {
        while j > -1 && pat[i] != pat[j as usize] {
            j = next_table[j as usize];
        }
        i += 1;
        j += 1;
        if i < m && pat[i] == pat[j as usize] {
            next_table[i] = next_table[j as usize];
        } else {
            next_table[i] = j;
        }
    }

    next_table
}

/*
    Initialize the pattern for Knuth-Morris-Pratt and save the elements in the
    packed form for use with calls to `kmp`.
*/
fn init_kmp(pat: &[u8]) -> Vec<PatternData> {
    let m = pat.len();
    let mut pattern_data: Vec<PatternData> = Vec::with_capacity(2);

    // Because the C code takes advantage of the presence of a null byte at the
    // end of strings, we have to force this in and re-convert the pattern to a
    // &[u8].
    let mut new_vec = pat.to_vec();
    new_vec.push(0);
    let new_pat = new_vec.as_slice();

    // Obtain the jump-table.
    let next_table = build_next_table(new_pat, m);

    pattern_data.push(PatternData::PatternU8Vec(new_pat.to_owned()));
    pattern_data.push(PatternData::PatternIntVec(next_table));

    pattern_data
}

/*
    Perform the KMP algorithm on the given pattern of length m, against the
    sequence of length n.
*/
fn kmp(pat_data: &[PatternData], sequence: &[u8]) -> i32 {
    let mut i: i32 = 0;
    let mut j: usize = 0;
    // Track the number of times the pattern is found in the sequence.
    let mut matches: i32 = 0;

    // Unpack pat_data:
    let pattern = match &pat_data[0] {
        PatternData::PatternU8Vec(pat_as_vec) => pat_as_vec,
        _ => panic!("Incorrect value at pat_data slot 0"),
    };
    let next_table = match &pat_data[1] {
        PatternData::PatternIntVec(table) => table,
        _ => panic!("Incorrect value at pat_data slot 1"),
    };

    // Sizes of pattern and sequence. Account for the sentinel character added
    // to the pattern.
    let m = pattern.len() - 1;
    let n = sequence.len();

    // The core algorithm.
    while j < n {
        while i > -1 && pattern[i as usize] != sequence[j] {
            i = next_table[i as usize];
        }
        i += 1;
        j += 1;
        if i >= m as i32 {
            matches += 1;
            i = next_table[i as usize];
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
    exit(run(&init_kmp, &kmp, "kmp", argv));
}
