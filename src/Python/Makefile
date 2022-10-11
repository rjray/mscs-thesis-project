include ../defines.mk

LONG_TARGETS := $(addprefix ./,$(addsuffix .py,$(LONG_ALGORITHMS)))
SHORT_TARGETS := $(addprefix ./,$(addsuffix .py,$(SHORT_ALGORITHMS)))
TARGETS := $(LONG_TARGETS) $(SHORT_TARGETS)

all: $(TARGETS)

clean:
	@echo "No clean-up needed in Python"

test-experiments:
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

experiments: long-experiments short-experiments

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
