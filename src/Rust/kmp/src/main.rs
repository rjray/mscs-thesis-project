/*
    Implementation of the Knuth-Morris-Pratt algorithm.

    This is based heavily on the C code given in chapter 7 of the book,
    "Handbook of Exact String-Matching Algorithms," by Christian Charras and
    Thierry Lecroq.
*/

use common::run::run;
use std::env;
use std::io::{self, stderr, Write};

/*
   Initialize the jump-table that KMP uses. Unlike the C code, which takes a
   pre-allocated pointer as an argument, this code returns a vector structure
   for the table. Rust's ownership mechanism will take care of freeing this
   when it is no longer needed.
*/
fn init_kmp(pat: &[u8], m: usize) -> Vec<i32> {
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
    Perform the KMP algorithm on the given pattern of length m, against the
    sequence of length n.
*/
fn kmp(
    pattern: &String,
    m: usize,
    sequence: &String,
    n: usize,
) -> io::Result<u32> {
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
    let mut i: i32 = 0;
    let mut j: usize = 0;
    // Track the number of times the pattern is found in the sequence.
    let mut matches = 0;
    // Obtain the jump-table.
    let next_table = init_kmp(&pattern, m);

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

    Ok(matches)
}

/*
    All that is done here is call the run() function with a pointer to the
    algorithm implementation, the label for the algorithm, and the argv values.
*/
fn main() -> io::Result<()> {
    let argv: Vec<String> = env::args().collect();
    let code: i32 = run(&kmp, "kmp", &argv).unwrap();

    if code < 0 {
        writeln!(stderr(), "Program encountered internal error.")?;
    } else if code > 0 {
        writeln!(stderr(), "Program encountered {} mismatches.", code)?;
    }

    return Ok(());
}
