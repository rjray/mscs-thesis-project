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
RANDOM_APPROX_ANSWERS := random-answers-%d.txt
RANDOM_FILES := $(RANDOM_SEQUENCES) $(RANDOM_PATTERNS) $(RANDOM_ANSWERS)
TEST_SEQUENCES := test-random-sequences.txt
TEST_PATTERNS := test-random-patterns.txt
TEST_ANSWERS := test-random-answers.txt
TEST_APPROX_ANSWERS := test-random-answers-%d.txt
TEST_FILES := $(TEST_SEQUENCES) $(TEST_PATTERNS) $(TEST_ANSWERS)

# Value(s) of k for approximate matching:
K := 1 2 3 4 5
# Convert it to a comma-joined single string:
comma := ,
empty :=
space := $(empty) $(empty)
KS := $(subst $(space),$(comma),$(K))

EXPERIMENTS_FILE := experiments-data.yml

# The default number of runs that each experiment will do, when running for
# results. Note that the scripts (Perl and Python) override this for the longer
# algorithms (but not for the Aho-Corasick runs).
RUNCOUNT := 25
# The default number of runs that each "long" experiment will do, when running
# for results. The scripts (Perl and Python) use this for the longer algorithms
# (but not for the Aho-Corasick runs).
LONG_RUNCOUNT := 5
# The default number of runs that each approximate-matching experiment will do,
# when running for results. Note that the scripts (Perl and Python) override
# this for the longer algorithms with APPROX_LONG_RUNCOUNT.
APPROX_RUNCOUNT := 5
# And finally, the default number of runs that each approximate-matching
# experiment will make if they're known to be excessively-long (Perl and Python
# in this case). Python's dfa_gap with k=5 takes over 2 hours by itself.
APPROX_LONG_RUNCOUNT := 3

# The file to write valgrind results to for the `memcheck` rule, and a def for
# valgrind itself.
MEMCHECK_FILE := memcheck.txt
VALGRIND := valgrind

# Command and file for SLOC data:
SLOC := sloc
SLOC_FILE := sloc.csv

# Commands and values for the compression data:
COMPRESSION_DIR := compression
COMPRESSION_STATS := compression.txt
CLOC := cloc
XZ := xz

# Commands and values for the cyclomatic complexity data:
CYCLOMATIC_FILE_CSV := cyclomatic.csv
CYCLOMATIC_FILE_JSON := cyclomatic.json
CYCLOMATIC_FILE_YAML := cyclomatic.yaml
LIZARD := lizard
COUNTPERL := countperl
RUST_CODE_ANALYSIS_CLI := rust-code-analysis-cli

# The languages under inspection, and clean-targets for those that have them.
LANGUAGES := C Cpp Rust Perl Python
LANG_CLEAN := $(addsuffix -clean,$(LANGUAGES))
LANG_DIRS := C C++ Rust Perl Python

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

clean-all: harness-clean $(LANG_CLEAN) clean-images clean-tex clean-gen-data

reset: clean all

clean-images:
	$(RM) *.png

clean-tex:
	$(RM) *.tex

clean-gen-data:
	$(RM) $(SLOC_FILE) $(COMPRESSION_STATS) $(CYCLOMATIC_FILE_CSV) \
		$(CYCLOMATIC_FILE_JSON) $(CYCLOMATIC_FILE_YAML)

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
		ANSWERS=../$(RANDOM_ANSWERS) \
		APPROX_ANSWERS=../$(RANDOM_APPROX_ANSWERS)
	make -C C++ memcheck NO_INTEL=$(NO_INTEL) \
		VALGRIND=$(VALGRIND) \
		MEMCHECK_FILE=../$(MEMCHECK_FILE) \
		SEQUENCES=../$(RANDOM_SEQUENCES) \
		PATTERNS=../$(RANDOM_PATTERNS) \
		ANSWERS=../$(RANDOM_ANSWERS) \
		APPROX_ANSWERS=../$(RANDOM_APPROX_ANSWERS)
	make -C Rust memcheck VALGRIND=$(VALGRIND) \
		MEMCHECK_FILE=../$(MEMCHECK_FILE) \
		SEQUENCES=../$(RANDOM_SEQUENCES) \
		PATTERNS=../$(RANDOM_PATTERNS) \
		ANSWERS=../$(RANDOM_ANSWERS) \
		APPROX_ANSWERS=../$(RANDOM_APPROX_ANSWERS)
	echo "# Memory check completed:" `date` >> $(MEMCHECK_FILE)

# Rule to run all three of the expressiveness elements.
expressiveness-data: sloc-data cyclomatic-data compression-data

