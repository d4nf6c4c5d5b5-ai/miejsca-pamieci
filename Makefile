.PHONY: help data sample test lint format serve docker

help:          ## Lista poleceń
	@grep -E '^[a-z]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/ —/'

data:          ## Pobierz dane z dane.gov.pl i zbuduj web/data/places.json
	python3 scripts/fetch_data.py

sample:        ## Zbuduj dane z próbki testowej (offline)
	python3 scripts/fetch_data.py --sample

test:          ## Uruchom testy
	python3 -m unittest discover -s tests -v

lint:          ## Linter (ruff) + sprawdzenie składni JS
	ruff check . && ruff format --check . && node --check web/app.js

format:        ## Formatowanie kodu
	ruff format . && ruff check --fix .

serve:         ## Serwer lokalny na http://localhost:8080
	python3 scripts/serve.py

docker:        ## Uruchom w Dockerze
	docker compose up --build
