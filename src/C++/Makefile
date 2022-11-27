# This is the Makefile for the C++ implementation of the algorithms.
#
# This is as long and complex as the C Makefile, for the same reasons (multiple
# compilers, etc.). Someone better versed in GNU Make could probably shorten
# this considerably with some choice macros.

include ../defines.mk

# Define all the sets of targets by adding the language (cpp) and toolchain to
# the algorithm names.
GCC_TARGETS := $(addprefix ./,$(addsuffix -cpp-gcc,$(ALGORITHMS)))
LLVM_TARGETS := $(addprefix ./,$(addsuffix -cpp-llvm,$(ALGORITHMS)))
INTEL_TARGETS := $(addprefix ./,$(addsuffix -cpp-intel,$(ALGORITHMS)))
GCC_APPROX_TARGETS := $(addprefix ./,$(addsuffix -cpp-gcc,$(APPROX_ALGORITHMS)))
LLVM_APPROX_TARGETS := $(addprefix ./,$(addsuffix -cpp-llvm,$(APPROX_ALGORITHMS)))
INTEL_APPROX_TARGETS := $(addprefix ./,$(addsuffix -cpp-intel,$(APPROX_ALGORITHMS)))

# These start out without Intel, in case the user doesn't want the Intel stuff
# used.
TARGETS := $(GCC_TARGETS) $(LLVM_TARGETS)
APPROX_TARGETS := $(GCC_APPROX_TARGETS) $(LLVM_APPROX_TARGETS)
TOP_TARGETS := gcc llvm

# Default this to unset
DEBUG=

CPPFLAGS := -Wall -std=c++2a
# Determine additional CPPFLAGS based on DEBUG:
ifeq ($(DEBUG),)
CPPFLAGS += -O3
else
CPPFLAGS += -g
endif

GCC=g++
CLANG=clang++
ICX=icpx

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
run-gcc.o: run.cpp run.hpp input.hpp
	$(GCC) $(CPPFLAGS) -c -o run-gcc.o run.cpp

input-gcc.o: input.cpp input.hpp
	$(GCC) $(CPPFLAGS) -c -o input-gcc.o input.cpp

kmp-gcc.o: kmp.cpp run.hpp
	$(GCC) $(CPPFLAGS) -c -o kmp-gcc.o kmp.cpp

kmp-cpp-gcc: kmp-gcc.o run-gcc.o input-gcc.o
	$(GCC) $(CPPFLAGS) -o kmp-cpp-gcc kmp-gcc.o run-gcc.o input-gcc.o

boyer_moore-gcc.o: boyer_moore.cpp run.hpp
	$(GCC) $(CPPFLAGS) -c -o boyer_moore-gcc.o boyer_moore.cpp

boyer_moore-cpp-gcc: boyer_moore-gcc.o run-gcc.o input-gcc.o
	$(GCC) $(CPPFLAGS) -o boyer_moore-cpp-gcc boyer_moore-gcc.o run-gcc.o input-gcc.o

shift_or-gcc.o: shift_or.cpp run.hpp
	$(GCC) $(CPPFLAGS) -c -o shift_or-gcc.o shift_or.cpp

shift_or-cpp-gcc: shift_or-gcc.o run-gcc.o input-gcc.o
	$(GCC) $(CPPFLAGS) -o shift_or-cpp-gcc shift_or-gcc.o run-gcc.o input-gcc.o

aho_corasick-gcc.o: aho_corasick.cpp run.hpp
	$(GCC) $(CPPFLAGS) -c -o aho_corasick-gcc.o aho_corasick.cpp

aho_corasick-cpp-gcc: aho_corasick-gcc.o run-gcc.o input-gcc.o
	$(GCC) $(CPPFLAGS) -o aho_corasick-cpp-gcc aho_corasick-gcc.o run-gcc.o input-gcc.o

dfa_gap-gcc.o: dfa_gap.cpp run.hpp
	$(GCC) $(CPPFLAGS) -c -o dfa_gap-gcc.o dfa_gap.cpp

dfa_gap-cpp-gcc: dfa_gap-gcc.o run-gcc.o input-gcc.o
	$(GCC) $(CPPFLAGS) -o dfa_gap-cpp-gcc dfa_gap-gcc.o run-gcc.o input-gcc.o

regexp-gcc.o: regexp.cpp run.hpp
	$(GCC) $(CPPFLAGS) -c -o regexp-gcc.o regexp.cpp

regexp-cpp-gcc: regexp-gcc.o run-gcc.o input-gcc.o
	$(GCC) $(CPPFLAGS) -o regexp-cpp-gcc regexp-gcc.o run-gcc.o input-gcc.o -lpcre2-8

# Rules for building with LLVM:
run-llvm.o: run.cpp run.hpp input.hpp
	$(CLANG) $(CPPFLAGS) -c -o run-llvm.o run.cpp

input-llvm.o: input.cpp input.hpp
	$(CLANG) $(CPPFLAGS) -c -o input-llvm.o input.cpp

kmp-llvm.o: kmp.cpp run.hpp
	$(CLANG) $(CPPFLAGS) -c -o kmp-llvm.o kmp.cpp

