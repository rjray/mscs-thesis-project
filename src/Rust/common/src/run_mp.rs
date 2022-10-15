/*
    This is the "runner" module, altered for use with multi-pattern matching.
    It provides the function that will handle running an experiment.
*/

use crate::setup::*;
use std::time::Instant;

// An enum to type the various sorts of values that can be returned from the
// pre-processing of a pattern.
pub enum PatternData<T> {
    PatternCount(usize),
    PatternIntVecVec(Vec<Vec<i32>>),
    PatternUsizeVec(Vec<usize>),
    PatternTypeVec(Vec<T>),
}

// A type alias for the signature of the multi-pattern matching algorithms.
pub type Algorithm<T> = dyn Fn(&[PatternData<T>], &[u8]) -> Vec<u32>;
// A type alias for the signature of the single-pattern initialization
// functions.
pub type Initializer<T> = dyn Fn(&[&[u8]]) -> Vec<PatternData<T>>;

/*
   This is the "runner" routine. It takes a pointer to the code that
   initializes the given algorithm, a pointer to the code that executes the
   algorithm, the text name of the algorithm for the output block, and the
   vector of command-line arguments that were passed to the program.

   After reading the data files given on the command-line, the code starts the
   clock on execution and runs the init code on the set of patterns. It then
   iterates over the sequences with the processed data from the initialization.
   Once all have been run, the total run-time for the computation phase is
   calculated and a block of output is written that identifies the language,
   the algorithm and the run-time.
*/
pub fn run_mp<T>(
    init: &Initializer<T>,
    code: &Algorithm<T>,
    name: &str,
    argv: Vec<String>,
) -> i32 {
    let argc = argv.len();
    if !(3..=4).contains(&argc) {
        panic!("Usage: {} <sequences> <patterns> [ <answers> ]", &argv[0]);
    }

    // Read the data files using the routines from common::setup. The answers
    // data uses Option<> since it does not have to be provided.
    let sequences_data: Vec<String> = read_sequences(&argv[1]);
    let patterns_data: Vec<String> = read_patterns(&argv[2]);
    let answers_data: Option<Vec<Vec<u32>>> = if argc == 4 {
        Some(read_answers(&argv[3]))
    } else {
        None
    };

    // If answers were provided, check that the number of lines matches the
    // number of patterns.
    if let Some(ref answers) = answers_data {
        if answers.len() != patterns_data.len() {
            panic!("Count mismatch between patterns file and answers file");
        }
    }

    // Run the given code. For each sequence, try each pattern against it. The
    // `code` function pointer will return the number of matches found, which
    // will be compared to the table of answers for that pattern. Report any
    // mismatches.
    let start_time = Instant::now();
    let mut return_code: i32 = 0;

    // Convert the patterns and sequences to `u8` (byte) arrays. Do this here
    // so that it isn't repeated in the for-loops.
    let patterns: Vec<&[u8]> =
        patterns_data.iter().map(|p| p.as_bytes()).collect();
    let sequences: Vec<&[u8]> =
        sequences_data.iter().map(|s| s.as_bytes()).collect();

    // Initialize the multi-patterns structure.
    let pat_data = init(&patterns);

    for (sequence, sequence_str) in sequences.iter().enumerate() {
        // Here, we don't iterate over the patterns. We just call the matching
        // function and pass it the pattern-data structure set up in the init
        // call above.
        let matches = code(&pat_data, sequence_str);

        if let Some(ref answers) = answers_data {
            for pattern in 0..patterns_data.len() {
                if matches[pattern] != answers[pattern][sequence] {
                    eprintln!(
                        "Pattern {} mismatch against sequence {} ({} != {})",
                        pattern + 1,
                        sequence + 1,
                        matches[pattern],
                        answers[pattern][sequence]
                    );

                    return_code += 1;
                }
            }
        }
    }

    // Note the end time before doing anything else.
    let elapsed = start_time.elapsed();
    println!("language: rust\nalgorithm: {}", &name);
    println!("runtime: {:.8}", elapsed.as_secs_f64());

    return_code
}
