.PHONY: env run test dist dist-clean

run: env
	env/bin/python3 -m collegejump --debug

# Test things
test: env
	env/bin/python3 setup.py test

env: env/setup-stamp

env/setup-stamp: setup.py
	python3 -m venv env
	touch $@
	env/bin/python3 env/bin/pip3 install --editable .

dist:
	env/bin/python3 setup.py sdist

dist-clean:
	@rm -rf dist/
