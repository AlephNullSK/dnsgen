.PHONY: lint check dev lint-check

check:
	poetry run pre-commit run --all-files

lint:
	poetry run black .
	poetry run isort . --profile black

lint-check:
	python3 -m poetry run black . --check
	python3 -m poetry run isort . --check-only --profile black
	python3 -m poetry run flake8 .

dev:
	python3 -m pip install -U poetry
	poetry install
	poetry run pre-commit install
