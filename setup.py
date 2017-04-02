#!/usr/bin/env python3
import os
import setuptools, setuptools.command.sdist
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

setuptools.setup(
    name='College JUMP Website',
    version=scmtools.get_scm_version(),
    packages=['collegejump'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Flask >= 0.12',
        'Flask-SQLAlchemy >= 2.2',
        'Flask-Bcrypt',
        'Flask-WTF',
        'Flask-Login',
    ],
    cmdclass={ # Override certain commands
        'sdist': sdist_burn_version
    },
)
