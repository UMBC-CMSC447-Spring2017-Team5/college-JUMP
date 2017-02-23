.PHONY: env install run dist

env:
	python3 -m venv env

install: env
	env/bin/python3 setup.py install --force

run: install
	env/bin/python3 -m collegejump

dist: env
	env/bin/python3 setup.py sdist

clean-dist:
	@rm -rf dist/
