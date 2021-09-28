
BIN=venv/bin

default: test

.PHONY: dist
dist:
	$(BIN)/python setup.py sdist

.PHONY: test
test:
	PYTHONPATH=. $(BIN)/pytest tests

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
test-publish:
	$(BIN)/pip install twine
	$(BIN)/twine check dist/*
	$(BIN)/twine upload --repository-url https://test.pypi.org/legacy/ dist/*


.PHONY: publish
publish:
	$(BIN)/pip install twine
	$(BIN)/twine upload dist/*


.PHONY: bump
bump:
	$(BIN)/pip install bumpversion
	$(BIN)/bumpversion minor