TS_DIRS := $(shell find . -maxdepth 1 -type d -name "*-ts" -exec sh -c 'ls "$$1"/*.ts >/dev/null 2>&1 && basename "$$1"' _ {} \;)

.PHONY: lint

lint:
	./bin/check-env
	shfmt -d .githooks/*
	shellcheck -P .githooks .githooks/* bin/check-env
	npx eslint

check: lint

format:
	shfmt -w .githooks/* ./bin/check-env

clean:
	rm -f .env-checked	

.env-checked: bin/check-env
	./bin/check-env
	touch .env-checked

include .env-checked
