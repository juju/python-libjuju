# Copyright 2016 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).absolute().parent
readme = here / 'docs' / 'readme.rst'
changelog = here / 'docs' / 'changelog.rst'
long_description = '{}\n\n{}'.format(
    readme.read_text(),
    changelog.read_text()
)
version = here / 'VERSION'

setup(
    name='juju',
    version=version.read_text().strip(),
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=[
        'macaroonbakery>=1.1,<2.0',
        'pyRFC3339>=1.0,<2.0',
        'pyyaml>=5.1.2,<=6.0',
        'theblues>=0.5.1,<1.0',
        'websockets>=7.0,<8.0',
        'paramiko>=2.4.0,<3.0.0',
        'pyasn1>=0.4.4',
        'toposort>=1.5,<2',
        'typing_inspect>=0.6.0'
    ],
    include_package_data=True,
    maintainer='Juju Ecosystem Engineering',
    maintainer_email='juju@lists.ubuntu.com',
    description=('Python library for Juju'),
    long_description=long_description,
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
    ],
    entry_points={
        'console_scripts': [
        ],
    },
)
