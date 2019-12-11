pre-commit: lint test
	@echo "OK"

install:
	pip install -r requirements.txt

lint:
	pylint bb84 bb84/tests bb84/cascade bb84/cascade/tests

test:
	rm -f .coverage*
	pytest -v -s --cov=bb84 --cov-report=html --cov-report term bb84/tests
	pytest -v -s --cov=bb84/cascade --cov-report=html --cov-report term bb84/cascade/tests

test-cascade:
	rm -f .coverage*
	pytest -v -s --cov=bb84/cascade --cov-report=html --cov-report term bb84/cascade/tests

coverage-open:
	open htmlcov/index.html

docs:
	sphinx-build -a docs/source docs/build

docs-open:
	open docs/build/index.html

clean:
	rm -f .coverage*
	rm -rf __pycache__
	rm -rf htmlcov
	rm -rf .pytest_cache
	rm -rf bb84/__pycache__
	rm -rf bb84/.pytest_cache
	rm -rf bb84/tests/__pycache__
	rm -rf bb84/cascade/__pycache__
	rm -rf bb84/cascade/.pytest_cache
	rm -rf bb84/cascade/tests/__pycache__
	rm -rf docs/source/_modules
	rm -rf docs/build/*

.PHONY: pre-commit install lint test test-cascade coverage-open docs docs-open clean