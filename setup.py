# Arline Quantum
# Copyright (C) 2019-2020 Turation Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="arline-quantum",
    version="0.1.6",
    author="Turation Ltd",
    author_email="info@arline.io",
    description="Quantum Hardware Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArlineQ/arline_quantum",
    packages=setuptools.find_packages(exclude=['tests*']),
    license="GNU Affero General Public License v3 (AGPLv3)",
    install_requires=[
        "numpy>=1.18.3",
        "scipy>=1.3.1",
        "cirq~=0.6.0",
        "qiskit~=0.18.0",
        "sympy>=1.5",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    include_package_data=True,
)
