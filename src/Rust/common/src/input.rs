/*
    This is the input code used by all the Rust programs to read the various
    data files and return the information in viable data structures.
*/

use std::fs::File;
use std::io::{self, BufRead, BufReader};
use std::path::Path;

/*
    Read one line from the BufRead-capable value `rdr`, and expect it to parse
    into (at least) two integer values. Return a vector of the integers read.
*/
fn read_header<R: io::BufRead>(rdr: &mut R, path: &String) -> Vec<u32> {
    let mut buffer = String::new();

    // Read one line from rdr and ensure that we got it. Panic on error.
    match rdr.read_line(&mut buffer) {
        Ok(_) => (),
        Err(err) => panic!("{}: Error reading first line: {:?}", &path, err),
    };
    // Split the line on ' ' and parse the tokens as u32 values. Discard errors.
    let ints: Vec<u32> = buffer
        .trim_end()
        .split(' ')
        .filter_map(|s| s.parse::<u32>().ok())
        .collect();

    ints
}

/*
    Read the sequence data from the given filename. Return it as a vector of
    String values.

    The first line indicates the number of data-lines. It also has a second
    value for the maximum line-length, which is not needed in this
    implementation.
*/
pub fn read_sequences(filename: &String) -> Vec<String> {
    let path = Path::new(&filename);
    // Get a filehandle on the given path, panicking on error.
    let file = match File::open(&path) {
        Ok(file) => file,
        Err(err) => {
            panic!("{}: File open error: {:?}", &filename, err)
        }
    };
    let mut rdr = BufReader::new(file);

    // This will consume the first line of the file, and get the number of
    // data-lines that are expected.
    let ints = read_header(&mut rdr, filename);
    let sequences_count: u32 = ints[0];

    // Read the remaining lines, converting the Result<> types to String values
    // and discarding any errors.
    let sequences: Vec<String> = rdr.lines().filter_map(|l| l.ok()).collect();

    // Verify that the correct number of lines were read.
    if sequences.len() != sequences_count as usize {
        panic!("{}: wrong number of lines read successfully", &filename)
    }

    sequences
}

/*
    Read the pattern data from the given filename. For now, the pattern data is
    the same format as the sequence data so just fall through to read_sequences.
*/
pub fn read_patterns(filename: &String) -> Vec<String> {
    read_sequences(filename)
}

/*
    Read the answers data from the given filename. This data is different from
    the DNA-based data. The first line tells how many data-lines there are (one
    for each pattern read) and how many comma-separated numbers there are on
    each data-line (one for each sequence read).
*/
pub fn read_answers(filename: &String) -> Vec<Vec<u32>> {
    // Get a filehandle on the given filename, panicking on error.
    let file = match File::open(&filename) {
        Ok(file) => file,
        Err(err) => {
            panic!("{}: File open error: {:?}", &filename, err)
        }
    };
    let mut rdr = BufReader::new(file);

    // This will consume the first line of the file, and get the number of
    // data-lines that are expected.
    let ints = read_header(&mut rdr, filename);
    // Here we use both values from the line, the second tells us how many ints
    // should be on each line that gets read.
    let lines_count: u32 = ints[0];
    let ans_count: u32 = ints[1];

    // Collect the remaining lines as a vector of String, discarding errors.
    let strings: Vec<String> = rdr.lines().filter_map(|l| l.ok()).collect();
    // Confirm the correct number of lines gathered.
    if strings.len() != lines_count as usize {
        panic!("{}: wrong number of lines read successfully", &filename);
    }

    let mut line_no = 1;
    let mut answers: Vec<Vec<u32>> = vec![];
    // Iterate over the lines read from the file. Each line is split on ',' and
    // the resulting tokens parsed as u32 ints. Gather the parsed ints into the
    // `answers` vector.
    strings.into_iter().for_each(|s| {
        line_no += 1;
        let mut errors = vec![];
        let line: Vec<u32> = s
            .split(',')
            .map(|i| i.parse::<u32>())
            .filter_map(|r| r.map_err(|e| errors.push(e)).ok())
            .collect();

        if !errors.is_empty() {
            panic!(
                "{}: Parse error on line {}: {:?}",
                &filename, line_no, errors[0]
            );
        }
        if line.len() != ans_count as usize {
            panic!(
                "{}: Error on line {}: wrong number of answer values",
                &filename, line_no
            );
        }

        answers.push(line);
    });

    answers
}
