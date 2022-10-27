VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
MAIN = src.main

.DEFAULT: help

help:
	@echo "make run"
	@echo "       run main script"
	@echo "make install-env"
	@echo "       creates venv and install requirements into it"
	@echo "make clean"
	@echo "       cleans up cache files and venv"

#run script
run:
	$(PYTHON) -m $(MAIN)

create-env:
	python3 -m venv $(VENV)

#this will install all requirements in venv, still MAKE SURE TO ACTIVATE VENV from your shell/terminal
install-env: create-env
	( \
    	source $(VENV)/bin/activate; \
    	pip install -r requirements.txt; \
    )

update-req:
	$(PYTHON) -m pip freeze > requirements.txt

clean-env:
	rm -rf $(VENV)

clean-cache:
	rm -rf .pytest_cache
	rm -rf src/__pycache__

clean: clean-cache clean-env
