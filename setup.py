#!/usr/bin/env python3
import os
import setuptools, setuptools.command.sdist, setuptools.command.test
import sys

# Load scmtools from inside the package, so that the code to get the version is
# always the same.
sys.path.append(os.path.abspath("collegejump"))
import scmtools

# Override sdist to include a _version.py file with the Git version
class sdist_burn_version(setuptools.command.sdist.sdist):
    def run(self):
        version = scmtools.get_scm_version()
        with open('collegejump/_version.py', 'w') as f:
            f.write('__version__ = \'{}\''.format(version))

        super().run()

        os.remove('collegejump/_version.py')

# PyTest runner borrowed from
# https://docs.pytest.org/en/latest/goodpractices.html#manual-integration
class PyTest(setuptools.command.test.test):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        super().initialize_options()
        self.pytest_args = 'collegejump --pylint --pylint-rcfile=pylintrc --junit-xml=coverage.xml'

    def run_tests(self):
        import shlex
        #import here, cause outside the eggs aren't loaded
        import pytest, pylint, pylint_flask
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)

setuptools.setup(
    name='College JUMP Website',
    version=scmtools.get_scm_version(),
    packages=['collegejump'],
    include_package_data=True,
    zip_safe=False,
    tests_require=[
        'pytest',
        'pytest-pylint',
        'pylint-flask',
    ],
    install_requires=[
        'setuptools',
        'Flask >= 0.12',
        'Flask-SQLAlchemy >= 2.2',
        'Flask-Bootstrap >= 3.3.7, < 3.3.8',
        'SQLAlchemy-Utils',
        'Flask-Bcrypt',
        'Flask-WTF',
        'Flask-Login',
        'markdown',
    ],
    cmdclass={ # Override certain commands
        'sdist': sdist_burn_version,
        'test': PyTest,
    },
)
