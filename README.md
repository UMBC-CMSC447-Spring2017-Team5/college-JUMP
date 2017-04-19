# College JUMP Website

This is the source code of the College JUMP (Journey Upward Mentoring Program) 
website. The goal of this website is to enable mentors and students to interact 
with one another in a similar manner to that of Blackboard. For example, a mentor 
should be able to view the completed tasks of a student, upload worksheets, and 
download any documents the student uploads. The opposite is also true of students 
in that they should be able to complete assigned tasks, consisting of U.I. 
elements, upload completed worksheets, and download documents. Additionally, 
administrators should be enabled to create, edit, and delete user accounts and 
ciriculum. Some of the noteable requirements of this website include having multiple 
levels of user access, the already stated file uploading and downloading, account 
modification, page navigation, and viewing of an integrated Google calendar. The 
following sections discuss the tools used to develop these functionalities and 
provide the basic setup steps to creating a functioning development environment.

The website is available at a [demo location][].

## Developer's Guide

The College JUMP website is written using Python3 and the Flask web framework.
Developing and running the site requires Python3 and Flask, and other
software requirements which may be installed using `pip` inside of a Python
virtual environment. For setup information, please consult the 
`Instantiating Local Builds` section below.

### Makefile

Make is not necessary to run the website, but it is a handy tool that lets us
keep our development processes standardized. It also enables us to build and 
run a working, offline iteration of the website through the use of the `make run` 
command. The information below is rolled into the repository `Makefile`.

### Virtual Environments

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

### Testing

Testing has its own set of dependencies, which are also automatically installed,
but which require the Python3 development headers to be installed. On Debian or
one of its derivatives, issue this command.
```
apt install python3-dev
```

In order to perform the automated testing, which includes both unit tests and
code linting, either run `make test` or invoke the setup script directly:
```
env/bin/python3 setup.py test
```

Tests themselves are managed with `pytest`, and located in the module
`collegejump.test`.


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

## Instantiating Local Builds

The instantiation of local builds enables us to test code modifications 
without compromising the main build. To instantiate a local build, simply 
use the `make run` command then type `http://localhost:8088/` into any 
browser of your choice to view the build.

While the build is active, you can modify the code and any changes will be 
reflected on the local build in real-time.

[demo location]: https://lassa.xen.prgmr.com/collegejump/
