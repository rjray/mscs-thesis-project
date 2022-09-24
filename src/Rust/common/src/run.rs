/*
    This is the "runner" module. It provides the function that will handle
    running an experiment.
*/

use crate::setup::*;
use std::time::Instant;

// A type alias for the signature of the single-pattern matching algorithms.
pub type Runnable = dyn Fn(&String, usize, &String, usize) -> u32;

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
pub fn run(code: &Runnable, name: &str, argv: &Vec<String>) -> i32 {
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

    for (sequence, sequence_str) in sequences_data.iter().enumerate() {
        let seq_len = sequence_str.len();

        for pattern in 0..patterns_data.len() {
            let pattern_str = &patterns_data[pattern];
            let pat_len = pattern_str.len();
            let matches = code(pattern_str, pat_len, sequence_str, seq_len);

            if let Some(ref answers) = answers_data {
                if matches != answers[pattern][sequence] {
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
    println!("---\nlanguage: rust\nalgorithm: {}", &name);
    println!("runtime: {:.8}", elapsed.as_secs_f64());

    return_code
}
