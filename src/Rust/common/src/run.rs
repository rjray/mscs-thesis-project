/*
    This is the "runner" module. It provides the function that will handle
    running an experiment.
*/

use crate::setup::*;
use std::time::Instant;

// `WordType` is used by shift-or. It's defined here so it can be used in the
// enum, below.
pub type WordType = u64;

// An enum to type the various sorts of values that can be returned from the
// pre-processing of a pattern.
pub enum PatternData {
    PatternU8Vec(Vec<u8>),
    PatternIntVec(Vec<i32>),
    PatternWord(WordType),
    PatternWordVec(Vec<WordType>),
}

// A type alias for the signature of the single-pattern matching algorithms.
pub type Algorithm = dyn Fn(&[PatternData], &[u8]) -> i32;
// A type alias for the signature of the single-pattern initialization
// functions.
pub type Initializer = dyn Fn(&[u8]) -> Vec<PatternData>;

/*
   This is the "runner" routine. It takes a pointer to the code that implements
   the given algorithm, the text name of the algorithm for the output block,
   and the vector of command-line arguments that were passed to the program.

   After reading the data files given on the command-line, the code starts the
   clock on execution and iterates over the patterns and sequences. Once all
   have been run, the total run-time for the computation phase is calculated
   and a block of output is written that identifies the language, the
   algorithm and the run-time.
*/
pub fn run(
    init: &Initializer,
    code: &Algorithm,
    name: &str,
    argv: Vec<String>,
) -> i32 {
    let argc = argv.len();
    if !(3..=4).contains(&argc) {
        eprintln!("Usage: {} <sequences> <patterns> [ <answers> ]", &argv[0]);

        return -1;
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
            eprintln!("Count mismatch between patterns file and answers file");

            return -1;
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

    for (pattern, pat_bytes) in patterns.iter().enumerate() {
        let pat_data = init(pat_bytes);

        for (sequence, seq_bytes) in sequences.iter().enumerate() {
            let matches = code(&pat_data, seq_bytes);
            // If there was an error in the actual algorithm, `matches` will be
            // <0.
            if matches < 0 {
                return matches;
            }

            if let Some(ref answers) = answers_data {
                if matches as u32 != answers[pattern][sequence] {
                    eprintln!(
                        "Pattern {} mismatch against sequence {} ({} != {})",
                        pattern + 1,
                        sequence + 1,
                        matches,
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
