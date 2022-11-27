# This is the Makefile for the Python implementation of the algorithms.
#
# While not as long as the C/C++ Makefiles, the need to break the algorithms
# into the longer-running, etc. for the sake of smaller iteration counts makes
# it more complex.
#
# Note that there are no actual build or clean targets since this is all
# interpreted code.

include ../defines.mk

# LONG_TARGETS are those that run significantly longer and thus have to run for
# fewer iterations. SHORT_TARGETS are those that can run the regular number of
# iterations. APPROX_TARGETS are the approximate-matching algorithms, which
# generally take even longer.
LONG_TARGETS := $(addprefix ./,$(addsuffix .py,$(LONG_ALGORITHMS)))
SHORT_TARGETS := $(addprefix ./,$(addsuffix .py,$(SHORT_ALGORITHMS)))
APPROX_TARGETS := $(addprefix ./,$(addsuffix .py,$(APPROX_ALGORITHMS)))
TARGETS := $(LONG_TARGETS) $(SHORT_TARGETS) $(APPROX_TARGETS)

all: $(TARGETS)

clean:
	@echo "No clean-up needed in Python"

# Run the experiments on the test-level data.
test-experiments: test-exact-experiments test-approx-experiments

# Test data, exact matching algorithms.
test-exact-experiments:
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run tests)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run tests)
endif
ifeq ($(ANSWERS),)
	$(warning Answer file not specified, no checking will be done)
endif
	$(foreach target,$(TARGETS),$(call RUN_test_experiment,$(target)))

# Test data, approximate matching algorithms
test-approx-experiments:
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run tests)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run tests)
endif
ifeq ($(APPROX_ANSWERS),)
	$(warning Answer file not specified, no checking will be done)
endif
	$(foreach target,$(APPROX_TARGETS),$(call RUN_test_approx_experiment,$(target)))

# Run the full experiments (all data, etc.).
experiments: long-experiments short-experiments approx-experiments

# Full data, experiments that can only run a smaller number of iterations.
long-experiments:
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
	$(foreach target,$(LONG_TARGETS),$(call RUN_long_experiment,$(target)))

# Full data, experiments that can run the full number of iterations.
short-experiments:
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
	$(foreach target,$(SHORT_TARGETS),$(call RUN_experiment,$(target)))

# Full data, approximate matching experiments.
approx-experiments:
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
	$(foreach target,$(APPROX_TARGETS),\
		$(foreach k,$(K),\
			$(call RUN_long_approx_experiment,$(target) $(k))\
		)\
	)
