# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).absolute().parent
readme = here / 'docs' / 'readme.rst'
changelog = here / 'docs' / 'changelog.rst'
long_description = '{}\n\n{}'.format(
    readme.read_text(),
    changelog.read_text()
)
long_description_content_type = 'text/x-rst'
version = here / 'VERSION'

setup(
    name='juju',
    version=version.read_text().strip(),
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=[
        'macaroonbakery>=1.1,<2.0',
        'pyRFC3339>=1.0,<2.0',
        'pyyaml>=5.1.2',
        'theblues>=0.5.1,<1.0',
        'websockets>=7.0,<8.0 ; python_version<"3.9"',
        'websockets>=8.0,<9.0 ; python_version=="3.9"',
        'websockets>=9.0; python_version>"3.9"',
        'paramiko>=2.4.0,<3.0.0',
        'pyasn1>=0.4.4',
        'toposort>=1.5,<2',
        'typing_inspect>=0.6.0',
        'kubernetes>=12.0.1',
    ],
    include_package_data=True,
    maintainer='Juju Ecosystem Engineering',
    maintainer_email='juju@lists.ubuntu.com',
    description=('Python library for Juju'),
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    url='https://github.com/juju/python-libjuju',
    license='Apache 2',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        'console_scripts': [
        ],
    },
)
