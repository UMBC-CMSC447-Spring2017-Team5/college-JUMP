.PHONY: env run test dist dist-clean

run: env
	env/bin/python3 -m collegejump

# Test things
test: env
	env/bin/python3 test.py

env: env/setup-stamp
dist: dist/setup-stamp

env/setup-stamp: setup.py
	touch $@
	python3 -m venv env
	env/bin/python3 env/bin/pip3 install --editable .

dist/setup-stamp: setup.py
	touch $@
	env/bin/python3 setup.py sdist

dist-clean:
	@rm -rf dist/
