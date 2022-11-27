/*
    Implementation of the Boyer-Moore algorithm.

    This is based heavily on the C code given in chapter 14 of the book,
    "Handbook of Exact String-Matching Algorithms," by Christian Charras and
    Thierry Lecroq.
*/

use common::run::{run, PatternData};
use std::cmp::max;
use std::env;
use std::process::exit;

// Define the alphabet size, part of the Boyer-Moore pre-processing. Here, we
// are just using ASCII characters, so 128 is fine.
const ASIZE: usize = 128;

/*
    Preprocessing step: calculate the bad-character shifts.
*/
fn calc_bad_char(pat: &[u8], m: usize) -> Vec<i32> {
    let mut bad_char: Vec<i32> = vec![m as i32; ASIZE];

    for i in 0..(m - 1) {
        bad_char[pat[i] as usize] = (m - i - 1) as i32;
    }

    bad_char
}

/*
    Preprocessing step: calculate suffixes for good-suffix shifts.
*/
fn calc_suffixes(pat: &[u8], m: usize) -> Vec<i32> {
    let mut suffix_list: Vec<i32> = vec![0; m];
    let mut f = 0;
    let mut g;
    let mut i;

    suffix_list[m - 1] = m as i32;

    g = m as i32 - 1;
    i = m as i32 - 2;
    while i >= 0 {
        if i > g && suffix_list[(i + m as i32 - 1 - f) as usize] < i - g {
            suffix_list[i as usize] =
                suffix_list[(i + m as i32 - 1 - f) as usize];
        } else {
            if i < g {
                g = i;
            }
            f = i;
            while g >= 0
                && pat[g as usize] == pat[(g + m as i32 - 1 - f) as usize]
            {
                g -= 1;
            }
            suffix_list[i as usize] = f - g;
        }

        i -= 1;
    }

    suffix_list
}

/*
  Preprocessing step: calculate the good-suffix shifts.
*/
fn calc_good_suffix(pat: &[u8], m: usize) -> Vec<i32> {
    let mut i: i32;
    let mut j: i32;
    let suffixes = calc_suffixes(pat, m);
    let mut good_suffix: Vec<i32> = vec![m as i32; m];

    j = 0;
    i = m as i32 - 1;
    while i >= -1 {
        if i == -1 || suffixes[i as usize] == i + 1 {
            while j < m as i32 - 1 - i {
                if good_suffix[j as usize] == m as i32 {
                    good_suffix[j as usize] = m as i32 - 1 - i;
                }

                j += 1;
            }
        }
        i -= 1;
    }
    for i in 0..=(m - 2) {
        good_suffix[m - 1 - suffixes[i as usize] as usize] = (m - 1 - i) as i32;
    }

    good_suffix
}

/*
    Initialize the pattern structure for Boyer-Moore that will be passed in to
    the calls to `boyer_moore`.
*/
fn init_boyer_moore(pat: &[u8]) -> Vec<PatternData> {
    let m = pat.len();
    let mut pattern_data: Vec<PatternData> = Vec::with_capacity(3);

    // Because the C code takes advantage of the presence of a null byte at the
    // end of strings, we have to force this in and re-convert the pattern to a
    // &[u8].
    let mut new_vec = pat.to_vec();
    new_vec.push(0);
    let new_pat = new_vec.as_slice();

    // Get the bad-character and good-suffix shift tables:
    let good_suffix: Vec<i32> = calc_good_suffix(new_pat, m);
    let bad_char: Vec<i32> = calc_bad_char(new_pat, m);

    pattern_data.push(PatternData::PatternU8Vec(new_pat.to_owned()));
    pattern_data.push(PatternData::PatternIntVec(good_suffix));
    pattern_data.push(PatternData::PatternIntVec(bad_char));

    pattern_data
}

/*
    Perform the Boyer-Moore algorithm on the given pattern of length m, against
    the sequence of length n.
*/
fn boyer_moore(pat_data: &[PatternData], sequence: &[u8]) -> i32 {
    let mut i: i32;
    let mut j: i32;
    // Track the number of times the pattern is found in the sequence.
    let mut matches: i32 = 0;

    // Unpack pat_data:
    let pattern = match &pat_data[0] {
        PatternData::PatternU8Vec(pat_as_vec) => pat_as_vec,
        _ => panic!("Incorrect value at pat_data slot 0"),
    };
    let good_suffix = match &pat_data[1] {
        PatternData::PatternIntVec(arr) => arr,
        _ => panic!("Incorrect value at pat_data slot 1"),
    };
    let bad_char = match &pat_data[2] {
        PatternData::PatternIntVec(arr) => arr,
        _ => panic!("Incorrect value at pat_data slot 2"),
    };

    // Sizes of pattern and sequence. Converted from usize to i32 to cut down
    // on the number of casts that have to be done. The casts don't really
    // contribute to the run-time of the code, but they affect the readability.
    let m = pattern.len() as i32 - 1; // Account for the sentinel character
    let n = sequence.len() as i32;

    // Perform the searching:
    j = 0;
    while j <= n - m {
        i = m - 1;
        while i >= 0 && pattern[i as usize] == sequence[(i + j) as usize] {
            i -= 1;
        }
        if i < 0 {
            matches += 1;
            j += good_suffix[0];
        } else {
            j += max(
                good_suffix[i as usize],
                bad_char[sequence[(i + j) as usize] as usize] - m + 1 + i,
            );
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
    exit(run(&init_boyer_moore, &boyer_moore, "boyer_moore", argv));
}
