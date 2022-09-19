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

# Tools.
RANDOM_DATA_PY := ./util/random_data.py

all: C

clean: clean-all

clean-all: clean-data C-clean

clean-data:
	$(RM) $(RANDOM_FILES) $(TEST_FILES)

data: random-data

testing-data: testing-random-data

random-data: $(RANDOM_DATA_PY) $(RANDOM_FILES)
	$(RANDOM_DATA_PY) --seed $(DATA_SEED) --file $(RANDOM_SEQUENCES) \
		--patterns $(RANDOM_PATTERNS) --answers $(RANDOM_ANSWERS) \
		--line-variance 16 --pattern-variance 1

testing-random-data: $(RANDOM_DATA_PY) $(TEST_FILES)
	$(RANDOM_DATA_PY) --seed $(DATA_SEED) --file $(TEST_SEQUENCES) \
		--patterns $(TEST_PATTERNS) --answers $(TEST_ANSWERS) --length 120 \
		--line-variance 4 --pattern-length 4 --pattern-variance 1 \
		--count 100 --pattern-count 10

C:
	make -C C all

C-clean:
	make -C C clean
