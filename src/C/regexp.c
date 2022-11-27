/*
  C implementation of the (tentatively-titled) DFA-Gap algorithm for
  approximate string matching, regular expression variant.
*/

// This must be set before pcre2.h is included.
#define PCRE2_CODE_UNIT_WIDTH 8

#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "run.h"

/*
  Initialize the pattern given. Return a 1-element array of the regexp from
  processing the pattern. The original pattern will not be needed for matching.
*/
void **init_regexp(unsigned char *pattern, int k) {
  // Allocate one pointer-slot more than is needed, as the final NULL will be
  // the signal to the loop that is freeing memory.
  void **return_val = (void **)calloc(2, sizeof(void *));

  int m = strlen((const char *)pattern);
  int errornumber;
  PCRE2_SIZE erroroffset;
  // The estimated length of the RE that will be built is (m*10 + 7), where `m`
  // is the length of the pattern. One more is added for the NULL byte at the
  // end.
  unsigned char *re_buf = (unsigned char *)calloc(m * 10 + 8, sizeof(char));
  int bufptr = 0;

  strcpy((char *)re_buf, "(?=(");
  bufptr += 4;
  re_buf[bufptr++] = pattern[0];
  for (int i = 1; i < m; i++) {
    bufptr += sprintf((char *)(re_buf + bufptr), "[^%c]{0,%d}%c", pattern[i], k,
                      pattern[i]);
  }
  re_buf[bufptr++] = ')';
  re_buf[bufptr++] = ')';

  pcre2_code *re = pcre2_compile((PCRE2_SPTR)re_buf, PCRE2_ZERO_TERMINATED, 0,
                                 &errornumber, &erroroffset, NULL);
  if (re == NULL) {
    PCRE2_UCHAR buffer[256];
    pcre2_get_error_message(errornumber, buffer, sizeof(buffer));
    printf("PCRE2 compilation failed at offset %d: %s\n", (int)erroroffset,
           buffer);
    exit(1);
  }

  // There is only the one value that is carried over to the `regexp` function.
  return_val[0] = (void *)re;
  free(re_buf);

  return return_val;
}

/*
  Perform the DFA-Gap-Regexp algorithm on the given (processed) pattern against
  the given sequence.
*/
int regexp(void **pat_data, unsigned char *sequence) {
  int matches = 0;
  PCRE2_SIZE *ovector;
  PCRE2_SIZE s;

  // Unpack pat_data:
  pcre2_code *re = (pcre2_code *)pat_data[0];
  pcre2_match_data *match_data = pcre2_match_data_create_from_pattern(re, NULL);

  s = 0;
  while (0 <= pcre2_match(re, (PCRE2_SPTR)sequence, PCRE2_ZERO_TERMINATED, s, 0,
                          match_data, NULL)) {
    matches++;
    ovector = pcre2_get_ovector_pointer(match_data);
    s = ovector[0] + 1;
  }

  pcre2_match_data_free(match_data);

  return matches;
}

/*
  All that is done here is call the run_approx() function with a pointer to the
  algorithm initializer, a pointer to the algorithm implementation, the label
  for the algorithm, and the argc/argv values.
*/
int main(int argc, char *argv[]) {
  int return_code = run_approx(&init_regexp, &regexp, "regexp", argc, argv);

  return return_code;
}
