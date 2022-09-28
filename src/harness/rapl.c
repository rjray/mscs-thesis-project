/*
  Code for the RAPL interface, adapted from:
  https://github.com/greensoftwarelab/Energy-Languages
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

int cpu_model;
int core = 0;

double package_before, package_after;
double pp0_before, pp0_after;

double power_units, energy_units, time_units;

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
#define CPU_HASWELL2 69
#define CPU_HASWELL3 70
#define CPU_HASWELL_EP 63
#define CPU_SKYLAKE1 78
#define CPU_SKYLAKE2 94
#define CPU_BROADWELL 77
#define CPU_BROADWELL2 79
#define CPU_KABYLAKE_MOBILE 142
#define CPU_KABYLAKE 158

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
  case CPU_SANDYBRIDGE:
  case CPU_SANDYBRIDGE_EP:
  case CPU_IVYBRIDGE:
  case CPU_IVYBRIDGE_EP:
  case CPU_HASWELL:
  case CPU_HASWELL2:
  case CPU_HASWELL3:
  case CPU_HASWELL_EP:
  case CPU_SKYLAKE1:
  case CPU_SKYLAKE2:
  case CPU_BROADWELL:
  case CPU_BROADWELL2:
  case CPU_KABYLAKE:
  case CPU_KABYLAKE_MOBILE:
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
  energy_units = pow(0.5, (double)((result >> 8) & 0x1f));
  time_units = pow(0.5, (double)((result >> 16) & 0xf));

  if (show_info) {
    printf("Power units = %.3fW\n", power_units);
    printf("Energy units = %.8fJ\n", energy_units);
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
  long long result;

  fd = open_msr(core);
  result = read_msr(fd, MSR_PKG_ENERGY_STATUS);

  package_before = (double)result * energy_units;

  result = read_msr(fd, MSR_PP0_ENERGY_STATUS);
  pp0_before = (double)result * energy_units;

  close(fd);

  return;
}

void rapl_after(FILE *fp, int core) {
  int fd;
  long long result;

  fd = open_msr(core);

  result = read_msr(fd, MSR_PKG_ENERGY_STATUS);
  package_after = (double)result * energy_units;
  fprintf(fp, "package: %.18f\n", package_after - package_before);

  result = read_msr(fd, MSR_PP0_ENERGY_STATUS);
  pp0_after = (double)result * energy_units;
  fprintf(fp, "cpu: %.18f\n", pp0_after - pp0_before);

  close(fd);

  return;
}
