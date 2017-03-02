# College JUMP Website

*information and background*

## Developer's Guide

The College JUMP website is written using Python3 and the Flask web framework.
Developing and running the site requires Python3 and Flask, and other
software requirements which may be installed using `pip` inside of a Python
virtual environment.

### Vagrant

The website may be developed completely within a virtual environment known as
Vagrant. This allows us to build and run the website on a standard virtual
interface. To do so, download and install
[Vagrant](https://www.vagrantup.com/downloads.html)
for your operating system.

To start or update the website, run the following command (if you are on a Unix
environment, and have `make`). The first time, this will take a while.
```
make vrun
```

Keeping Vagrant running will consume some resources, so to stop the virtual
machine, run the following.
```
make vhalt
```

### Makefile

Make is not necessary to run the website, but it is a handy tool that lets us
keep our development processes standardized. The information below is rolled
into the repository `Makefile`.

### Virtual Environment

Python3 ships with a virtual environment module, which can be used to install
Python libraries and utilities inside a directory, to be kept isolated from the
system libraries. The libraries are listed in a text file called
`python-requirements`.

To prepare a virtual environment for the first time, execute
```
python3 -m venv env
```
If your Python executable is not called `python3`, it may be called `python` or
`Python`.
Once prepared, execute this to install requirements,
```
env/bin/pip install --force .
```

### Flask Itself

The website is organized underneath the `app` directory into fairly distinct
components. These are stitched together by the `__init__.py` file, which just
does the bootstrapping and imports from various portions of the directory. The
directory is organized as follows:

- `views` is responsible for website display **logic** (not HTML/CSS/JS)
- `templates` holds the HTML/CSS templates to be served

## Contrib and Extra Scripts

Extra scripts and service files may be stored in the `contrib/` folder. For
example, the Systemd service is installed there.
