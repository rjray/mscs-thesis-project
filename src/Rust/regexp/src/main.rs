/*
    Rust implementation of the DFA-Gap algorithm for approximate string
    matching, using regular expressions.
*/

use common::run::{run_approx, ApproxPatternData};
use std::cell::RefCell;
use std::env;
use std::process::exit;
use std::str;

use pcre2::bytes::Regex;

// This declares a global value into which we can store the compiled regular
// expression. This is because adding a reference to pcre2::bytes::Regex to
// the `ApproxPatternData` enum would have required every one of the
// experiments to be compiled against the PCRE2 library.
thread_local!(
    static RE: RefCell<Regex> = RefCell::new(Regex::new("").unwrap())
);

/*
    Initialize the pattern as a regular expression and store it into the global
    set up above in the `thread_local` macro.
*/
fn init_regexp(pattern: &[u8], k: u32) -> Vec<ApproxPatternData> {
    let m = pattern.len();
    // Note that this algorithm doesn't actually use the `pattern_data` value.
    let pattern_data: Vec<ApproxPatternData> = Vec::with_capacity(1);
    let pat_str: &str = str::from_utf8(&pattern).unwrap();
    let pat_chars: Vec<char> = pat_str.chars().collect();
    // Start the `built_re` vector with the first character of pat:
    let mut built_re: String = pat_chars[0].to_string();

    for i in 1..m {
        let ch = pat_chars[i];

        built_re = format!("{}[^{}]{{0,{}}}{}", built_re, ch, k, ch);
    }
    built_re = format!("(?=({}))", built_re);

    // Because adding the Regex type to the ApproxPattenData enum would require
    // the all the tools to link with the regex crate, here we're using a
    // "trick" global approach.
    RE.with(|val| {
        *val.borrow_mut() = Regex::new(&built_re).unwrap();
    });

    pattern_data
}

/*
    Perform the regular expression variant matching on the given sequence.
*/
fn regexp(_pat_data: &[ApproxPatternData], sequence: &[u8]) -> i32 {
    let mut matches: usize = 0;

    // Pull the pre-processed regex from the RE static global and apply it to
    // `sequence`.
    RE.with(|val| {
        matches = val.borrow().captures_iter(sequence).count();
    });

    matches as i32
}

/*
    All that is done here is call the run_approx() function with the values.
*/
fn main() {
    let argv: Vec<String> = env::args().collect();
    exit(run_approx(&init_regexp, &regexp, "regexp", argv));
}
