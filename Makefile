.PHONY: lint

lint:
	shfmt -d .githooks/*
	shellcheck -P .githooks .githooks/*
	yarn eslint

check: lint

format:
	shfmt -w .githooks/* ./bin/check-env

clean:
	rm -f .env-checked


.env-checked: bin/check-env
	./bin/check-env
	touch .env-checked

include .env-checked
