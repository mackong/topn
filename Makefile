SHELL?=bash
PYTHON?=python3
CC?=gcc

.PHONY: all

all: test

data:
	@$(SHELL) gendata.sh

time33:
	@cd wip && $(PYTHON) setup.py install

uring:
	@cd wip && $(CC) -g -Wall -O2 -o uring uring.c -luring

test:
	@$(PYTHON) topn.py

run:
	@sudo cgcreate -g memory:topn
	@sudo cgset -r memory.limit_in_bytes=1073741824 topn
	@sudo cgexec -g memory:topn $(PYTHON) topn.py urls.txt
	@sudo cgdelete memory:topn
