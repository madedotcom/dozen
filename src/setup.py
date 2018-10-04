#!/usr/bin/env python

from distutils.core import setup

setup(
    name="dozen",
    version="0.0.2",
    description="Build type-safe config from env vars and consul.",
    python_requires=">=3.6.5",
    install_requires=[],
    author="Bob Gregory",
    author_email="bob@made.com",
    url="https://github.com/madedotcom/dozen",
    packages=["dozen", "tests"],
)
