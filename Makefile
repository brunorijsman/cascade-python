MAKE_FILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
export PYTHONPATH := $(PYTHONPATH):$(MAKE_FILE_DIR)

pre-commit: lint test
	@echo "OK"

clean:
	rm -f .coverage*
	rm -f profile.out
	rm -rf __pycache__
	rm -rf htmlcov
	rm -rf .pytest_cache
	rm -rf cascade/__pycache__
	rm -rf cascade/.pytest_cache
	rm -rf cascade/tests/__pycache__
	rm -rf study/__pycache__
	rm -rf docs/source/_build
	rm -rf docs/source/_modules
	rm -rf docs/build/*

data: data-papers data-performance data-zero-handling

data-papers:
	mkdir -p study/data/papers
	rm -f study/data/papers/data__*
	python study/run_experiments.py study/experiments_papers.json \
		--output-dir study/data/papers

data-papers-subset:
	mkdir -p study/data/papers_subset
	rm -f study/data/papers_subset/data__*
	python study/run_experiments.py study/experiments_papers.json \
		--output-dir study/data/papers_subset --max-runs 3

data-performance:
	mkdir -p study/data/performance
	rm -f study/data/performance/data__*
	python study/run_experiments.py study/experiments_performance.json \
		--output-dir study/data/performance

data-zero-handling:
	mkdir -p study/data/zero_handling
	rm -f study/data/zero_handling/data__*
	python study/run_experiments.py study/experiments_zero_handling.json \
		--output-dir study/data/zero_handling

coverage-open:
	open htmlcov/index.html

docs:
	sphinx-build -a docs/source docs/build

docs-open: docs
	open docs/build/index.html

graphs-papers:
	mkdir -p study/graphs/papers
	rm -f study/graphs/papers/*.png
	python study/make_graphs.py study/graphs_demystifying.json \
		--data-dir study/data/papers
	python study/make_graphs.py study/graphs_andre_reis_thesis.json \
		--data-dir study/data/papers

graphs-performance:
	mkdir -p study/graphs/performance
	rm -f study/graphs/performance/*.png
	python study/make_graphs.py study/graphs_performance.json \
		--data-dir study/data/performance

graphs-zero-handling:
	mkdir -p study/graphs/zero_handling
	rm -f study/graphs/zero_handling/*.png
	python study/make_graphs.py study/graphs_zero_handling.json \
		--data-dir study/data/zero_handling

install:
	pip install -r requirements.txt

lint:
	pylint cascade cascade/tests
	pylint study

profile:
	mkdir -p study/data/profile
	rm -f study/data/performance/data__*
	python -m cProfile -o profile.out study/run_experiments.py --disable-multi-processing \
		--output-directory study/data/profile study/experiments_profile.json
	python -m gprof2dot -f pstats profile.out | dot -Tpng -o profile.png
	open profile.png

profile-open:
	open profile.png

test:
	rm -f .coverage*
	pytest -v -s --cov=cascade --cov-report=html --cov-report term cascade/tests

.PHONY: \
	clean \
	coverage-open \
	data \
	data-papers \
	data-papers-subset \
	data-performance \
	data-zero-handling \
	docs \
	docs-open \
	graphs-papers \
	graphs-performance \
	graphs-zero-handling \
	install \
	lint \
	pre-commit \
	profile \
	profile-open \
	test
