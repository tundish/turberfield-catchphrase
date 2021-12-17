#!/usr/bin/env python
# encoding: UTF-8

import ast
import os.path

from setuptools import setup


try:
    # For setup.py install
    from turberfield.catchphrase import __version__ as version
except ImportError:
    # For pip installations
    version = str(ast.literal_eval(
        open(os.path.join(
            os.path.dirname(__file__),
            "turberfield", "catchphrase", "__init__.py"), "r"
        ).read().split("=")[-1].strip()
    ))

__doc__ = open(os.path.join(os.path.dirname(__file__), "README.rst"),
               'r').read()

setup(
    name="turberfield-catchphrase",
    version=version,
    description="A Python framework for parser-based web adventures.",
    author="D Haynes",
    author_email="tundish@gigeconomy.org.uk",
    url="https://github.com/tundish/turberfield-catchphrase/issues",
    long_description=__doc__,
    classifiers=[
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3"
        " or later (GPLv3+)"
    ],
    namespace_packages=["turberfield"],
    packages=[
        "turberfield.catchphrase",
        "turberfield.catchphrase.css",
        "turberfield.catchphrase.test",
    ],
    package_data={
        "turberfield.catchphrase.css": ["*.css"],
    },
    install_requires=[
        "turberfield-dialogue>=0.39.0",
        "turberfield-utils>=0.38.0",
    ],
    extras_require={},
    tests_require=[],
    entry_points={},
    zip_safe=False
)
