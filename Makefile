.PHONY: install test lint format demo down logs

install:
	python -m pip install -e '.[dev]'

test:
	pytest --cov=iiot_platform --cov-report=term-missing

lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

demo:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f api mqtt-collector opcua-collector
