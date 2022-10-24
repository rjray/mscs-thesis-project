/*
  "Setup" code used by all the C++ programs to read the various data files and
  return viable data structures.
*/

#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "input.hpp"

/*
  Read the numbers from the first line of the file pointed to by `input`. Store
  them in a vector of int and return it.
*/
std::vector<int> read_header(std::ifstream &input) {
  std::string line;
  std::vector<int> ints;

  std::getline(input, line);
  std::istringstream ss(std::move(line));

  for (std::string value; std::getline(ss, value, ' ');) {
    ints.push_back(std::stoi(value));
  }

  return ints;
}

/*
  Read the sequence data from the given filename. Return it as a vector of
  std::string.

  The first line indicates the number of data-lines and their maximum length:

    100000 1040

  Here, the max-length is not used. Simply compare the number of lines of data
  read to the first integer from the first line.
*/
std::vector<std::string> read_sequences(std::string fname) {
  std::ifstream input{fname};
  if (!input.is_open()) {
    std::ostringstream error;
    error << "Error opening " << fname << " for reading";
    throw std::runtime_error{error.str()};
  }

  std::vector<int> ints = read_header(input);
  unsigned int num_lines = ints[0];

  std::vector<std::string> data;
  for (std::string line; std::getline(input, line);) {
    data.push_back(std::move(line));
  }

  if (data.size() != num_lines) {
    std::ostringstream error;
    error << fname << ": wrong number of lines read";
    throw std::runtime_error{error.str()};
  }

  return data;
}

/*
  Read the pattern data from the given filename. For now, the pattern data is
  the same format as the sequence data so just fall through to read_sequences.
*/
std::vector<std::string> read_patterns(std::string fname) {
  return read_sequences(fname);
}

/*
  Read the answers data from the given filename. This data is different from
  the DNA-based data. The first line tells how many data-lines there are (one
  for each pattern read) and how many comma-separated numbers there are on
  each data-line (one for each sequence read). As with the others, the return
  value is a vector of the data read, here std::vector<std::vector<int>>.
*/
std::vector<std::vector<int>> read_answers(std::string fname, int *k) {
  std::ifstream input{fname};
  if (!input.is_open()) {
    std::ostringstream error;
    error << "Error opening " << fname << " for reading";
    throw std::runtime_error{error.str()};
  }

  std::vector<int> ints = read_header(input);
  unsigned int num_lines = ints[0];
  unsigned int num_ints = ints[1];
  if (k != nullptr)
    *k = ints[2];

  // Allocate the vector-of-vectors in `table`:
  std::vector<std::vector<int>> table;

  for (std::string line; std::getline(input, line);) {
    std::istringstream ss(std::move(line));
    std::vector<int> row;
    row.reserve(num_ints);

    for (std::string value; std::getline(ss, value, ',');) {
      row.push_back(std::stoi(value));
    }
    if (row.size() != num_ints) {
      std::ostringstream error;
      error << fname << ": wrong number of numbers read (" << row.size() << ")";
      throw std::runtime_error{error.str()};
    }

    table.push_back(row);
  }

  if (table.size() != num_lines) {
    std::ostringstream error;
    error << fname << ": wrong number of lines read";
    throw std::runtime_error{error.str()};
  }

  return table;
}
