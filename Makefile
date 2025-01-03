.PHONY: lint check dev lint-check

lint-check:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy --show-error-codes --pretty dnsgen/

lint:
	bash .git/hooks/pre-commit
	uv run ruff format ./dnsgen
	uv run ruff check --fix ./dnsgen

dev:
	uv pip install . --extra dev
	uv run pre-commit install