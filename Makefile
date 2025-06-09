SH_FILES		:=		.githooks/*		\
					bin/setup		\
					bin/ssh-to-host

all: lint test

setup:
	./bin/setup

lint:
	prettier -c *-ts
	autopep8 --exclude venv --exit-code -d -r *-py
	shfmt -d $(SH_FILES)
	shellcheck -P .githooks $(SH_FILES)

test:

check: lint test

format:
	prettier -w *-ts
	autopep8 --exclude venv -i -r *-py
	shfmt -w .githooks/* $(SH_FILES)

.PHONY: setup lint test check format
