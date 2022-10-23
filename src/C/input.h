/*
  Header file for the code that manages input of experiment data.
*/

#ifndef _INPUT_H
#define _INPUT_H

extern int read_sequences(const char *fname, char ***data);
extern int read_patterns(const char *fname, char ***data);
extern int read_answers(const char *fname, int ***data, int *k);

#endif // !_INPUT_H
