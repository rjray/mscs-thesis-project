/*
  Header file for the setup code.
*/

#ifndef _SETUP_H
#define _SETUP_H

extern int read_sequences(const char *fname, char ***data);
extern int read_patterns(const char *fname, char ***data);
extern int read_answers(const char *fname, int ***data);

#endif // !_SETUP_H
