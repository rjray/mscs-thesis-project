# This is the main Makefile for the experiments part of the thesis work.
#
# This controls the building and running of the experiments, as well as the
# harness program that runs each experiment and records energy and memory
# usage.
#
#     `make all` will build everything
#
#     `make experiments` will run the full suite of experiments as was done for
#     the thesis
#
#     `make clean` will clean everything, including any PNG or TeX files that
#     are present from the utils/process_results.py script (it will not remove
#     the data file, as those can be harder to generate)
#
#     `make realclean` will clean everything, including the data files
#
# See the README.md file in this directory for more information.

# This uses features of GNU Make 4.3, and might not work with older versions.

# The DATA_SEED value is used to control the randomness of the random_data.py
# script. The value isn't random to me, but don't worry about it.
DATA_SEED ?= 215377800

# Files and such. The RANDOM_* definitions are the files used for actual data
# gathering runs. The TEST_* definitions are much much smaller and used for
# basic testing of changes for sanity, etc. The EXPERIMENTS_FILE definition is
# the file that `harness` will write all of the gathered data to during a data-
# gathering run.
RANDOM_SEQUENCES := random-sequences.txt
RANDOM_PATTERNS := random-patterns.txt
RANDOM_ANSWERS := random-answers.txt
RANDOM_FILES := $(RANDOM_SEQUENCES) $(RANDOM_PATTERNS) $(RANDOM_ANSWERS)
TEST_SEQUENCES := test-random-sequences.txt
TEST_PATTERNS := test-random-patterns.txt
TEST_ANSWERS := test-random-answers.txt
TEST_FILES := $(TEST_SEQUENCES) $(TEST_PATTERNS) $(TEST_ANSWERS)

EXPERIMENTS_FILE := experiments_data.yml

# The default number of runs that each experiment will do, when running for
# results. Note that the scripts (Perl and Python) override this for the longer
# algorithms (but not for the Aho-Corasick runs).
RUNCOUNT := 25

# The file to write valgrind results to for the `memcheck` rule, and a def for
# valgrind itself.
MEMCHECK_FILE := memcheck.txt
VALGRIND := valgrind

# The languages under inspection, and clean-targets for those that have them.
LANGUAGES := C Cpp Rust Perl Python
LANG_CLEAN := C-clean Cpp-clean Rust-clean

# Tools.
RANDOM_DATA_PY := ./util/random_data.py
HARNESS := ./harness/harness

# This is used to opt-out of using the Intel toolchain. Set it to something
# non-null if you don't have the icx/icpx compilers, or simply done't want to
# use them in the data-gathering. Default this to unset here so that it can be
# passed down where needed.
NO_INTEL=

# Rule to build everything. Includes Perl and Python directories, even though
# they currently have no actions for the "all" target.
.PHONY: harness $(LANGUAGES)
all: harness $(LANGUAGES)

# Clean-up rules. Note that data files are not cleaned unless "realclean" is
# given.
clean: clean-all

realclean: clean clean-data

clean-all: harness-clean $(LANG_CLEAN) clean-images clean-tex

reset: clean all

clean-images:
	$(RM) *.png

clean-tex:
	$(RM) *.tex

# A rule to run valgrind over all the compiled code to ensure that no memory
# leaks have been introduced.

memcheck:
	echo "# Running on host:" `hostname` > $(MEMCHECK_FILE)
	echo "# Memory check started:" `date` >> $(MEMCHECK_FILE)
	make -C C memcheck NO_INTEL=$(NO_INTEL) \
		VALGRIND=$(VALGRIND) \
		MEMCHECK_FILE=../$(MEMCHECK_FILE) \
		SEQUENCES=../$(RANDOM_SEQUENCES) \
		PATTERNS=../$(RANDOM_PATTERNS) \
		ANSWERS=../$(RANDOM_ANSWERS)
	make -C C++ memcheck NO_INTEL=$(NO_INTEL) \
		VALGRIND=$(VALGRIND) \
		MEMCHECK_FILE=../$(MEMCHECK_FILE) \
		SEQUENCES=../$(RANDOM_SEQUENCES) \
		PATTERNS=../$(RANDOM_PATTERNS) \
		ANSWERS=../$(RANDOM_ANSWERS)
	make -C Rust memcheck VALGRIND=$(VALGRIND) \
		MEMCHECK_FILE=../$(MEMCHECK_FILE) \
		SEQUENCES=../$(RANDOM_SEQUENCES) \
		PATTERNS=../$(RANDOM_PATTERNS) \
		ANSWERS=../$(RANDOM_ANSWERS)
	echo "# Memory check completed:" `date` >> $(MEMCHECK_FILE)

# Rules relevant to the creation/cleaning of the data files:

clean-data:
	$(RM) $(RANDOM_FILES) $(TEST_FILES)

data: random-data

all-data: testing-data random-data

testing-data: testing-random-data

random-data: $(RANDOM_FILES)

