pre-commit: lint test
	@echo "OK"

install:
	pip install -r requirements.txt

lint:
	pylint cascade cascade/tests
	pylint study

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
	python -m cProfile -o profile.out study/run_experiments.py --disable-multi-processing \
		study/experiments_profile.json
	python -m gprof2dot -f pstats profile.out | dot -Tpng -o profile.png
	open profile.png

profile-open:
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

.PHONY: \
	clean \
	coverage-open \
	docs \
	docs-open \
	install \
	lint \
	pre-commit \
	profile \
	profile-open \
	test
