# HSLU
#
# Created by Thomas Koller on 7/28/2020
#
from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="jass_kit",
    version="2.0.3",
    author="ABIZ HSLU",
    author_email="thomas.koller@hslu.ch",
    description="Package for the game of jass",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_namespace_packages(include=['jass.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy>=1.19'
    ],
    python_requires='>=3.6'
)

