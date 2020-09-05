all: install-dev

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .
