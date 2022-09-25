/*
  Header file for the RAPL code, adapted from:
  https://github.com/greensoftwarelab/Energy-Languages
 */

#ifndef _RAPL_H
#define _RAPL_H

#define MSR_RAPL_POWER_UNIT 0x606

/*
 * Platform specific RAPL Domains.
 */

/* Package RAPL Domain */
#define MSR_PKG_RAPL_POWER_LIMIT 0x610
#define MSR_PKG_ENERGY_STATUS 0x611
#define MSR_PKG_PERF_STATUS 0x613
#define MSR_PKG_POWER_INFO 0x614

/* PP0 RAPL Domain */
#define MSR_PP0_POWER_LIMIT 0x638
#define MSR_PP0_ENERGY_STATUS 0x639
#define MSR_PP0_POLICY 0x63A
#define MSR_PP0_PERF_STATUS 0x63B

/* RAPL UNIT BITMASK */
#define POWER_UNIT_OFFSET 0
#define POWER_UNIT_MASK 0x0F

#define ENERGY_UNIT_OFFSET 0x08
#define ENERGY_UNIT_MASK 0x1F00

#define TIME_UNIT_OFFSET 0x10
#define TIME_UNIT_MASK 0xF000

int open_msr(int core);
long long read_msr(int fd, int which);
int detect_cpu(void);
int rapl_init(int core, int show_info);
void show_power_info(int core);
void show_power_limit(int core);
void rapl_before(int);
void rapl_after(FILE *, int);

#endif // !_RAPL_H
