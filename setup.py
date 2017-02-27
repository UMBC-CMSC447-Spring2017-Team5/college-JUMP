#!/usr/bin/env python3
from setuptools import setup, find_packages
import subprocess

try:
    version = subprocess.check_output(
            ['git', 'describe', '--always', '--dirty=-plus']) \
            .decode('UTF-8').strip()
except Exception as e:
    print("Could not get version: {}", repr(e))
    version = None

setup(
    name='College JUMP Website',
    version=version,
    packages=['collegejump'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask >= 0.12',
    ]
)
