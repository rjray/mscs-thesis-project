/*
  Code for the RAPL interface, adapted from:
  https://github.com/greensoftwarelab/Energy-Languages

  That code itself was adapted from:
  https://github.com/deater/uarch-configure/blob/master/rapl-read/rapl-read.c

  NOTE: Though I have tried to keep as much of the processor-agnostic nature of
  this as I can, I've only run it on Kaby Lake family CPUs (a Kaby Lake and a
  Kaby Lake Mobile). It might not work on earlier chips. I have, however, taken
  out all of the AMD chip references.
 */

#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "rapl.h"

/*
  All the ENERGY_STATUS registers are only significant to the first 32 bits
  (31:0). Use this to mask it.
 */
#define ENERGY_MASK (long long)0x00000000ffffffff
#define ENERGY_MAX (long long)0x0000000100000000

#define MSR_RAPL_POWER_UNIT 0x606

/*
 * Platform specific RAPL Domains.
 */

/* Package RAPL Domain */
#define MSR_PKG_RAPL_POWER_LIMIT 0x610
#define MSR_PKG_ENERGY_STATUS 0x611
#define MSR_PKG_POWER_INFO 0x614

/* PP0 RAPL Domain */
#define MSR_PP0_ENERGY_STATUS 0x639

/* PP1 RAPL Domain, may reflect to uncore devices */
#define MSR_PP1_ENERGY_STATUS 0x641

/* DRAM RAPL Domain */
#define MSR_DRAM_ENERGY_STATUS 0x619

/* PSYS RAPL Domain */
#define MSR_PLATFORM_ENERGY_STATUS 0x64d

int cpu_model;
int core = 0;

int pp0_avail, pp1_avail, dram_avail, psys_avail, different_units;
long long package_before, package_after;
long long pp0_before, pp0_after;
/* Commenting-out, as these are always zeros on my systems. */
// long long pp1_before, pp1_after;
long long dram_before, dram_after;
/* Commenting-out, as these are not used in my experiments after all. */
// long long psys_before, psys_after;

double power_units, cpu_energy_units, time_units, dram_energy_units;

/*
  Compute the energy reading from the `before`/`after` values, scaled by
  `scale`.

  Note that in some cases `before` may be larger than `after`, due to the
  MSR counter wrapping at 2^32.
*/
double compute_energy(long long before, long long after, double scale) {
  long long diff;

  if (after > before)
    diff = after - before;
  else
    diff = (ENERGY_MAX - before) + after;

  return (double)diff * scale;
}

int open_msr(int core) {
  char msr_filename[32];
  int fd;

  sprintf(msr_filename, "/dev/cpu/%d/msr", core);
  fd = open(msr_filename, O_RDONLY);
  if (fd < 0) {
    if (errno == ENXIO) {
      fprintf(stderr, "open_msr: No CPU %d\n", core);
      exit(2);
    } else if (errno == EIO) {
      fprintf(stderr, "open_msr: CPU %d doesn't support MSRs\n", core);
      exit(3);
    } else {
      perror("open_msr: open");
      fprintf(stderr, "Error trying to open %s\n", msr_filename);
      exit(-1);
    }
  }

  return fd;
}

long long read_msr(int fd, int which) {
  uint64_t data;

  if (pread(fd, &data, sizeof data, which) != sizeof data) {
    perror("read_msr: pread");
    exit(-1);
  }

  return (long long)data;
}

#define CPU_SANDYBRIDGE 42
#define CPU_SANDYBRIDGE_EP 45
#define CPU_IVYBRIDGE 58
#define CPU_IVYBRIDGE_EP 62
#define CPU_HASWELL 60
#define CPU_HASWELL_ULT 69
#define CPU_HASWELL_GT3E 70
#define CPU_HASWELL_EP 63
#define CPU_BROADWELL 61
#define CPU_BROADWELL_GT3E 71
#define CPU_BROADWELL_EP 79
#define CPU_BROADWELL_DE 86
#define CPU_SKYLAKE 78
#define CPU_SKYLAKE_HS 94
#define CPU_SKYLAKE_X 85
#define CPU_KNIGHTS_LANDING 87
#define CPU_KNIGHTS_MILL 133
#define CPU_KABYLAKE_MOBILE 142
#define CPU_KABYLAKE 158
#define CPU_ATOM_SILVERMONT 55
#define CPU_ATOM_AIRMONT 76
#define CPU_ATOM_MERRIFIELD 74
#define CPU_ATOM_MOOREFIELD 90
#define CPU_ATOM_GOLDMONT 92
#define CPU_ATOM_GEMINI_LAKE 122
#define CPU_ATOM_DENVERTON 95

