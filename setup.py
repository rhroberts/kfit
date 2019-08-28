#!/usr/bin/env python3

from setuptools import setup, find_packages

app_dir = 'share/kfit/'
image_dir = 'share/images/'

setup(
        name='kfit',
        version='0.1.0',
        description='Simple, graphical spectral fitting in Python.',
        author="Rusty Roberts",
        license="GNU GPL v3",
        data_files=[
            (app_dir, ['kfit/kfit.py', 'kfit/models.py', 'kfit/tools.py',
                       'kfit/kfit.glade', 'kfit/kfit.mplstyle',
                       'kfit/custom_backend_gtk3.py']),
            (image_dir, ['images/kfit_v2.svg'])
        ],
        packages=find_packages(),
        install_requires=[
            'numpy',
            'matplotlib',
            'pandas',
            'lmfit'
        ]
)
