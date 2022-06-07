#
# This Makefile is used to manage the the development virtual environment.
#
# Created: 2022-03-23
# Updated: 2022-05-30
#

.PHONY: create-venv help update-venv venv-base venv-install

DEV_DIR := ../
VENV_DIR := ./venv

PYTHON := python3
VENV := ./venv.sh "${VENV_DIR}"

help:
	@echo "Usage: make [<target>]"
	@echo
	@echo "Development Targets:"
	@echo "  create-venv  Create the development Python virtual environment."
	@echo "  update-venv  Update the development Python virtual environment."

create-venv: venv-base venv-install

update-venv: venv-install

venv-base:
	${PYTHON} -m venv --clear "${VENV_DIR}"

venv-install:
	${VENV} pip install --upgrade pip setuptools wheel
	${VENV} pip install --upgrade tox
	${VENV} pip install -e "${DEV_DIR}"
