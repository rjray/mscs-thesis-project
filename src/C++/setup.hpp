/*
  Header file for the setup code.
*/

#ifndef _SETUP_HPP
#define _SETUP_HPP

#include <string>
#include <vector>

extern std::vector<std::string> read_sequences(std::string fname);
extern std::vector<std::string> read_patterns(std::string fname);
extern std::vector<std::vector<int>> read_answers(std::string fname);

#endif // !_SETUP_HPP
