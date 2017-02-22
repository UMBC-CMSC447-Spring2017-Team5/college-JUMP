.PHONY: run
run: env
	./run.py

env: python-requirements
	python3 -m venv env
	env/bin/pip install --requirement python-requirements
	touch env
