
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

.PHONY: check
check:
	CI=true PYTHONPATH=. $(BIN)/pytest --capture sys --show-capture all -m "not gfx"  tests

.PHONY: check-gfx
check-gfx:
	PYTHONPATH=. $(BIN)/pytest --capture sys --show-capture all -m "gfx"  tests

.PHONY: check-cairo
check-cairo:
	PYTHONPATH=. $(BIN)/pytest --capture sys --show-capture all -m "cairo"  tests


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


.PHONY: test-distribution-install
test-distribution-install: dist
	@echo "Current Version is $(CURRENT_VERSION)"
	rm -rf $(DIST_TEST)
	python3 -m venv $(DIST_TEST)/venv
	$(DIST_TEST)/venv/bin/pip install wheel dist/gopro-overlay-$(CURRENT_VERSION).tar.gz

.PHONY: test-distribution-test
test-distribution-test:
	DISTRIBUTION=$(DIST_TEST)/venv $(BIN)/pytest --capture sys --show-capture all tests-dist

.PHONY: test-distribution
test-distribution: test-distribution-install test-distribution-test


.PHONY: ensure-not-released
ensure-not-released:
	build-scripts/ensure-version-not-released.sh $(CURRENT_VERSION)


.PHONY: ensure-pristine
ensure-pristine:
	build-scripts/ensure-working-directory-clean.sh


.PHONY: doc-examples
doc-examples:
	PYTHONPATH=. $(BIN)/python3 build-scripts/generate-examples.py

.PHONY: doc-map-examples
doc-map-examples:
	PYTHONPATH=. $(BIN)/python3 build-scripts/generate-map-examples.py

.PHONY: doc
doc: doc-examples doc-map-examples


.PHONY: publish
publish: ensure-not-released ensure-pristine clean test-distribution
	$(BIN)/pip install twine
	$(BIN)/twine check dist/*
	$(BIN)/twine upload --skip-existing --non-interactive --repository pypi dist/*
	git tag v$(CURRENT_VERSION)


.PHONY: bump
bump:
	$(BIN)/pip install bumpversion
	$(BIN)/bumpversion minor

.PHONY: bump-major
bump-major:
	$(BIN)/pip install bumpversion
	$(BIN)/bumpversion major


.PHONY: help
help:
	PYTHONPATH=. $(BIN)/python bin/gopro-contrib-data-extract.py --help
	PYTHONPATH=. $(BIN)/python bin/gopro-cut.py --help
	PYTHONPATH=. $(BIN)/python bin/gopro-dashboard.py --help
	PYTHONPATH=. $(BIN)/python bin/gopro-extract.py --help
	PYTHONPATH=. $(BIN)/python bin/gopro-join.py --help
	PYTHONPATH=. $(BIN)/python bin/gopro-rename.py --help
	PYTHONPATH=. $(BIN)/python bin/gopro-to-csv.py --help
	PYTHONPATH=. $(BIN)/python bin/gopro-to-gpx.py --help
