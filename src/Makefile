# The DATA_SEED value is used to control the randomness of the random_data.py
# script. The value is my wife's birthdate and time.
DATA_SEED ?= $(shell TZ=America/Los_Angeles date '+%s' --date "1976-10-28 12:10:00 -7:00")

# Files and such
RANDOM_SEQUENCES := sequences-random.txt
RANDOM_PATTERNS := patterns-random.txt

# Tools.
RANDOM_DATA := ./util/random_data.py

all:

clean: clean-all

clean-all: clean-data

clean-data:
	$(RM) $(RANDOM_PATTERNS) $(RANDOM_SEQUENCES)

data: random_data

random_data: $(RANDOM_DATA)
	$(RANDOM_DATA) --seed $(DATA_SEED) --file $(RANDOM_SEQUENCES) \
		--patterns $(RANDOM_PATTERNS) --line-variance 16 --pattern-variance 1
