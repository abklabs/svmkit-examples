TS_DIRS := $(shell find . -maxdepth 1 -type d -name "*-ts" -exec sh -c 'ls "$$1"/*.ts >/dev/null 2>&1 && basename "$$1"' _ {} \;)

.PHONY: lint

lint:
	shfmt -d .githooks/*
	shellcheck -P .githooks .githooks/* 
	@for dir in $(TS_DIRS); do \
		echo "Linting $$dir..."; \
		npx eslint $$dir --config eslint.config.mjs; \
	done

check: lint

format:
	shfmt -w .githooks/* ./bin/check-env


