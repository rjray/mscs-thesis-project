# Shared elements between languages' Makefiles

ALGORITHMS := kmp boyer_moore shift_or aho_corasick

define RUN_test_experiment
@$(1) $(SEQUENCES) $(PATTERNS) $(ANSWERS)

endef
define RUN_experiment
@$(HARNESS) -v -n $(RUNCOUNT) -f $(EXPERIMENTS_FILE) $(1) $(SEQUENCES) $(PATTERNS) $(ANSWERS)

endef
