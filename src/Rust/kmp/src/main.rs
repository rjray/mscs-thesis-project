use common::setup::*;
use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();

    let sequences: Vec<String> = read_sequences(&args[1]);
    println!("{} sequences read from {}", sequences.len(), &args[1]);

    let patterns: Vec<String> = read_patterns(&args[2]);
    println!("{} patterns read from {}", patterns.len(), &args[2]);

    if args.len() > 3 {
        let answers: Vec<Vec<u32>> = read_answers(&args[3]);
        println!("{} rows of answers read from {}", answers.len(), &args[3]);

        if patterns.len() != answers.len() {
            println!("Count mismatch between patterns and answers");
        }
        if sequences.len() != answers[0].len() {
            println!("Count mismatch between answers and sequences");
        }
    }
}
