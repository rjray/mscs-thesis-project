# This is the Makefile for the C implementation of the algorithms.
#
# This looks pretty complex and certainly redundant. It build all programs for
# (up to) three toolchains so that the data gathered compares the toolchains as
# well as the languages.
#
# Someone much better at GNU Make than I am could probably shorten this quite a
# bit with some good macro-programming and more cleverness in the build-rules
# that are repeated for each toolchain.

include ../defines.mk

# Define all the sets of targets by adding the language (c) and toolchain to
# the algorithm names.
GCC_TARGETS := $(addprefix ./,$(addsuffix -c-gcc,$(ALGORITHMS)))
LLVM_TARGETS := $(addprefix ./,$(addsuffix -c-llvm,$(ALGORITHMS)))
INTEL_TARGETS := $(addprefix ./,$(addsuffix -c-intel,$(ALGORITHMS)))
GCC_APPROX_TARGETS := $(addprefix ./,$(addsuffix -c-gcc,$(APPROX_ALGORITHMS)))
LLVM_APPROX_TARGETS := $(addprefix ./,$(addsuffix -c-llvm,$(APPROX_ALGORITHMS)))
INTEL_APPROX_TARGETS := $(addprefix ./,$(addsuffix -c-intel,$(APPROX_ALGORITHMS)))

# These start out without Intel, in case the user doesn't want the Intel stuff
# used.
TARGETS := $(GCC_TARGETS) $(LLVM_TARGETS)
APPROX_TARGETS := $(GCC_APPROX_TARGETS) $(LLVM_APPROX_TARGETS)
TOP_TARGETS := gcc llvm

# Default this to unset
DEBUG=

CFLAGS := -Wall -std=c17 -D_GNU_SOURCE
# Determine additional CFLAGS based on DEBUG:
ifeq ($(DEBUG),)
CFLAGS += -O3
else
CFLAGS += -g
endif

GCC=gcc
CLANG=clang
ICX=icx

# Unless they specifically disabled the use of the Intel toolchain, add it in.
ifeq ($(NO_INTEL),)
TARGETS += $(INTEL_TARGETS)
APPROX_TARGETS += $(INTEL_APPROX_TARGETS)
TOP_TARGETS += intel
endif

# Define the groupings of experiments, again by toolchain as well as by exact
# vs. approximate.
TEST_EXPERIMENTS := $(addprefix test-experiments-,$(TOP_TARGETS))
TEST_APPROX_EXPERIMENTS := $(addprefix test-approx-experiments-,$(TOP_TARGETS))
EXPERIMENTS := $(addprefix experiments-,$(TOP_TARGETS))
APPROX_EXPERIMENTS := $(addprefix approx-experiments-,$(TOP_TARGETS))

all: $(TOP_TARGETS)

gcc: $(GCC_TARGETS) $(GCC_APPROX_TARGETS)

llvm: $(LLVM_TARGETS) $(LLVM_APPROX_TARGETS)

intel: $(INTEL_TARGETS) $(INTEL_APPROX_TARGETS)

test-experiments: $(TEST_EXPERIMENTS) $(TEST_APPROX_EXPERIMENTS)

experiments: $(EXPERIMENTS) $(APPROX_EXPERIMENTS)

clean:
	$(RM) *.o
	$(RM) $(TARGETS) $(APPROX_TARGETS)

reset: clean all

# Rules for building with GCC:
run-gcc.o: run.c run.h input.h
	$(GCC) $(CFLAGS) -c -o run-gcc.o run.c

input-gcc.o: input.c input.h
	$(GCC) $(CFLAGS) -c -o input-gcc.o input.c

kmp-gcc.o: kmp.c run.h
	$(GCC) $(CFLAGS) -c -o kmp-gcc.o kmp.c

kmp-c-gcc: kmp-gcc.o run-gcc.o input-gcc.o
	$(GCC) $(CFLAGS) -o kmp-c-gcc kmp-gcc.o run-gcc.o input-gcc.o

boyer_moore-gcc.o: boyer_moore.c run.h
	$(GCC) $(CFLAGS) -c -o boyer_moore-gcc.o boyer_moore.c

boyer_moore-c-gcc: boyer_moore-gcc.o run-gcc.o input-gcc.o
	$(GCC) $(CFLAGS) -o boyer_moore-c-gcc boyer_moore-gcc.o run-gcc.o input-gcc.o

shift_or-gcc.o: shift_or.c run.h
	$(GCC) $(CFLAGS) -c -o shift_or-gcc.o shift_or.c

shift_or-c-gcc: shift_or-gcc.o run-gcc.o input-gcc.o
	$(GCC) $(CFLAGS) -o shift_or-c-gcc shift_or-gcc.o run-gcc.o input-gcc.o

aho_corasick-gcc.o: aho_corasick.c run.h
	$(GCC) $(CFLAGS) -c -o aho_corasick-gcc.o aho_corasick.c

aho_corasick-c-gcc: aho_corasick-gcc.o run-gcc.o input-gcc.o
	$(GCC) $(CFLAGS) -o aho_corasick-c-gcc aho_corasick-gcc.o run-gcc.o input-gcc.o

