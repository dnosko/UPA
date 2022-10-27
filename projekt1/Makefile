help:
	@echo "make update"
	@echo "      update environment.yml"
	@echo "make create-env-from-yml"
	@echo "       creates venv and install requirements into it"
	@echo "make clean"
	@echo "       cleans up cache files and venv"




start:
	cp requirements.txt ./server/
	docker-compose up --build -d



removeData:
	cd data && rm -rf download_data && rm -rf extract_data && rm -rf cache.json


update:
	pip freeze > requirements.txt
	cp requirements.txt ./server/

docker:
	docker-compose rm -f
	docker-compose up --build -d

