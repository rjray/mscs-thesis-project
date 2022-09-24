# Shared elements between languages' Makefiles

ALGORITHMS := kmp boyer_moore shift_or aho_corasick

define RUN_test_experiment
@$(1) $(SEQUENCES) $(PATTERNS) $(ANSWERS)

endef
define RUN_experiment
@$(HARNESS) -n $(RUNCOUNT) $(1) $(SEQUENCES) $(PATTERNS) $(ANSWERS)

endef
