.PHONY: test run check compare all

test:
	python -m unittest discover -s tests -v
run:
	python run_experiments.py
check:
	python property_checks.py
compare:
	python compare_baselines.py
all:
	python verify_project.py