int detect_cpu(void) {
  FILE *file;
  int family, model = -1;
  char buffer[BUFSIZ], *result;
  char vendor[BUFSIZ];

  file = fopen("/proc/cpuinfo", "r");
  if (file == NULL)
    return -1;

  while (model == -1) {
    result = fgets(buffer, BUFSIZ, file);
    if (result == NULL)
      break;

    if (!strncmp(result, "vendor_id", 8)) {
      sscanf(result, "%*s%*s%s", vendor);

      if (strncmp(vendor, "GenuineIntel", 12)) {
        fprintf(stderr, "%s not an Intel chip\n", vendor);
        return -1;
      }
    }

    if (!strncmp(result, "cpu family", 10)) {
      sscanf(result, "%*s%*s%*s%d", &family);
      if (family != 6) {
        fprintf(stderr, "Wrong CPU family %d\n", family);
        return -1;
      }
    }

    if (!strncmp(result, "model", 5)) {
      sscanf(result, "%*s%*s%d", &model);
    }
  }

  fclose(file);

  switch (model) {
  case CPU_SANDYBRIDGE_EP:
  case CPU_IVYBRIDGE_EP:
    pp0_avail = 1;
    pp1_avail = 0;
    dram_avail = 1;
    different_units = 0;
    psys_avail = 0;
    break;
  case CPU_HASWELL_EP:
  case CPU_BROADWELL_EP:
  case CPU_SKYLAKE_X:
    pp0_avail = 1;
    pp1_avail = 0;
    dram_avail = 1;
    different_units = 1;
    psys_avail = 0;
    break;
  case CPU_KNIGHTS_LANDING:
  case CPU_KNIGHTS_MILL:
    pp0_avail = 0;
    pp1_avail = 0;
    dram_avail = 1;
    different_units = 1;
    psys_avail = 0;
    break;
  case CPU_SANDYBRIDGE:
  case CPU_IVYBRIDGE:
    pp0_avail = 1;
    pp1_avail = 1;
    dram_avail = 0;
    different_units = 0;
    psys_avail = 0;
    break;
  case CPU_HASWELL:
  case CPU_HASWELL_ULT:
  case CPU_HASWELL_GT3E:
  case CPU_BROADWELL:
  case CPU_BROADWELL_GT3E:
  case CPU_ATOM_GOLDMONT:
  case CPU_ATOM_GEMINI_LAKE:
  case CPU_ATOM_DENVERTON:
    pp0_avail = 1;
    pp1_avail = 1;
    dram_avail = 1;
    different_units = 0;
    psys_avail = 0;
    break;
  case CPU_SKYLAKE:
  case CPU_SKYLAKE_HS:
  case CPU_KABYLAKE:
  case CPU_KABYLAKE_MOBILE:
    pp0_avail = 1;
    pp1_avail = 1;
    dram_avail = 1;
    different_units = 0;
    psys_avail = 1;
    break;
  default:
    fprintf(stderr, "Unsupported CPU model %d\n", model);
    model = -1;
    break;
  }

  return model;
}

int rapl_init(int core, int show_info) {
  int fd;
  long long result;

  cpu_model = detect_cpu();
  if (cpu_model < 0) {
    fprintf(stderr, "Unsupported CPU type\n");
    return -1;
  }

  fd = open_msr(core);

  /* Calculate the units used */
  result = read_msr(fd, MSR_RAPL_POWER_UNIT);

  power_units = pow(0.5, (double)(result & 0xf));
  cpu_energy_units = pow(0.5, (double)((result >> 8) & 0x1f));
  time_units = pow(0.5, (double)((result >> 16) & 0xf));
  /* Do the DRAM units differ from the CPU ones? */
  if (different_units) {
    dram_energy_units = pow(0.5, (double)16);
  } else {
    dram_energy_units = cpu_energy_units;
  }

  if (show_info) {
    printf("Power units = %.3fW\n", power_units);
    printf("CPU Energy units = %.8fJ\n", cpu_energy_units);
    printf("DRAM Energy units = %.8fJ\n", dram_energy_units);
    printf("Time units = %.8fs\n", time_units);
    printf("\n");
  }

  close(fd);

  return 0;
}

