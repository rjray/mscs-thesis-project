/*
    Implementation of the Boyer-Moore algorithm.

    This is based heavily on the C code given in chapter 14 of the book,
    "Handbook of Exact String-Matching Algorithms," by Christian Charras and
    Thierry Lecroq.
*/

use common::run::run;
use std::cmp::{max, Ordering};
use std::env;

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
    let mut good_suffix: Vec<i32> = vec![m as i32; m + 1];

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
    Perform the Boyer-Moore algorithm on the given pattern of length m, against
    the sequence of length n.
*/
fn boyer_moore(pattern: &String, m: usize, sequence: &String, n: usize) -> i32 {
    // Because the C code takes advantage of the presence of a null byte at the
    // end of strings, we have to force this in before converting the pattern
    // to a [u8].
    let mut pattern_p = String::from(pattern);
    pattern_p.push('\0');
    // For indexing that would be comparable to C's, convert the String objects
    // to arrays of bytes. This works because the UTF-8 data won't have any
    // wide characters.
    let pattern = pattern_p.as_bytes();
    let sequence = sequence.as_bytes();
    let mut i: i32;
    let mut j: i32;
    // Convert m and n from usize to i32 to cut down on the number of casts
    // that have to be done. The casts don't really contribute to the run-time
    // of the code, but they affect the readability.
    let m: i32 = m as i32;
    let n: i32 = n as i32;
    // Track the number of times the pattern is found in the sequence.
    let mut matches: i32 = 0;

    // Get the bad-character and good-suffix shift tables:
    let good_suffix: Vec<i32> = calc_good_suffix(pattern, m as usize);
    let bad_char: Vec<i32> = calc_bad_char(pattern, m as usize);

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
    let code: i32 = run(&boyer_moore, "boyer_moore", &argv);

    match code.cmp(&0) {
        Ordering::Less => eprintln!("Program encountered internal error."),
        Ordering::Greater => {
            eprintln!("Program encountered {} mismatches.", code);
        }
        Ordering::Equal => (),
    };
}
