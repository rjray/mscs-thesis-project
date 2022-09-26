# This uses features of GNU Make 4.3, and might not work with older versions.

# The DATA_SEED value is used to control the randomness of the random_data.py
# script. The value isn't random to me, but don't worry about it.
DATA_SEED ?= 215377800

# Files and such
RANDOM_SEQUENCES := random-sequences.txt
RANDOM_PATTERNS := random-patterns.txt
RANDOM_ANSWERS := random-answers.txt
RANDOM_FILES := $(RANDOM_SEQUENCES) $(RANDOM_PATTERNS) $(RANDOM_ANSWERS)
TEST_SEQUENCES := test-random-sequences.txt
TEST_PATTERNS := test-random-patterns.txt
TEST_ANSWERS := test-random-answers.txt
TEST_FILES := $(TEST_SEQUENCES) $(TEST_PATTERNS) $(TEST_ANSWERS)
EXPERIMENTS_FILE := experiments_data.yml
RUNCOUNT := 10

# Tools.
RANDOM_DATA_PY := ./util/random_data.py
HARNESS := ./harness/harness

.PHONY: harness C Rust
all: harness C Rust

clean: clean-all

realclean: clean clean-data

clean-all: C-clean Rust-clean harness-clean

clean-data:
	$(RM) $(RANDOM_FILES) $(TEST_FILES)

data: random-data

all-data: testing-data random-data

testing-data: testing-random-data

random-data: $(RANDOM_FILES)

$(RANDOM_FILES) &: $(RANDOM_DATA_PY)
	$(RANDOM_DATA_PY) --seed $(DATA_SEED) --file $(RANDOM_SEQUENCES) \
		--patterns $(RANDOM_PATTERNS) --answers $(RANDOM_ANSWERS) \
		--line-variance 16 --pattern-variance 1

testing-random-data: $(TEST_FILES)

$(TEST_FILES) &: $(RANDOM_DATA_PY)
	$(RANDOM_DATA_PY) --seed $(DATA_SEED) --file $(TEST_SEQUENCES) \
		--patterns $(TEST_PATTERNS) --answers $(TEST_ANSWERS) --length 120 \
		--line-variance 4 --pattern-length 4 --pattern-variance 1 \
		--count 100 --pattern-count 10

C:
	$(MAKE) -C C all

C-clean:
	$(MAKE) -C C clean

Rust:
	$(MAKE) -C Rust all

Rust-clean:
	$(MAKE) -C Rust clean

harness:
	$(MAKE) -C harness all

harness-clean:
	$(MAKE) -C harness clean

experiments: data $(HARNESS)
	echo "# Experiments run:" $(shell date) > $(EXPERIMENTS_FILE)
	$(MAKE) -C C experiments \
		HARNESS=../$(HARNESS) \
		RUNCOUNT=$(RUNCOUNT) \
		EXPERIMENTS_FILE=../$(EXPERIMENTS_FILE) \
		SEQUENCES=../$(RANDOM_SEQUENCES) \
		PATTERNS=../$(RANDOM_PATTERNS) \
		ANSWERS=../$(RANDOM_ANSWERS)
	$(MAKE) -C Rust experiments \
		HARNESS=../$(HARNESS) \
		RUNCOUNT=$(RUNCOUNT) \
		EXPERIMENTS_FILE=../$(EXPERIMENTS_FILE) \
		SEQUENCES=../$(RANDOM_SEQUENCES) \
		PATTERNS=../$(RANDOM_PATTERNS) \
		ANSWERS=../$(RANDOM_ANSWERS)

test-experiments: testing-data C Rust
	$(MAKE) -C C test-experiments SEQUENCES=../$(TEST_SEQUENCES) \
		PATTERNS=../$(TEST_PATTERNS) ANSWERS=../$(TEST_ANSWERS)
	$(MAKE) -C Rust test-experiments SEQUENCES=../$(TEST_SEQUENCES) \
		PATTERNS=../$(TEST_PATTERNS) ANSWERS=../$(TEST_ANSWERS)
