SHELL=bash
PYTHON=python3

.PHONY: all

all: test

data:
	@$(SHELL) gendata.sh

test:
	@$(PYTHON) topn.py

run:
	@sudo cgcreate -g memory:topn
	@sudo cgset -r memory.limit_in_bytes=1073741824 topn
	@sudo cgexec -g memory:topn $(PYTHON) topn.py urls.py
	@sudo cgdelete memory:topn
