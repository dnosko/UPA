help:
	@echo "make update"
	@echo "      update environment.yml"
	@echo "make create-env-from-yml"
	@echo "       creates venv and install requirements into it"
	@echo "make clean"
	@echo "       cleans up cache files and venv"

activate:
	conda activate UPA2022

create-env-from-yml:
	conda env create -f environment.yml

update:
	conda env export > environment.yml

download:
	cd client && python3 main.py

