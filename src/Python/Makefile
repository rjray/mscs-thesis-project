include ../defines.mk

LONG_TARGETS := $(addprefix ./,$(addsuffix .py,$(LONG_ALGORITHMS)))
SHORT_TARGETS := $(addprefix ./,$(addsuffix .py,$(SHORT_ALGORITHMS)))
APPROX_TARGETS := $(addprefix ./,$(addsuffix .py,$(APPROX_ALGORITHMS)))
TARGETS := $(LONG_TARGETS) $(SHORT_TARGETS) $(APPROX_TARGETS)

all: $(TARGETS)

clean:
	@echo "No clean-up needed in Python"

test-experiments: test-exact-experiments test-approx-experiments

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

experiments: long-experiments short-experiments approx-experiments

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
