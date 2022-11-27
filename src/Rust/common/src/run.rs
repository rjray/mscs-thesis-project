/*
    This is the "runner" module. It provides the functions that will handle
    running the experiments. There are three public-facing functions defined
    here:

        * run() - Runs a single-pattern, exact-matching algorithm
        * run_multi() - Runs a multi-pattern, exact-matching algorithm
        * run_approx() - Runs a single-pattern, approximate-matching algorithm

    Each of the three functions also has an associated enum with it, that is
    used for the packing/unpacking of pattern data between the algorithms'
    init functions and primary functions.
*/

use crate::input::*;
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
type Algorithm = dyn Fn(&[PatternData], &[u8]) -> i32;
// A type alias for the signature of the single-pattern initialization
// functions.
type Initializer = dyn Fn(&[u8]) -> Vec<PatternData>;

/*
   This is the "runner" routine. It takes a pointer to the code that
   initializes the given algorithm, a pointer to the code that executes the
   algorithm, the text name of the algorithm for the output block, and the
   vector of command-line arguments that were passed to the program.

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

/*
    Handling multi-pattern matching algorithms.
*/

// An enum to type the various sorts of values that can be returned from the
// pre-processing of a set of patterns.
pub enum MultiPatternData<T> {
    PatternCount(usize),
    PatternIntVecVec(Vec<Vec<i32>>),
    PatternUsizeVec(Vec<usize>),
    PatternTypeVec(Vec<T>),
}

// A type alias for the signature of the multi-pattern matching algorithms.
type MPAlgorithm<T> = dyn Fn(&[MultiPatternData<T>], &[u8]) -> Vec<u32>;
// A type alias for the signature of the single-pattern initialization
// functions.
type MPInitializer<T> = dyn Fn(&[&[u8]]) -> Vec<MultiPatternData<T>>;

/*
   This is the "runner" routine for multi-pattern algorithms. The signature is
   identical to `run`, above, except for the generic type specification that is
   passed through to the MPInitializer and MPAlgorithm types.
*/
pub fn run_multi<T>(
    init: &MPInitializer<T>,
    code: &MPAlgorithm<T>,
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

// An enum to type the various sorts of values that can be returned from the
// pre-processing of an approximate matching pattern.
pub enum ApproxPatternData {
    PatternIntVecVec(Vec<Vec<i32>>),
    PatternUsize(usize),
}

// A type alias for the signature of the approximate matching algorithms.
type AMAlgorithm = dyn Fn(&[ApproxPatternData], &[u8]) -> i32;
// A type alias for the signature of the approximate matching initialization
// functions.
type AMInitializer = dyn Fn(&[u8], u32) -> Vec<ApproxPatternData>;

/*
   This is the "runner" routine for approximate matching algorithms. The
   signature is identical to `run`, above, except for the enum type used for
   the pattern data.
*/
pub fn run_approx(
    init: &AMInitializer,
    code: &AMAlgorithm,
    name: &str,
    argv: Vec<String>,
) -> i32 {
    let argc = argv.len();
    if !(4..=5).contains(&argc) {
        eprintln!(
            "Usage: {} <k> <sequences> <patterns> [ <answers> ]",
            &argv[0]
        );

        return -1;
    }

    // First argument is the value of k:
    let k: u32 = argv[1].parse().unwrap();
    // Read the data files using the routines from common::setup. The answers
    // data uses Option<> since it does not have to be provided.
    let sequences_data: Vec<String> = read_sequences(&argv[2]);
    let patterns_data: Vec<String> = read_patterns(&argv[3]);
    let answers_data: Option<Vec<Vec<u32>>> = if argc == 5 {
        let answers_file = argv[4].replace("%d", &k.to_string());
        Some(read_answers(&answers_file))
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
        let pat_data = init(pat_bytes, k);

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
    println!("language: rust\nalgorithm: {}({})", &name, k);
    println!("runtime: {:.8}", elapsed.as_secs_f64());

    return_code
}
