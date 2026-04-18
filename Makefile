.PHONY: install test lint docs clean

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v --cov=loopiase --cov-report=term-missing

lint:
	python -m pyright src/ tests/

docs:
	sphinx-build -b html docs/ docs/_build

clean:
	rm -rf docs/_build/ .pytest_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
