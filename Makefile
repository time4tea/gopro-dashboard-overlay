
BIN=venv/bin

default: test

.PHONY: clean
clean:
	rm -rf dist

.PHONY: dist
dist:
	$(BIN)/python setup.py sdist

.PHONY: test
test:
	CI=true PYTHONPATH=. $(BIN)/pytest --capture sys --show-capture all tests

.PHONY: flake
flake:
	$(BIN)/flake8 gopro_overlay/ --count --select=E9,F63,F7,F82 --show-source --statistics
	$(BIN)/flake8 gopro_overlay/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

.PHONY: venv
venv:
	python -m venv venv

.PHONY: req
req:
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/pip install -r requirements-dev.txt


.PHONY: test-publish
test-publish: dist
	$(BIN)/pip install twine
	$(BIN)/twine check dist/*
	$(BIN)/twine upload --non-interactive --repository testpypi dist/*


.PHONY: publish
publish: clean dist
	$(BIN)/pip install twine
	$(BIN)/twine check dist/*
	$(BIN)/twine upload --skip-existing --non-interactive --repository pypi dist/*



.PHONY: bump
bump:
	$(BIN)/pip install bumpversion
	$(BIN)/bumpversion minor


.PHONY: help
help:
	PYTHONPATH=. $(BIN)/python bin/gopro-dashboard.py --help