dfa_gap-gcc.o: dfa_gap.c run.h
	$(GCC) $(CFLAGS) -c -o dfa_gap-gcc.o dfa_gap.c

dfa_gap-c-gcc: dfa_gap-gcc.o run-gcc.o input-gcc.o
	$(GCC) $(CFLAGS) -o dfa_gap-c-gcc dfa_gap-gcc.o run-gcc.o input-gcc.o

regexp-gcc.o: regexp.c run.h
	$(GCC) $(CFLAGS) -c -o regexp-gcc.o regexp.c

regexp-c-gcc: regexp-gcc.o run-gcc.o input-gcc.o
	$(GCC) $(CFLAGS) -o regexp-c-gcc regexp-gcc.o run-gcc.o input-gcc.o -lpcre2-8

# Rules for building with LLVM:
run-llvm.o: run.c run.h input.h
	$(CLANG) $(CFLAGS) -c -o run-llvm.o run.c

input-llvm.o: input.c input.h
	$(CLANG) $(CFLAGS) -c -o input-llvm.o input.c

kmp-llvm.o: kmp.c run.h
	$(CLANG) $(CFLAGS) -c -o kmp-llvm.o kmp.c

kmp-c-llvm: kmp-llvm.o run-llvm.o input-llvm.o
	$(CLANG) $(CFLAGS) -o kmp-c-llvm kmp-llvm.o run-llvm.o input-llvm.o

boyer_moore-llvm.o: boyer_moore.c run.h
	$(CLANG) $(CFLAGS) -c -o boyer_moore-llvm.o boyer_moore.c

boyer_moore-c-llvm: boyer_moore-llvm.o run-llvm.o input-llvm.o
	$(CLANG) $(CFLAGS) -o boyer_moore-c-llvm boyer_moore-llvm.o run-llvm.o input-llvm.o

shift_or-llvm.o: shift_or.c run.h
	$(CLANG) $(CFLAGS) -c -o shift_or-llvm.o shift_or.c

shift_or-c-llvm: shift_or-llvm.o run-llvm.o input-llvm.o
	$(CLANG) $(CFLAGS) -o shift_or-c-llvm shift_or-llvm.o run-llvm.o input-llvm.o

aho_corasick-llvm.o: aho_corasick.c run.h
	$(CLANG) $(CFLAGS) -c -o aho_corasick-llvm.o aho_corasick.c

aho_corasick-c-llvm: aho_corasick-llvm.o run-llvm.o input-llvm.o
	$(CLANG) $(CFLAGS) -o aho_corasick-c-llvm aho_corasick-llvm.o run-llvm.o input-llvm.o

dfa_gap-llvm.o: dfa_gap.c run.h
	$(CLANG) $(CFLAGS) -c -o dfa_gap-llvm.o dfa_gap.c

dfa_gap-c-llvm: dfa_gap-llvm.o run-llvm.o input-llvm.o
	$(CLANG) $(CFLAGS) -o dfa_gap-c-llvm dfa_gap-llvm.o run-llvm.o input-llvm.o

regexp-llvm.o: regexp.c run.h
	$(CLANG) $(CFLAGS) -c -o regexp-llvm.o regexp.c

regexp-c-llvm: regexp-llvm.o run-llvm.o input-llvm.o
	$(CLANG) $(CFLAGS) -o regexp-c-llvm regexp-llvm.o run-llvm.o input-llvm.o -lpcre2-8

# Rules for building with Intel:
run-intel.o: run.c run.h input.h
	$(ICX) $(CFLAGS) -c -o run-intel.o run.c

input-intel.o: input.c input.h
	$(ICX) $(CFLAGS) -c -o input-intel.o input.c

kmp-intel.o: kmp.c run.h
	$(ICX) $(CFLAGS) -c -o kmp-intel.o kmp.c

kmp-c-intel: kmp-intel.o run-intel.o input-intel.o
	$(ICX) $(CFLAGS) -o kmp-c-intel kmp-intel.o run-intel.o input-intel.o

boyer_moore-intel.o: boyer_moore.c run.h
	$(ICX) $(CFLAGS) -c -o boyer_moore-intel.o boyer_moore.c

boyer_moore-c-intel: boyer_moore-intel.o run-intel.o input-intel.o
	$(ICX) $(CFLAGS) -o boyer_moore-c-intel boyer_moore-intel.o run-intel.o input-intel.o

shift_or-intel.o: shift_or.c run.h
	$(ICX) $(CFLAGS) -c -o shift_or-intel.o shift_or.c

shift_or-c-intel: shift_or-intel.o run-intel.o input-intel.o
	$(ICX) $(CFLAGS) -o shift_or-c-intel shift_or-intel.o run-intel.o input-intel.o

aho_corasick-intel.o: aho_corasick.c run.h
	$(ICX) $(CFLAGS) -c -o aho_corasick-intel.o aho_corasick.c

