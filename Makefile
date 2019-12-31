pre-commit: lint test
	@echo "OK"

install:
	pip install -r requirements.txt

lint:
	pylint cascade cascade/tests

test:
	rm -f .coverage*
	pytest -v -s --cov=cascade --cov-report=html --cov-report term cascade/tests

coverage-open:
	open htmlcov/index.html

docs:
	sphinx-build -a docs/source docs/build

docs-open: docs
	open docs/build/index.html

profile:
	PYTHONPATH=$(pwd) python -m cProfile -o profile.out cascade/tests/test_session.py
	python -m gprof2dot -f pstats profile.out | dot -Tpng -o profile.png

profile-open: profile
	open profile.png

clean:
	rm -f .coverage*
	rm -f profile.out profile.png
	rm -rf __pycache__
	rm -rf htmlcov
	rm -rf .pytest_cache
	rm -rf cascade/__pycache__
	rm -rf cascade/.pytest_cache
	rm -rf cascade/tests/__pycache__
	rm -rf docs/source/_modules
	rm -rf docs/build/*

.PHONY: pre-commit install lint test coverage-open docs docs-open profile profile-open clean