.PHONY: env run test vrun vhalt install user_run dist clean-dist

env:
	python3 -m venv env
	env/bin/python3 env/bin/pip3 install --editable .

run: env
	env/bin/python3 -m collegejump

# Test things
test: env
	env/bin/python3 test.py

# Run the module inside a vagrant instance. (Remember to vhalt afterward.)
vrun:
	vagrant up
	vagrant ssh --command "cd collegejump && make user_run"

vhalt:
	vagrant halt

install: dist
	pip3 install --force "dist/$(shell env/bin/python3 setup.py --fullname).tar.gz"

# Install dependencies user-wide and run the module from the current directory.
user_run:
	pip3 install --editable .
	python3 -m collegejump --host 0.0.0.0

dist: env
	env/bin/python3 setup.py sdist

clean-dist:
	@rm -rf dist/