void show_power_info(int core) {
  int fd;
  long long result;
  double thermal_spec_power, minimum_power, maximum_power, time_window;

  /* Show package power info */

  fd = open_msr(core);
  result = read_msr(fd, MSR_PKG_POWER_INFO);

  thermal_spec_power = power_units * (double)(result & 0x7fff);
  printf("Package thermal spec: %.3fW\n", thermal_spec_power);

  minimum_power = power_units * (double)((result >> 16) & 0x7fff);
  printf("Package minimum power: %.3fW\n", minimum_power);

  maximum_power = power_units * (double)((result >> 32) & 0x7fff);
  printf("Package maximum power: %.3fW\n", maximum_power);

  time_window = time_units * (double)((result >> 48) & 0x7fff);
  printf("Package maximum time window: %.6fs\n", time_window);

  close(fd);

  return;
}

void show_power_limit(int core) {
  int fd;
  long long result;

  /* Show package power limit */

  fd = open_msr(core);
  result = read_msr(fd, MSR_PKG_RAPL_POWER_LIMIT);

  printf("Package power limits are %s\n",
         (result >> 63) ? "locked" : "unlocked");
  double pkg_power_limit_1 = power_units * (double)((result >> 0) & 0x7FFF);
  double pkg_time_window_1 = time_units * (double)((result >> 17) & 0x007F);
  printf("Package power limit #1: %.3fW for %.6fs (%s, %s)\n",
         pkg_power_limit_1, pkg_time_window_1,
         (result & (1LL << 15)) ? "enabled" : "disabled",
         (result & (1LL << 16)) ? "clamped" : "not_clamped");
  double pkg_power_limit_2 = power_units * (double)((result >> 32) & 0x7FFF);
  double pkg_time_window_2 = time_units * (double)((result >> 49) & 0x007F);
  printf("Package power limit #2: %.3fW for %.6fs (%s, %s)\n",
         pkg_power_limit_2, pkg_time_window_2,
         (result & (1LL << 47)) ? "enabled" : "disabled",
         (result & (1LL << 48)) ? "clamped" : "not_clamped");
  printf("\n");

  close(fd);

  return;
}

void rapl_before(int core) {
  int fd;

  fd = open_msr(core);

  // Package energy
  package_before = read_msr(fd, MSR_PKG_ENERGY_STATUS) & ENERGY_MASK;

  // PP0 energy
  pp0_before = read_msr(fd, MSR_PP0_ENERGY_STATUS) & ENERGY_MASK;

  /*
    Always reads as zeros on my systems.

  // PP1 energy, if available
  if (pp1_avail)
    pp1_before = read_msr(fd, MSR_PP1_ENERGY_STATUS);
  */

  // DRAM energy, if available
  if (dram_avail)
    dram_before = read_msr(fd, MSR_DRAM_ENERGY_STATUS) & ENERGY_MASK;

  /*
    Not used by my experiments after all.

  // PSYS energy, if available
  if (psys_avail)
    psys_before = read_msr(fd, MSR_PLATFORM_ENERGY_STATUS);
  */

  close(fd);

  return;
}

void rapl_after(FILE *fp, int core) {
  int fd;

  fd = open_msr(core);

  package_after = read_msr(fd, MSR_PKG_ENERGY_STATUS) & ENERGY_MASK;
  fprintf(fp, "package: %.14f\n",
          compute_energy(package_before, package_after, cpu_energy_units));

  pp0_after = read_msr(fd, MSR_PP0_ENERGY_STATUS) & ENERGY_MASK;
  fprintf(fp, "pp0: %.14f\n",
          compute_energy(pp0_before, pp0_after, cpu_energy_units));

  /*
    Always comes up zeros on my machines.

  // PP1 energy, if available
  if (pp1_avail) {
    pp1_after = read_msr(fd, MSR_PP1_ENERGY_STATUS);
    fprintf(fp, "pp1: %.14f\n",
            compute_energy(pp1_before, pp1_after, cpu_energy_units));
  }
  */

  // DRAM energy, if available
  if (dram_avail) {
    dram_after = read_msr(fd, MSR_DRAM_ENERGY_STATUS) & ENERGY_MASK;
    fprintf(fp, "dram: %.14f\n",
            compute_energy(dram_before, dram_after, dram_energy_units));
  }

  /*
    Not used by my experiments after all.

  // PSYS energy, if available
  if (psys_avail) {
    psys_after = read_msr(fd, MSR_PLATFORM_ENERGY_STATUS);
    fprintf(fp, "psys: %.14f\n",
            compute_energy(psys_before, psys_after, cpu_energy_units));
  }
  */

  close(fd);

  return;
}
