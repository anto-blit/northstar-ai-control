.PHONY: test run check compare recover monitor all

test:
	python -m unittest discover -s tests -v
run:
	python run_experiments.py
check:
	python property_checks.py
compare:
	python compare_baselines.py
recover:
	python recoverability_analysis.py
monitor:
	python monitor_analysis.py
all:
	python verify_project.py
