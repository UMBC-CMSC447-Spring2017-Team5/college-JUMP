.PHONY: env run dist

env:
	python3 -m venv env

run: env
	env/bin/python3 setup.py install
	env/bin/python -m collegejump

dist: env
	env/bin/python3 setup.py sdist

clean-dist:
	@rm -rf dist/
