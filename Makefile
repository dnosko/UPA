help:
	@echo "make update"
	@echo "      update environment.yml"
	@echo "make create-env-from-yml"
	@echo "       creates venv and install requirements into it"
	@echo "make clean"
	@echo "       cleans up cache files and venv"





update:
	pip freeze > requirements.txt
	cp requirements.txt ./server/

docker:
	docker-compose rm -f
	docker-compose up --build -d

