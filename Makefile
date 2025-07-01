.PHONY: test test-unit test-slow test-cov clean install-dev

# Install development dependencies
install-dev:
	pip install -r requirements-test.txt

# Run all tests
test:
	pytest

# Run only fast unit tests
test-unit:
	pytest -m "unit"

# Run only slow integration tests
test-slow:
	pytest -m "slow"

# Run tests with coverage
test-cov:
	pytest --cov=stock_info --cov-report=html --cov-report=term

# Run tests in parallel
test-parallel:
	pytest -n auto

# Run specific test file
test-file:
	pytest tests/test_stock_info.py -v

# Clean up generated files
clean:
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Lint code
lint:
	flake8 stock_info.py tests/
	black --check stock_info.py tests/

# Format code
format:
	black stock_info.py tests/

# Type check
typecheck:
	mypy stock_info.py

# Run all checks
check: lint typecheck test-unit