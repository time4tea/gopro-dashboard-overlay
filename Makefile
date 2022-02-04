
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
	TEST=true PYTHONPATH=. $(BIN)/pytest --capture sys --show-capture all tests

.PHONY: ci
ci:
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


DIST_TEST=$(realpath tmp/dist-test)
CURRENT_VERSION=$(shell PYTHONPATH=. python3 -c 'import gopro_overlay.__version__;print(gopro_overlay.__version__.__version__)')

.PHONY: version
version:
	@echo $(CURRENT_VERSION)

.PHONY:
test-distribution: dist
	@echo "Current Version is $(CURRENT_VERSION)"
	rm -rf $(DIST_TEST)
	python3 -m venv $(DIST_TEST)/venv
	$(DIST_TEST)/venv/bin/pip install wheel dist/gopro-overlay-$(CURRENT_VERSION).tar.gz
	DISTRIBUTION=$(DIST_TEST)/venv $(BIN)/pytest --capture sys --show-capture all tests-dist


.PHONY: publish
publish: clean test-distribution
	$(BIN)/pip install twine
	$(BIN)/twine check dist/*
	$(BIN)/twine upload --skip-existing --non-interactive --repository pypi dist/*
	git tag v$(CURRENT_VERSION)


.PHONY: bump
bump:
	$(BIN)/pip install bumpversion
	$(BIN)/bumpversion minor


.PHONY: help
help:
	PYTHONPATH=. $(BIN)/python bin/gopro-dashboard.py --help
	PYTHONPATH=. $(BIN)/python bin/gopro-join.py --help