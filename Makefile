define USAGE
Super awesome hand-crafted build system ⚙️

Commands:
	install		Install package and dependencies
	test		Run tests.
endef

export USAGE
help:
	@echo "$$USAGE"

init:
	pip3 install .

test:
	python -m unittest discover ./tests/
