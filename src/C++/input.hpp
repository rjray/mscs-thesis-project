/*
  Header file for the code that manages input of experiment data.
*/

#ifndef _INPUT_HPP
#define _INPUT_HPP

#include <string>
#include <vector>

extern std::vector<std::string> read_sequences(std::string fname);
extern std::vector<std::string> read_patterns(std::string fname);
extern std::vector<std::vector<int>> read_answers(std::string fname, int *k);

#endif // !_INPUT_HPP
