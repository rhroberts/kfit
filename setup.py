from setuptools import setup, find_packages


setup(
        name='kfit',
        version='0.1.0',
        description='Simple, graphical spectral fitting in Python.',
        packages=find_packages(),
        install_requires=[
            'pandas',
            'scipy',
            'numpy',
            'matplotlib',
            'lmfit'
    ]
)
