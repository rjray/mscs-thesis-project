use common::run::run;
use std::cmp::max;
use std::env;

const ASIZE: usize = 128;

fn calc_bad_char(pat: &[u8], m: usize) -> Vec<i32> {
    let mut bad_char: Vec<i32> = vec![m as i32; ASIZE];

    for i in 0..(m - 1) {
        bad_char[pat[i] as usize] = (m - i - 1) as i32;
    }

    bad_char
}

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

fn calc_good_suffix(pat: &[u8], m: usize) -> Vec<i32> {
    let mut i: i32;
    let mut j: i32;
    let suffixes = calc_suffixes(&pat, m);
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

fn boyer_moore(pattern: &String, m: usize, sequence: &String, n: usize) -> u32 {
    let mut pattern_p = String::from(pattern);
    pattern_p.push('\0');
    let pattern = pattern_p.as_bytes();
    let sequence = sequence.as_bytes();
    let mut i: i32;
    let mut j: i32;
    let m: i32 = m as i32;
    let n: i32 = n as i32;
    let mut matches: u32 = 0;

    let good_suffix: Vec<i32> = calc_good_suffix(&pattern, m as usize);
    let bad_char: Vec<i32> = calc_bad_char(&pattern, m as usize);

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

fn main() {
    let argv: Vec<String> = env::args().collect();
    run(&boyer_moore, "boyer_moore", &argv);
}
