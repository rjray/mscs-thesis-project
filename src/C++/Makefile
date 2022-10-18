include ../defines.mk

GCC_TARGETS := $(addprefix ./,$(addsuffix -cpp-gcc,$(ALGORITHMS)))
LLVM_TARGETS := $(addprefix ./,$(addsuffix -cpp-llvm,$(ALGORITHMS)))
INTEL_TARGETS := $(addprefix ./,$(addsuffix -cpp-intel,$(ALGORITHMS)))

# These start out without Intel, in case the user doesn't want the Intel stuff
# used.
TARGETS := $(GCC_TARGETS) $(LLVM_TARGETS)
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
TOP_TARGETS += intel
endif

TEST_EXPERIMENTS = $(addprefix test-experiments-,$(TOP_TARGETS))
EXPERIMENTS = $(addprefix experiments-,$(TOP_TARGETS))

all: $(TOP_TARGETS)

gcc: $(GCC_TARGETS)

llvm: $(LLVM_TARGETS)

intel: $(INTEL_TARGETS)

test-experiments: $(TEST_EXPERIMENTS)

experiments: $(EXPERIMENTS)

clean:
	$(RM) *.o
	$(RM) $(TARGETS)

reset: clean all

# Rules for building with GCC:
run-gcc.o: run.cpp run.hpp setup.hpp
	$(GCC) $(CPPFLAGS) -c -o run-gcc.o run.cpp

setup-gcc.o: setup.cpp setup.hpp
	$(GCC) $(CPPFLAGS) -c -o setup-gcc.o setup.cpp

kmp-gcc.o: kmp.cpp run.hpp
	$(GCC) $(CPPFLAGS) -c -o kmp-gcc.o kmp.cpp

kmp-cpp-gcc: kmp-gcc.o run-gcc.o setup-gcc.o
	$(GCC) $(CPPFLAGS) -o kmp-cpp-gcc kmp-gcc.o run-gcc.o setup-gcc.o

boyer_moore-gcc.o: boyer_moore.cpp run.hpp
	$(GCC) $(CPPFLAGS) -c -o boyer_moore-gcc.o boyer_moore.cpp

boyer_moore-cpp-gcc: boyer_moore-gcc.o run-gcc.o setup-gcc.o
	$(GCC) $(CPPFLAGS) -o boyer_moore-cpp-gcc boyer_moore-gcc.o run-gcc.o setup-gcc.o

shift_or-gcc.o: shift_or.cpp run.hpp
	$(GCC) $(CPPFLAGS) -c -o shift_or-gcc.o shift_or.cpp

shift_or-cpp-gcc: shift_or-gcc.o run-gcc.o setup-gcc.o
	$(GCC) $(CPPFLAGS) -o shift_or-cpp-gcc shift_or-gcc.o run-gcc.o setup-gcc.o

aho_corasick-gcc.o: aho_corasick.cpp run.hpp
	$(GCC) $(CPPFLAGS) -c -o aho_corasick-gcc.o aho_corasick.cpp

aho_corasick-cpp-gcc: aho_corasick-gcc.o run-gcc.o setup-gcc.o
	$(GCC) $(CPPFLAGS) -o aho_corasick-cpp-gcc aho_corasick-gcc.o run-gcc.o setup-gcc.o

# Rules for building with LLVM:
run-llvm.o: run.cpp run.hpp setup.hpp
	$(CLANG) $(CPPFLAGS) -c -o run-llvm.o run.cpp

setup-llvm.o: setup.cpp setup.hpp
	$(CLANG) $(CPPFLAGS) -c -o setup-llvm.o setup.cpp

kmp-llvm.o: kmp.cpp run.hpp
	$(CLANG) $(CPPFLAGS) -c -o kmp-llvm.o kmp.cpp

kmp-cpp-llvm: kmp-llvm.o run-llvm.o setup-llvm.o
	$(CLANG) $(CPPFLAGS) -o kmp-cpp-llvm kmp-llvm.o run-llvm.o setup-llvm.o

boyer_moore-llvm.o: boyer_moore.cpp run.hpp
	$(CLANG) $(CPPFLAGS) -c -o boyer_moore-llvm.o boyer_moore.cpp

boyer_moore-cpp-llvm: boyer_moore-llvm.o run-llvm.o setup-llvm.o
	$(CLANG) $(CPPFLAGS) -o boyer_moore-cpp-llvm boyer_moore-llvm.o run-llvm.o setup-llvm.o

shift_or-llvm.o: shift_or.cpp run.hpp
	$(CLANG) $(CPPFLAGS) -c -o shift_or-llvm.o shift_or.cpp

shift_or-cpp-llvm: shift_or-llvm.o run-llvm.o setup-llvm.o
	$(CLANG) $(CPPFLAGS) -o shift_or-cpp-llvm shift_or-llvm.o run-llvm.o setup-llvm.o

aho_corasick-llvm.o: aho_corasick.cpp run.hpp
	$(CLANG) $(CPPFLAGS) -c -o aho_corasick-llvm.o aho_corasick.cpp

aho_corasick-cpp-llvm: aho_corasick-llvm.o run-llvm.o setup-llvm.o
	$(CLANG) $(CPPFLAGS) -o aho_corasick-cpp-llvm aho_corasick-llvm.o run-llvm.o setup-llvm.o

# Rules for building with Intel:
run-intel.o: run.cpp run.hpp setup.hpp
	$(ICX) $(CPPFLAGS) -c -o run-intel.o run.cpp

setup-intel.o: setup.cpp setup.hpp
	$(ICX) $(CPPFLAGS) -c -o setup-intel.o setup.cpp

kmp-intel.o: kmp.cpp run.hpp
	$(ICX) $(CPPFLAGS) -c -o kmp-intel.o kmp.cpp

kmp-cpp-intel: kmp-intel.o run-intel.o setup-intel.o
	$(ICX) $(CPPFLAGS) -o kmp-cpp-intel kmp-intel.o run-intel.o setup-intel.o

boyer_moore-intel.o: boyer_moore.cpp run.hpp
	$(ICX) $(CPPFLAGS) -c -o boyer_moore-intel.o boyer_moore.cpp

boyer_moore-cpp-intel: boyer_moore-intel.o run-intel.o setup-intel.o
	$(ICX) $(CPPFLAGS) -o boyer_moore-cpp-intel boyer_moore-intel.o run-intel.o setup-intel.o

shift_or-intel.o: shift_or.cpp run.hpp
	$(ICX) $(CPPFLAGS) -c -o shift_or-intel.o shift_or.cpp

shift_or-cpp-intel: shift_or-intel.o run-intel.o setup-intel.o
	$(ICX) $(CPPFLAGS) -o shift_or-cpp-intel shift_or-intel.o run-intel.o setup-intel.o

aho_corasick-intel.o: aho_corasick.cpp run.hpp
	$(ICX) $(CPPFLAGS) -c -o aho_corasick-intel.o aho_corasick.cpp

aho_corasick-cpp-intel: aho_corasick-intel.o run-intel.o setup-intel.o
	$(ICX) $(CPPFLAGS) -o aho_corasick-cpp-intel aho_corasick-intel.o run-intel.o setup-intel.o

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