kmp-cpp-llvm: kmp-llvm.o run-llvm.o input-llvm.o
	$(CLANG) $(CPPFLAGS) -o kmp-cpp-llvm kmp-llvm.o run-llvm.o input-llvm.o

boyer_moore-llvm.o: boyer_moore.cpp run.hpp
	$(CLANG) $(CPPFLAGS) -c -o boyer_moore-llvm.o boyer_moore.cpp

boyer_moore-cpp-llvm: boyer_moore-llvm.o run-llvm.o input-llvm.o
	$(CLANG) $(CPPFLAGS) -o boyer_moore-cpp-llvm boyer_moore-llvm.o run-llvm.o input-llvm.o

shift_or-llvm.o: shift_or.cpp run.hpp
	$(CLANG) $(CPPFLAGS) -c -o shift_or-llvm.o shift_or.cpp

shift_or-cpp-llvm: shift_or-llvm.o run-llvm.o input-llvm.o
	$(CLANG) $(CPPFLAGS) -o shift_or-cpp-llvm shift_or-llvm.o run-llvm.o input-llvm.o

aho_corasick-llvm.o: aho_corasick.cpp run.hpp
	$(CLANG) $(CPPFLAGS) -c -o aho_corasick-llvm.o aho_corasick.cpp

aho_corasick-cpp-llvm: aho_corasick-llvm.o run-llvm.o input-llvm.o
	$(CLANG) $(CPPFLAGS) -o aho_corasick-cpp-llvm aho_corasick-llvm.o run-llvm.o input-llvm.o

dfa_gap-llvm.o: dfa_gap.cpp run.hpp
	$(CLANG) $(CPPFLAGS) -c -o dfa_gap-llvm.o dfa_gap.cpp

dfa_gap-cpp-llvm: dfa_gap-llvm.o run-llvm.o input-llvm.o
	$(CLANG) $(CPPFLAGS) -o dfa_gap-cpp-llvm dfa_gap-llvm.o run-llvm.o input-llvm.o

regexp-llvm.o: regexp.cpp run.hpp
	$(CLANG) $(CPPFLAGS) -c -o regexp-llvm.o regexp.cpp

regexp-cpp-llvm: regexp-llvm.o run-llvm.o input-llvm.o
	$(CLANG) $(CPPFLAGS) -o regexp-cpp-llvm regexp-llvm.o run-llvm.o input-llvm.o -lpcre2-8

# Rules for building with Intel:
run-intel.o: run.cpp run.hpp input.hpp
	$(ICX) $(CPPFLAGS) -c -o run-intel.o run.cpp

input-intel.o: input.cpp input.hpp
	$(ICX) $(CPPFLAGS) -c -o input-intel.o input.cpp

kmp-intel.o: kmp.cpp run.hpp
	$(ICX) $(CPPFLAGS) -c -o kmp-intel.o kmp.cpp

kmp-cpp-intel: kmp-intel.o run-intel.o input-intel.o
	$(ICX) $(CPPFLAGS) -o kmp-cpp-intel kmp-intel.o run-intel.o input-intel.o

boyer_moore-intel.o: boyer_moore.cpp run.hpp
	$(ICX) $(CPPFLAGS) -c -o boyer_moore-intel.o boyer_moore.cpp

boyer_moore-cpp-intel: boyer_moore-intel.o run-intel.o input-intel.o
	$(ICX) $(CPPFLAGS) -o boyer_moore-cpp-intel boyer_moore-intel.o run-intel.o input-intel.o

shift_or-intel.o: shift_or.cpp run.hpp
	$(ICX) $(CPPFLAGS) -c -o shift_or-intel.o shift_or.cpp

shift_or-cpp-intel: shift_or-intel.o run-intel.o input-intel.o
	$(ICX) $(CPPFLAGS) -o shift_or-cpp-intel shift_or-intel.o run-intel.o input-intel.o

aho_corasick-intel.o: aho_corasick.cpp run.hpp
	$(ICX) $(CPPFLAGS) -c -o aho_corasick-intel.o aho_corasick.cpp

aho_corasick-cpp-intel: aho_corasick-intel.o run-intel.o input-intel.o
	$(ICX) $(CPPFLAGS) -o aho_corasick-cpp-intel aho_corasick-intel.o run-intel.o input-intel.o

dfa_gap-intel.o: dfa_gap.cpp run.hpp
	$(ICX) $(CPPFLAGS) -c -o dfa_gap-intel.o dfa_gap.cpp

dfa_gap-cpp-intel: dfa_gap-intel.o run-intel.o input-intel.o
	$(ICX) $(CPPFLAGS) -o dfa_gap-cpp-intel dfa_gap-intel.o run-intel.o input-intel.o

regexp-intel.o: regexp.cpp run.hpp
	$(ICX) $(CPPFLAGS) -c -o regexp-intel.o regexp.cpp

regexp-cpp-intel: regexp-intel.o run-intel.o input-intel.o
	$(ICX) $(CPPFLAGS) -o regexp-cpp-intel regexp-intel.o run-intel.o input-intel.o -lpcre2-8

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
