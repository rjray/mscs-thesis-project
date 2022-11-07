# Shared elements between languages' Makefiles

ALGORITHMS := kmp boyer_moore shift_or aho_corasick
LONG_ALGORITHMS := kmp boyer_moore shift_or
SHORT_ALGORITHMS := aho_corasick
APPROX_ALGORITHMS := dfa_gap regexp

# Default the run-count values, in case they aren't explicitly passed in.
ifeq ($(RUNCOUNT),)
RUNCOUNT := 10
endif
ifeq ($(LONG_RUNCOUNT),)
LONG_RUNCOUNT := 3
endif
ifeq ($(APPROX_RUNCOUNT),)
APPROX_RUNCOUNT := 5
endif
ifeq ($(APPROX_LONG_RUNCOUNT),)
APPROX_LONG_RUNCOUNT := 1
endif

# Macros for running the experiments. One set for testing and one set for real.
define RUN_test_experiment
@$(1) $(SEQUENCES) $(PATTERNS) $(ANSWERS)

endef
define RUN_test_approx_experiment
@$(1) 1 $(SEQUENCES) $(PATTERNS) $(APPROX_ANSWERS)

endef

define RUN_experiment
@$(HARNESS) -v -n $(RUNCOUNT) -f $(EXPERIMENTS_FILE) $(1) $(SEQUENCES) $(PATTERNS) $(ANSWERS)

endef
define RUN_long_experiment
@$(HARNESS) -v -s -n $(LONG_RUNCOUNT) -f $(EXPERIMENTS_FILE) $(1) $(SEQUENCES) $(PATTERNS) $(ANSWERS)

endef
define RUN_approx_experiment
@$(HARNESS) -v -s -n $(APPROX_RUNCOUNT) -f $(EXPERIMENTS_FILE) $(1) $(2) $(SEQUENCES) $(PATTERNS) $(APPROX_ANSWERS)

endef
define RUN_long_approx_experiment
@$(HARNESS) -v -s -n $(APPROX_LONG_RUNCOUNT) -f $(EXPERIMENTS_FILE) $(1) $(2) $(SEQUENCES) $(PATTERNS) $(APPROX_ANSWERS)

endef

# Macro for running an experiment instance under valgrind.
define RUN_memcheck
$(VALGRIND) $(1) $(SEQUENCES) $(PATTERNS) $(ANSWERS) 1>/dev/null 2>>$(MEMCHECK_FILE)
@echo >> $(MEMCHECK_FILE)

endef
define RUN_approx_memcheck
$(VALGRIND) $(1) 1 $(SEQUENCES) $(PATTERNS) $(APPROX_ANSWERS) 1>/dev/null 2>>$(MEMCHECK_FILE)
@echo >> $(MEMCHECK_FILE)

endef

# Rule to run memory checking:
memcheck: memcheck-exact memcheck-approx

memcheck-exact: $(TARGETS)
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run memcheck)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run memcheck)
endif
ifeq ($(ANSWERS),)
	$(warning Answer file not specified, no checking will be done)
endif
	$(foreach target,$(TARGETS),$(call RUN_memcheck,$(target)))

memcheck-approx: $(APPROX_TARGETS)
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run memcheck)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run memcheck)
endif
ifeq ($(APPROX_ANSWERS),)
	$(warning Answer file not specified, no checking will be done)
endif
	$(foreach target,$(APPROX_TARGETS),$(call RUN_approx_memcheck,$(target)))