aho_corasick-c-intel: aho_corasick-intel.o run-intel.o input-intel.o
	$(ICX) $(CFLAGS) -o aho_corasick-c-intel aho_corasick-intel.o run-intel.o input-intel.o

dfa_gap-intel.o: dfa_gap.c run.h
	$(ICX) $(CFLAGS) -c -o dfa_gap-intel.o dfa_gap.c

dfa_gap-c-intel: dfa_gap-intel.o run-intel.o input-intel.o
	$(ICX) $(CFLAGS) -o dfa_gap-c-intel dfa_gap-intel.o run-intel.o input-intel.o

regexp-intel.o: regexp.c run.h
	$(ICX) $(CFLAGS) -c -o regexp-intel.o regexp.c

regexp-c-intel: regexp-intel.o run-intel.o input-intel.o
	$(ICX) $(CFLAGS) -o regexp-c-intel regexp-intel.o run-intel.o input-intel.o -lpcre2-8

# Rules for running the experiments, broken down by toolchain.
test-experiments-gcc:
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run tests)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run tests)
endif
ifeq ($(ANSWERS),)
	$(warning Answer file not specified, no checking will be done)
endif
	$(foreach target,$(GCC_TARGETS),$(call RUN_test_experiment,$(target)))

test-approx-experiments-gcc:
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run tests)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run tests)
endif
ifeq ($(APPROX_ANSWERS),)
	$(warning Answer file not specified, no checking will be done)
endif
	$(foreach target,$(GCC_APPROX_TARGETS),$(call RUN_test_approx_experiment,$(target)))

experiments-gcc:
ifeq ($(HARNESS),)
	$(error Harness not specified, cannot run experiments)
endif
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run experiments)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run experiments)
endif
ifeq ($(ANSWERS),)
	$(warning Answers file not specified, no checking will be done)
endif
	$(foreach target,$(GCC_TARGETS),$(call RUN_experiment,$(target)))

approx-experiments-gcc:
ifeq ($(HARNESS),)
	$(error Harness not specified, cannot run experiments)
endif
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run experiments)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run experiments)
endif
ifeq ($(APPROX_ANSWERS),)
	$(warning Answers file not specified, no checking will be done)
endif
	$(foreach target,$(GCC_APPROX_TARGETS),\
		$(foreach k,$(K),\
			$(call RUN_approx_experiment,$(target) $(k))\
		)\
	)

test-experiments-llvm:
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run tests)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run tests)
endif
ifeq ($(ANSWERS),)
	$(warning Answer file not specified, no checking will be done)
endif
	$(foreach target,$(LLVM_TARGETS),$(call RUN_test_experiment,$(target)))

test-approx-experiments-llvm:
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run tests)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run tests)
endif
ifeq ($(APPROX_ANSWERS),)
	$(warning Answer file not specified, no checking will be done)
endif
	$(foreach target,$(LLVM_APPROX_TARGETS),$(call RUN_test_approx_experiment,$(target)))

experiments-llvm:
ifeq ($(HARNESS),)
	$(error Harness not specified, cannot run experiments)
endif
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run experiments)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run experiments)
endif
ifeq ($(ANSWERS),)
	$(warning Answers file not specified, no checking will be done)
endif
	$(foreach target,$(LLVM_TARGETS),$(call RUN_experiment,$(target)))

approx-experiments-llvm:
ifeq ($(HARNESS),)
	$(error Harness not specified, cannot run experiments)
endif
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run experiments)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run experiments)
endif
ifeq ($(APPROX_ANSWERS),)
	$(warning Answers file not specified, no checking will be done)
endif
	$(foreach target,$(LLVM_APPROX_TARGETS),\
		$(foreach k,$(K),\
			$(call RUN_approx_experiment,$(target) $(k))\
		)\
	)

test-experiments-intel:
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run tests)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run tests)
endif
ifeq ($(ANSWERS),)
	$(warning Answer file not specified, no checking will be done)
endif
	$(foreach target,$(INTEL_TARGETS),$(call RUN_test_experiment,$(target)))

test-approx-experiments-intel:
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run tests)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run tests)
endif
ifeq ($(APPROX_ANSWERS),)
	$(warning Answer file not specified, no checking will be done)
endif
	$(foreach target,$(INTEL_APPROX_TARGETS),$(call RUN_test_approx_experiment,$(target)))

experiments-intel:
ifeq ($(HARNESS),)
	$(error Harness not specified, cannot run experiments)
endif
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run experiments)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run experiments)
endif
ifeq ($(ANSWERS),)
	$(warning Answers file not specified, no checking will be done)
endif
	$(foreach target,$(INTEL_TARGETS),$(call RUN_experiment,$(target)))

approx-experiments-intel:
ifeq ($(HARNESS),)
	$(error Harness not specified, cannot run experiments)
endif
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run experiments)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run experiments)
endif
ifeq ($(APPROX_ANSWERS),)
	$(warning Answers file not specified, no checking will be done)
endif
	$(foreach target,$(INTEL_APPROX_TARGETS),\
		$(foreach k,$(K),\
			$(call RUN_approx_experiment,$(target) $(k))\
		)\
	)
