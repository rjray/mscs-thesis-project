use common::run::run;
use std::env;

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

fn kmp(pattern: &String, m: usize, sequence: &String, n: usize) -> u32 {
    let mut pattern_p = String::from(pattern);
    pattern_p.push('\0');
    let pattern = pattern_p.as_bytes();
    let sequence = sequence.as_bytes();
    let mut i: i32 = 0;
    let mut j: usize = 0;
    let mut matches = 0;
    let next_table = init_kmp(&pattern, m);

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

fn main() {
    let argv: Vec<String> = env::args().collect();
    run(&kmp, "kmp", &argv);
}
