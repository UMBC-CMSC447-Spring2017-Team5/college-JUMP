.PHONY: env install run dist clean-dist

dist: env
	env/bin/python3 setup.py sdist

install: dist
	pip3 install --force "dist/$(shell env/bin/python3 setup.py --fullname).tar.gz"

env:
	python3 -m venv env
	env/bin/pip3 install --editable .

run: env
	python3 -m collegejump
	env/bin/python3 -m collegejump

# Install dependencies user-wide and run the module from the current directory.
user_run:
	pip3 install --editable .
	python3 -m collegejump --host 0.0.0.0

# Run the module inside a vagrant instance. (Remember to vhalt afterward.)
vrun:
	vagrant up
	vagrant ssh --command "cd collegejump && make user_run"

vhalt:
	vagrant halt

clean-dist:
	@rm -rf dist/
