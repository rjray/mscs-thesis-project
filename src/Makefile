# The DATA_SEED value is used to control the randomness of the random_data.py
# script. The value isn't random to me, but don't worry about it.
DATA_SEED ?= 215377800

# Files and such
RANDOM_SEQUENCES := sequences-random.txt
RANDOM_PATTERNS := patterns-random.txt
RANDOM_ANSWERS := answers-random.txt

# Tools.
RANDOM_DATA := ./util/random_data.py

all:

clean: clean-all

clean-all: clean-data

clean-data:
	$(RM) $(RANDOM_PATTERNS) $(RANDOM_SEQUENCES) $(RANDOM_ANSWERS)

data: random-data

random-data: $(RANDOM_DATA)
	$(RANDOM_DATA) --seed $(DATA_SEED) --file $(RANDOM_SEQUENCES) \
		--patterns $(RANDOM_PATTERNS) --answers $(RANDOM_ANSWERS) \
		--line-variance 16 --pattern-variance 1
