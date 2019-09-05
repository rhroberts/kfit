#!/usr/bin/env python3

from setuptools import setup, find_packages

prime = './'
app_dir = 'share/kfit/'
image_dir = 'share/images/'

setup(
        name='kfit',
        version='0.1.1',
        description='Simple, graphical spectral fitting in Python.',
        author="Rusty Roberts",
        license="GNU GPL v3",
        data_files=[
            (prime, ['kfit.desktop', 'images/kfit_v2.svg']),
            (app_dir, ['kfit/kfit.py', 'kfit/models.py', 'kfit/tools.py',
                       'kfit/kfit.glade', 'kfit/kfit.mplstyle',
                       'kfit/custom_backend_gtk3.py']),
            (image_dir, ['images/kfit_v2.svg',
                         'images/document-properties-symbolic.svg',
                         'images/document-save-symbolic.svg',
                         'images/document-send-symbolic.svg',
                         'images/drive-optical-symbolic.svg',
                         'images/view-refresh-symbolic.svg',
                         'images/list-add-symbolic.svg',
                         'images/list-remove-symbolic.svg',
                         'images/dialog-question-symbolic.svg'])
        ],
        packages=find_packages(),
        install_requires=[
            'numpy',
            'matplotlib',
            'pandas',
            'lmfit'
        ]
)
