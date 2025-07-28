.PHONY: lint

lint:
	shfmt -d .githooks/*
	shellcheck -P .githooks .githooks/*
	yarn eslint

check: lint

format:
	shfmt -w .githooks/* ./bin/check-env
