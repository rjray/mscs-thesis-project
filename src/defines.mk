# Shared elements between languages' Makefiles

ALGORITHMS := kmp boyer_moore shift_or aho_corasick
LONG_ALGORITHMS := kmp boyer_moore shift_or
SHORT_ALGORITHMS := aho_corasick

# Default the run-count values, in case they aren't explicitly passed in.
ifeq ($(RUNCOUNT),)
RUNCOUNT := 10
endif
ifeq ($(LONG_RUNCOUNT),)
LONG_RUNCOUNT := 5
endif

# Macros for running the experiments. One for testing and one for real.
define RUN_test_experiment
@$(1) $(SEQUENCES) $(PATTERNS) $(ANSWERS)

endef
define RUN_experiment
@$(HARNESS) -v -n $(RUNCOUNT) -f $(EXPERIMENTS_FILE) $(1) $(SEQUENCES) $(PATTERNS) $(ANSWERS)

endef

define RUN_long_experiment
@$(HARNESS) -v -s -n $(LONG_RUNCOUNT) -f $(EXPERIMENTS_FILE) $(1) $(SEQUENCES) $(PATTERNS) $(ANSWERS)

endef

# Macro for running an experiment instance under valgrind.
define RUN_memcheck
$(VALGRIND) $(1) $(SEQUENCES) $(PATTERNS) $(ANSWERS) 1>/dev/null 2>>$(MEMCHECK_FILE)
@echo >> $(MEMCHECK_FILE)

endef

# Rule to run memory checking:
memcheck: $(TARGETS)
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
