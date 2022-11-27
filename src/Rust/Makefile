# This is the Makefile for the Rust implementation of the algorithms.
#
# It's rather shorter than the C or C++ ones, as `cargo` handles the great
# majority of the work here.
#
# This is mainly to define the targets themselves and control the running of
# the experiments.

include ../defines.mk

# Get the list of source code files, needed to let the "all" target properly
# trigger `cargo`.
SOURCE := $(addsuffix /src/main.rs,$(ALGORITHMS))
SOURCE += $(wildcard common/src/*.rs)

# Default this to unset
DEBUG=

# Set up PATHTYPE, TARGETS, etc. based on DEBUG:
ifeq ($(DEBUG),)
PATHTYPE=release
CARGOFLAGS += --release
TARGETS := $(addprefix ./target/release/,$(ALGORITHMS))
APPROX_TARGETS := $(addprefix ./target/release/,$(APPROX_ALGORITHMS))
else
PATHTYPE=debug
TARGETS := $(addprefix ./target/debug/,$(ALGORITHMS))
APPROX_TARGETS := $(addprefix ./target/debug/,$(APPROX_ALGORITHMS))
endif

# This tool does most of the work:
CARGO := cargo

all: $(TARGETS) $(APPROX_TARGETS)

clean:
	$(CARGO) clean

$(TARGETS) $(APPROX_TARGETS) &: $(SOURCE)
	$(CARGO) build $(CARGOFLAGS)

# Run the experiments on the test-level data.
test-experiments: test-exact-experiments test-approx-experiments

# Run the full experiments (all data, etc.).
experiments: exact-experiments approx-experiments

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

# Full data, exact matching algorithms.
exact-experiments:
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
	$(foreach target,$(TARGETS),$(call RUN_experiment,$(target)))

# Full data, approximate matching algorithms
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
			$(call RUN_approx_experiment,$(target) $(k))\
		)\
	)
