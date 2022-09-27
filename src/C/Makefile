include ../defines.mk

GCC_TARGETS := $(addprefix ./,$(addsuffix -c-gcc,$(ALGORITHMS)))
LLVM_TARGETS := $(addprefix ./,$(addsuffix -c-llvm,$(ALGORITHMS)))

# Default this to unset
DEBUG=

# Determine CFLAGS based on DEBUG:
ifeq ($(DEBUG),)
CFLAGS += -O3
else
CFLAGS += -g
endif

GCC=gcc
CLANG=clang

all: gcc llvm

gcc: $(GCC_TARGETS)

llvm: $(LLVM_TARGETS)

clean:
	$(RM) *.o
	$(RM) $(GCC_TARGETS) $(LLVM_TARGETS)

# Rules for building with gcc:
run-gcc.o: run.c run.h setup.h
	$(GCC) $(CFLAGS) -c -o run-gcc.o run.c

setup-gcc.o: setup.c setup.h
	$(GCC) $(CFLAGS) -c -o setup-gcc.o setup.c

kmp-gcc.o: kmp.c run.h
	$(GCC) $(CFLAGS) -c -o kmp-gcc.o kmp.c

kmp-c-gcc: kmp-gcc.o run-gcc.o setup-gcc.o
	$(GCC) $(CFLAGS) -o kmp-c-gcc kmp-gcc.o run-gcc.o setup-gcc.o

boyer_moore-gcc.o: boyer_moore.c run.h
	$(GCC) $(CFLAGS) -c -o boyer_moore-gcc.o boyer_moore.c

boyer_moore-c-gcc: boyer_moore-gcc.o run-gcc.o setup-gcc.o
	$(GCC) $(CFLAGS) -o boyer_moore-c-gcc boyer_moore-gcc.o run-gcc.o setup-gcc.o

shift_or-gcc.o: shift_or.c run.h
	$(GCC) $(CFLAGS) -c -o shift_or-gcc.o shift_or.c

shift_or-c-gcc: shift_or-gcc.o run-gcc.o setup-gcc.o
	$(GCC) $(CFLAGS) -o shift_or-c-gcc shift_or-gcc.o run-gcc.o setup-gcc.o

aho_corasick-gcc.o: aho_corasick.c setup.h
	$(GCC) $(CFLAGS) -c -o aho_corasick-gcc.o aho_corasick.c

aho_corasick-c-gcc: aho_corasick-gcc.o setup-gcc.o
	$(GCC) $(CFLAGS) -o aho_corasick-c-gcc aho_corasick-gcc.o setup-gcc.o

# Rules for building with LLVM:
run-llvm.o: run.c run.h setup.h
	$(CLANG) $(CFLAGS) -c -o run-llvm.o run.c

setup-llvm.o: setup.c setup.h
	$(CLANG) $(CFLAGS) -c -o setup-llvm.o setup.c

kmp-llvm.o: kmp.c run.h
	$(CLANG) $(CFLAGS) -c -o kmp-llvm.o kmp.c

kmp-c-llvm: kmp-llvm.o run-llvm.o setup-llvm.o
	$(CLANG) $(CFLAGS) -o kmp-c-llvm kmp-llvm.o run-llvm.o setup-llvm.o

boyer_moore-llvm.o: boyer_moore.c run.h
	$(CLANG) $(CFLAGS) -c -o boyer_moore-llvm.o boyer_moore.c

boyer_moore-c-llvm: boyer_moore-llvm.o run-llvm.o setup-llvm.o
	$(CLANG) $(CFLAGS) -o boyer_moore-c-llvm boyer_moore-llvm.o run-llvm.o setup-llvm.o

shift_or-llvm.o: shift_or.c run.h
	$(CLANG) $(CFLAGS) -c -o shift_or-llvm.o shift_or.c

shift_or-c-llvm: shift_or-llvm.o run-llvm.o setup-llvm.o
	$(CLANG) $(CFLAGS) -o shift_or-c-llvm shift_or-llvm.o run-llvm.o setup-llvm.o

aho_corasick-llvm.o: aho_corasick.c setup.h
	$(CLANG) $(CFLAGS) -c -o aho_corasick-llvm.o aho_corasick.c

aho_corasick-c-llvm: aho_corasick-llvm.o setup-llvm.o
	$(CLANG) $(CFLAGS) -o aho_corasick-c-llvm aho_corasick-llvm.o setup-llvm.o

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

test-experiments: test-experiments-gcc test-experiments-llvm

experiments: experiments-gcc experiments-llvm
