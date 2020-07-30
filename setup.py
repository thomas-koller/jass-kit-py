# HSLU
#
# Created by Thomas Koller on 7/28/2020
#
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jass-kit-py",
    version="2.0",
    author="ABIZ HSLU",
    author_email="thomas.koller@hslu.ch",
    description="Package for the game of jass",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(exclude=['test']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy>=1.19'
    ],
    python_requires='>=3.7'
)

