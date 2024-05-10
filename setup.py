from setuptools import setup, find_packages
from os.path import splitext
from os.path import basename
from glob import glob

#TODO: Review versions of packages & license

setup(
    name='verifier',
    version='0.1',
    license='TODO',
    description='Cardano Ballot KERI Verifier',
    long_description="Cardano Ballot KERI Verifier",
    author='Cardano Foundation',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    entry_points={
        'console_scripts': [
            'verifier = verifier.cli.verifier:main',
        ]
    },
    python_requires='>=3.10.4',
    install_requires=[
        'hio>=0.6.9',
        'keri==1.1.13',
        'multicommand>=1.0.0'
    ]
    )