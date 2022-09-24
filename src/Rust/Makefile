ALGORITHMS := kmp boyer_moore shift_or aho_corasick
SOURCE := $(addsuffix /src/main.rs,$(ALGORITHMS))
SOURCE += $(wildcard common/src/*.rs)

# Default this to unset
DEBUG=

# Set up PATHTYPE, TARGETS, etc. based on DEBUG:
ifeq ($(DEBUG),)
PATHTYPE=debug
TARGETS := $(addprefix target/debug/,$(ALGORITHMS))
else
PATHTYPE=release
CARGOFLAGS += --release
TARGETS := $(addprefix target/release/,$(ALGORITHMS))
endif

ifeq ($(RUNCOUNT),)
RUNCOUNT := 10
endif

CARGO := cargo

all: $(TARGETS)

$(TARGETS) &: $(SOURCE)
	$(CARGO) build $(CARGOFLAGS)

test-experiments: $(TARGETS)
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run tests)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run tests)
endif
ifeq ($(ANSWERS),)
	$(warning Answer file not specified, no checking will be done)
endif
	@./target/$(PATHTYPE)/kmp $(SEQUENCES) $(PATTERNS) $(ANSWERS)
	@./target/$(PATHTYPE)/boyer_moore $(SEQUENCES) $(PATTERNS) $(ANSWERS)
	@./target/$(PATHTYPE)/shift_or $(SEQUENCES) $(PATTERNS) $(ANSWERS)
	@./target/$(PATHTYPE)/aho_corasick $(SEQUENCES) $(PATTERNS) $(ANSWERS)

experiments: $(TARGETS)
ifeq ($(HARNESS),)
	$(error Harness not specified, cannot run experiments)
endif
ifeq ($(SEQUENCES),)
	$(error Sequences file not specified, cannot run experiments)
endif
ifeq ($(PATTERNS),)
	$(error Patterns file not specified, cannot run experiments)
endif
ifeq ($(ANSWERS),)
	$(warning Answers file not specified, no checking will be done)
endif
	@$(HARNESS) -n $(RUNCOUNT) ./target/$(PATHTYPE)/kmp $(SEQUENCES) $(PATTERNS) $(ANSWERS)
	@$(HARNESS) -n $(RUNCOUNT) ./target/$(PATHTYPE)/boyer_moore $(SEQUENCES) $(PATTERNS) $(ANSWERS)
	@$(HARNESS) -n $(RUNCOUNT) ./target/$(PATHTYPE)/shift_or $(SEQUENCES) $(PATTERNS) $(ANSWERS)
	@$(HARNESS) -n $(RUNCOUNT) ./target/$(PATHTYPE)/aho_corasick $(SEQUENCES) $(PATTERNS) $(ANSWERS)
