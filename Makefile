install:
	pip install -r requirements.txt

clean:
	rm -f .coverage*
	rm -rf __pycache__
	rm -rf bb84/__pycache__
	rm -rf tests/__pycache__

lint:
	pylint bb84 bb84/tests bb84/cascade bb84/cascade/tests

test:
	rm -f .coverage*
	pytest -v -s --cov=bb84 --cov-report=html --cov-report term bb84/tests
	pytest -v -s --cov=bb84/cascade --cov-report=html --cov-report term bb84/cascade/tests

test-cascade:
	rm -f .coverage*
	pytest -v -s --cov=bb84/cascade --cov-report=html --cov-report term bb84/cascade/tests

pre-commit: lint test
	@echo "OK"

.PHONY: install clean lint test test-cascade pre-commit