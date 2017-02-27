.PHONY: env install run dist clean-dist

dist: env
	env/bin/python3 setup.py sdist

install: dist
	pip3 install --force "dist/$(shell env/bin/python3 setup.py --fullname).tar.gz"

env:
	python3 -m venv env

run: install
	python3 -m collegejump

vrun:
	vagrant up --provision
	vagrant ssh --command "python3 -m collegejump --host 0.0.0.0"

vhalt:
	vagrant halt

clean-dist:
	@rm -rf dist/
