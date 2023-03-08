#
# This Makefile is used to manage development and distribution.
#
# Created: 2022-08-01
# Updated: 2022-08-31
#

.PHONY: build create-venv help prebuild publish test update-venv

help:
	@echo "Usage: make [<target>]"
	@echo
	@echo "General Targets:"
	@echo "  help      Display this help message."
	@echo
	@echo "Distribution Targets:"
	@echo "  build     Build the package."
	@echo "  prebuild  Generate files used by distribution."
	@echo "  publish   Publish the package to PyPI."
	@echo
	@echo "Development Targets:"
	@echo "  create-venv  Create the development Python virtual environment."
	@echo "  test         Run tests using Tox."
	@echo "  update-venv  Update the development Python virtual environment."

build: dist-build

create-venv: dev-venv-create

prebuild: dist-prebuild

publish: dist-publish

test: dev-test

update-venv: dev-venv-install


################################################################################
# Development
################################################################################

SRC_DIR := ./
VENV_DIR := ./dev/venv

PYTHON := python3
VENV := ./dev/venv.sh "${VENV_DIR}"

.PHONY: dev-test dev-venv-base dev-venv-create dev-venv-install

dev-test:
	${VENV} python -m tox

dev-venv-base:
	${PYTHON} -m venv --clear "${VENV_DIR}"

dev-venv-create: dev-venv-base dev-venv-install

dev-venv-install:
	${VENV} pip3 install --upgrade pip setuptools wheel
	${VENV} pip3 install --upgrade build sphinx tox twine typing-extensions
	${VENV} pip3 install -e "${SRC_DIR}"


################################################################################
# Distribution
################################################################################

.PHONY: dist-build dist-prebuild dist-publish

dist-build: dist-prebuild
	find ./dist -type f -delete
	${VENV} python -m build

dist-prebuild:
	${VENV} python ./prebuild.py

dist-publish: dist-build
	${VENV} twine check ./dist/*
	${VENV} twine upload -r sqlparams --skip-existing ./dist/*