# A rule to create the SLOC data in CSV format.
sloc-data:
	find $(LANG_DIRS) \
		-name \*.[ch] -o -name \*.[ch]pp -o -name \*.p[lm] -o -name \*.py -o \
		-name \*.rs | sort | xargs $(SLOC) -f csv -d -a pm=pl > $(SLOC_FILE)

# Rule/action to determine the compression ratios
compression-data:
	@$(RM) -r $(COMPRESSION_DIR)
	mkdir -p $(COMPRESSION_DIR)
	@echo Copying source files to $(COMPRESSION_DIR).
	find $(LANG_DIRS) \
		-name \*.[ch] -o -name \*.[ch]pp -o -name \*.p[lm] -o -name \*.py -o \
		-name \*.rs | xargs tar cf - | (cd $(COMPRESSION_DIR) ; tar xf -)
	@echo Copying complete.
	@echo Removing external elements.
	$(RM) $(COMPRESSION_DIR)/C++/jpcre2.hpp
	@echo Done.
	@echo Stripping comments.
	$(CLOC) --original-dir --strip-comments=nc --report-file=/dev/null $(COMPRESSION_DIR)
	@echo Comment-removal done.
	@echo Removing original files.
	find compression -type f ! -name \*.nc -exec rm \{\} \;
	@echo Done.
	@echo Creating per-language text files.
	for lang in $(LANG_DIRS); do \
		(cd $(COMPRESSION_DIR) ; find $$lang -type f | xargs cat) > $(COMPRESSION_DIR)/$$lang.txt; \
	done
	@echo Text files complete.
	@echo Compressing and saving statistics.
	$(XZ) --lzma2=preset=9e,lc=4,pb=0 -k -v -f $(COMPRESSION_DIR)/*.txt 2>&1 | tee $(COMPRESSION_STATS)
	@echo Compression done.
	@echo Removing directory.
	$(RM) -r $(COMPRESSION_DIR)

# Rule/actions for calculating the cyclomatic complexity data
cyclomatic-data:
	$(LIZARD) --csv C C++ Python > $(CYCLOMATIC_FILE_CSV)
	$(COUNTPERL) --json Perl > $(CYCLOMATIC_FILE_JSON)
	$(RUST_CODE_ANALYSIS_CLI) -m -O yaml -p Rust > $(CYCLOMATIC_FILE_YAML)

# Rules relevant to the creation/cleaning of the data files:

clean-data:
	$(RM) $(RANDOM_FILES) $(TEST_FILES) *-answers-*.txt

data: random-data

all-data: testing-data random-data

testing-data: testing-random-data

random-data: $(RANDOM_FILES)

$(RANDOM_FILES) &: $(RANDOM_DATA_PY)
	$(RANDOM_DATA_PY) --seed $(DATA_SEED) --sequences $(RANDOM_SEQUENCES) \
		--patterns $(RANDOM_PATTERNS) --answers $(RANDOM_ANSWERS) \
		--approx-answers $(RANDOM_APPROX_ANSWERS) -k $(KS) \
		--sequence-length 1024 --sequence-variance 16 --pattern-length 9 \
		--pattern-variance 1 --sequence-count 100000 --pattern-count 100

testing-random-data: $(TEST_FILES)

$(TEST_FILES) &: $(RANDOM_DATA_PY)
	$(RANDOM_DATA_PY) --seed $(DATA_SEED) --sequences $(TEST_SEQUENCES) \
		--patterns $(TEST_PATTERNS) --answers $(TEST_ANSWERS) \
		--approx-answers $(TEST_APPROX_ANSWERS) -k $(KS) \
		--sequence-length 120 --sequence-variance 4 --pattern-length 4 \
		--pattern-variance 1 --sequence-count 100 --pattern-count 10

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

Perl-clean:
	$(MAKE) -C Perl clean

Python:
	$(MAKE) -C Python all

Python-clean:
	$(MAKE) -C Python clean

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
		LONG_RUNCOUNT=$(LONG_RUNCOUNT) \
		APPROX_RUNCOUNT=$(APPROX_RUNCOUNT) \
		APPROX_LONG_RUNCOUNT=$(APPROX_LONG_RUNCOUNT) \
		EXPERIMENTS_FILE=../$(EXPERIMENTS_FILE) \
		SEQUENCES=../$(RANDOM_SEQUENCES) \
		PATTERNS=../$(RANDOM_PATTERNS) \
		ANSWERS=../$(RANDOM_ANSWERS) \
		APPROX_ANSWERS=../$(RANDOM_APPROX_ANSWERS) \
		K="$(K)"
	$(MAKE) -C C++ experiments \
		NO_INTEL=$(NO_INTEL) \
		HARNESS=../$(HARNESS) \
		RUNCOUNT=$(RUNCOUNT) \
		LONG_RUNCOUNT=$(LONG_RUNCOUNT) \
		APPROX_RUNCOUNT=$(APPROX_RUNCOUNT) \
		APPROX_LONG_RUNCOUNT=$(APPROX_LONG_RUNCOUNT) \
		EXPERIMENTS_FILE=../$(EXPERIMENTS_FILE) \
		SEQUENCES=../$(RANDOM_SEQUENCES) \
		PATTERNS=../$(RANDOM_PATTERNS) \
		ANSWERS=../$(RANDOM_ANSWERS) \
		APPROX_ANSWERS=../$(RANDOM_APPROX_ANSWERS) \
		K="$(K)"
	$(MAKE) -C Rust experiments \
		HARNESS=../$(HARNESS) \
		RUNCOUNT=$(RUNCOUNT) \
		LONG_RUNCOUNT=$(LONG_RUNCOUNT) \
		APPROX_RUNCOUNT=$(APPROX_RUNCOUNT) \
		APPROX_LONG_RUNCOUNT=$(APPROX_LONG_RUNCOUNT) \
		EXPERIMENTS_FILE=../$(EXPERIMENTS_FILE) \
		SEQUENCES=../$(RANDOM_SEQUENCES) \
		PATTERNS=../$(RANDOM_PATTERNS) \
		ANSWERS=../$(RANDOM_ANSWERS) \
		APPROX_ANSWERS=../$(RANDOM_APPROX_ANSWERS) \
		K="$(K)"
	$(MAKE) -C Perl experiments \
		HARNESS=../$(HARNESS) \
		RUNCOUNT=$(RUNCOUNT) \
		LONG_RUNCOUNT=$(LONG_RUNCOUNT) \
		APPROX_RUNCOUNT=$(APPROX_RUNCOUNT) \
		APPROX_LONG_RUNCOUNT=$(APPROX_LONG_RUNCOUNT) \
		EXPERIMENTS_FILE=../$(EXPERIMENTS_FILE) \
		SEQUENCES=../$(RANDOM_SEQUENCES) \
		PATTERNS=../$(RANDOM_PATTERNS) \
		ANSWERS=../$(RANDOM_ANSWERS) \
		APPROX_ANSWERS=../$(RANDOM_APPROX_ANSWERS) \
		K="$(K)"
	$(MAKE) -C Python experiments \
		HARNESS=../$(HARNESS) \
		RUNCOUNT=$(RUNCOUNT) \
		LONG_RUNCOUNT=$(LONG_RUNCOUNT) \
		APPROX_RUNCOUNT=$(APPROX_RUNCOUNT) \
		APPROX_LONG_RUNCOUNT=$(APPROX_LONG_RUNCOUNT) \
		EXPERIMENTS_FILE=../$(EXPERIMENTS_FILE) \
		SEQUENCES=../$(RANDOM_SEQUENCES) \
		PATTERNS=../$(RANDOM_PATTERNS) \
		ANSWERS=../$(RANDOM_ANSWERS) \
		APPROX_ANSWERS=../$(RANDOM_APPROX_ANSWERS) \
		K="$(K)"
	@echo "# Experiments completed:" `date` >> $(EXPERIMENTS_FILE)

test-experiments: testing-data C Rust
	$(MAKE) -C C test-experiments NO_INTEL=$(NO_INTEL) \
		SEQUENCES=../$(TEST_SEQUENCES) PATTERNS=../$(TEST_PATTERNS) \
		ANSWERS=../$(TEST_ANSWERS) APPROX_ANSWERS=../$(TEST_APPROX_ANSWERS) \
		K="1 2"
	$(MAKE) -C C++ test-experiments NO_INTEL=$(NO_INTEL) \
		SEQUENCES=../$(TEST_SEQUENCES) PATTERNS=../$(TEST_PATTERNS) \
		ANSWERS=../$(TEST_ANSWERS) APPROX_ANSWERS=../$(TEST_APPROX_ANSWERS) \
		K="1 2"
	$(MAKE) -C Rust test-experiments SEQUENCES=../$(TEST_SEQUENCES) \
		PATTERNS=../$(TEST_PATTERNS) ANSWERS=../$(TEST_ANSWERS) \
		APPROX_ANSWERS=../$(TEST_APPROX_ANSWERS) K="1 2"
	$(MAKE) -C Perl test-experiments SEQUENCES=../$(TEST_SEQUENCES) \
		PATTERNS=../$(TEST_PATTERNS) ANSWERS=../$(TEST_ANSWERS) \
		APPROX_ANSWERS=../$(TEST_APPROX_ANSWERS) K="1 2"
	$(MAKE) -C Python test-experiments SEQUENCES=../$(TEST_SEQUENCES) \
		PATTERNS=../$(TEST_PATTERNS) ANSWERS=../$(TEST_ANSWERS) \
		APPROX_ANSWERS=../$(TEST_APPROX_ANSWERS) K="1 2"
