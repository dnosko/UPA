VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
MAIN = src.main

.DEFAULT: help

help:
	@echo "make run"
	@echo "       run main script"
	@echo "make create_env"
	@echo "       creates venv"
	@echo "make update_req"
	@echo "       updates requirements.txt"
	@echo "make clean"
	@echo "       cleans up downloaded files and venv"

#run script
run:
	$(PYTHON) -m $(MAIN)

update_req:
	pip freeze > requirements.txt

create_env:
	python3 -m venv $(VENV)

clean_env:
	rm -rf $(VENV)

clean: clean_env
	cd data && rm -rf download_data