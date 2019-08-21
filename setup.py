#!/usr/bin/env python3

from setuptools import setup, find_packages

DEST = 'share/kfit/'

setup(
        name='kfit',
        version='0.1.0',
        description='Simple, graphical spectral fitting in Python.',
        author="Rusty Roberts",
        license="GNU GPL v3",
        data_files=[(DEST, ['kfit/kfit.py'])],
        packages=find_packages(),
        install_requires=[
            'pandas',
            'scipy',
            'numpy',
            'matplotlib',
            'lmfit',
            'PyQt5',
            'pyperclip'
        ]
)
