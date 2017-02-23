.PHONY: run
run: env
	env/bin/python -m app

env: python-requirements
	python3 -m venv env
	env/bin/pip install --requirement python-requirements
	touch env
