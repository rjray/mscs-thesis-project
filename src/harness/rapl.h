/*
  Header file for the RAPL code, adapted from:
  https://github.com/greensoftwarelab/Energy-Languages
 */

#ifndef _RAPL_H
#define _RAPL_H

int open_msr(int core);
long long read_msr(int fd, int which);
int detect_cpu(void);
int rapl_init(int core, int show_info);
void show_power_info(int core);
void show_power_limit(int core);
void rapl_before(int);
void rapl_after(FILE *, int);

#endif // !_RAPL_H
