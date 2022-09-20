/*
    This is the "runner" module. It provides the function that will handle
    running an experiment.
*/

use crate::setup::*;
use std::io::{stderr, Write};
use std::time::Instant;

const LANG: &str = "rust";

pub type Runnable = dyn Fn(&String, usize, &String, usize) -> u32;

pub fn run(code: &Runnable, name: &String, argv: &Vec<String>) -> i32 {
    let argc = argv.len();
    if argc < 3 || argc > 4 {
        match writeln!(
            stderr(),
            "Usage: {} <sequences> <patterns> [ <answers> ]",
            &argv[0]
        ) {
            Err(err) => {
                panic!("Failed to write to stderr: {:?}", err);
            }
            Ok(_) => 0,
        };

        return -1;
    }

    let sequences_file: String = String::from(&argv[1]);
    let patterns_file: String = String::from(&argv[2]);
    let answers_file: Option<String> = if argc == 4 {
        Some(String::from(&argv[3]))
    } else {
        None
    };

    let sequences_data: Vec<String> = read_sequences(&sequences_file);
    let patterns_data: Vec<String> = read_patterns(&patterns_file);
    let answers_data: Option<Vec<Vec<u32>>> = if let Some(file) = answers_file {
        Some(read_answers(&file))
    } else {
        None
    };

    if let Some(ref answers) = answers_data {
        if answers.len() != patterns_data.len() {
            match writeln!(
                stderr(),
                "Count mismatch between patterns file and answers file"
            ) {
                Err(err) => {
                    panic!("Failed to write to stderr: {:?}", err);
                }
                Ok(_) => 0,
            };

            return -1;
        }
    }

    // Run the given code. For each sequence, try each pattern against it. The
    // `code` function pointer will return the number of matches found, which
    // will be compared to the table of answers for that pattern. Report any
    // mismatches.
    let start_time = Instant::now();
    let mut return_code: i32 = 0;

    for sequence in 0..sequences_data.len() {
        let sequence_str = &sequences_data[sequence];
        let seq_len = sequence_str.len();

        for pattern in 0..patterns_data.len() {
            let pattern_str = &patterns_data[pattern];
            let pat_len = pattern_str.len();
            let matches = code(&pattern_str, pat_len, &sequence_str, seq_len);

            if let Some(ref answers) = answers_data {
                if matches != answers[pattern][sequence] {
                    match writeln!(
                        stderr(),
                        "Pattern {} mismatch against sequence {} ({} != {})",
                        pattern + 1,
                        sequence + 1,
                        matches,
                        answers[pattern][sequence]
                    ) {
                        Err(err) => {
                            panic!("Failed to write to stderr: {:?}", err);
                        }
                        Ok(_) => 0,
                    };

                    return_code += 1;
                }
            }
        }
    }
    // Note the end time before doing anything else.
    let elapsed = start_time.elapsed();
    print!("---\nlanguage: {}\nalgorithm: {}\n", &LANG, &name);
    print!("runtime: {:.6?}\n", elapsed);

    return_code
}