$(RANDOM_FILES) &: $(RANDOM_DATA_PY)
	$(RANDOM_DATA_PY) --seed $(DATA_SEED) --file $(RANDOM_SEQUENCES) \
		--patterns $(RANDOM_PATTERNS) --answers $(RANDOM_ANSWERS) \
		--length 1024 --line-variance 16 --pattern-length 9 \
		--pattern-variance 1 --count 100000 --pattern-count 100

testing-random-data: $(TEST_FILES)

$(TEST_FILES) &: $(RANDOM_DATA_PY)
	$(RANDOM_DATA_PY) --seed $(DATA_SEED) --file $(TEST_SEQUENCES) \
		--patterns $(TEST_PATTERNS) --answers $(TEST_ANSWERS) --length 120 \
		--line-variance 4 --pattern-length 4 --pattern-variance 1 \
		--count 100 --pattern-count 10

# Rules for the descent into subdirectories to propagate the all and clean
# targets.

C:
	$(MAKE) -C C all NO_INTEL=$(NO_INTEL)

C-clean:
	$(MAKE) -C C clean NO_INTEL=$(NO_INTEL)

Cpp:
	$(MAKE) -C C++ all NO_INTEL=$(NO_INTEL)

Cpp-clean:
	$(MAKE) -C C++ clean NO_INTEL=$(NO_INTEL)

Rust:
	$(MAKE) -C Rust all

Rust-clean:
	$(MAKE) -C Rust clean

Perl:
	$(MAKE) -C Perl all

Python:
	$(MAKE) -C Python all

harness:
	$(MAKE) -C harness all

harness-clean:
	$(MAKE) -C harness clean

# The two types of experiment runs: full (experiments) and testing
# (test-experiments).

experiments: data $(HARNESS)
	@echo "# Running on host:" `hostname` > $(EXPERIMENTS_FILE)
	@echo "#" >> $(EXPERIMENTS_FILE)
	@$(HARNESS) -i | sed -e 's/^/# /' >> $(EXPERIMENTS_FILE)
	@echo "# Experiments started:" `date` >> $(EXPERIMENTS_FILE)
	$(MAKE) -C C experiments \
		NO_INTEL=$(NO_INTEL) \
		HARNESS=../$(HARNESS) \
		RUNCOUNT=$(RUNCOUNT) \
		EXPERIMENTS_FILE=../$(EXPERIMENTS_FILE) \
		SEQUENCES=../$(RANDOM_SEQUENCES) \
		PATTERNS=../$(RANDOM_PATTERNS) \
		ANSWERS=../$(RANDOM_ANSWERS)
	$(MAKE) -C C++ experiments \
		NO_INTEL=$(NO_INTEL) \
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
	$(MAKE) -C Perl experiments \
		HARNESS=../$(HARNESS) \
		RUNCOUNT=$(RUNCOUNT) \
		EXPERIMENTS_FILE=../$(EXPERIMENTS_FILE) \
		SEQUENCES=../$(RANDOM_SEQUENCES) \
		PATTERNS=../$(RANDOM_PATTERNS) \
		ANSWERS=../$(RANDOM_ANSWERS)
	$(MAKE) -C Python experiments \
		HARNESS=../$(HARNESS) \
		RUNCOUNT=$(RUNCOUNT) \
		EXPERIMENTS_FILE=../$(EXPERIMENTS_FILE) \
		SEQUENCES=../$(RANDOM_SEQUENCES) \
		PATTERNS=../$(RANDOM_PATTERNS) \
		ANSWERS=../$(RANDOM_ANSWERS)
	@echo "# Experiments completed:" `date` >> $(EXPERIMENTS_FILE)

test-experiments: testing-data C Rust
	$(MAKE) -C C test-experiments NO_INTEL=$(NO_INTEL) \
		SEQUENCES=../$(TEST_SEQUENCES) PATTERNS=../$(TEST_PATTERNS) \
		ANSWERS=../$(TEST_ANSWERS)
	$(MAKE) -C C++ test-experiments NO_INTEL=$(NO_INTEL) \
		SEQUENCES=../$(TEST_SEQUENCES) PATTERNS=../$(TEST_PATTERNS) \
		ANSWERS=../$(TEST_ANSWERS)
	$(MAKE) -C Rust test-experiments SEQUENCES=../$(TEST_SEQUENCES) \
		PATTERNS=../$(TEST_PATTERNS) ANSWERS=../$(TEST_ANSWERS)
	$(MAKE) -C Perl test-experiments SEQUENCES=../$(TEST_SEQUENCES) \
		PATTERNS=../$(TEST_PATTERNS) ANSWERS=../$(TEST_ANSWERS)
	$(MAKE) -C Python test-experiments SEQUENCES=../$(TEST_SEQUENCES) \
		PATTERNS=../$(TEST_PATTERNS) ANSWERS=../$(TEST_ANSWERS)
