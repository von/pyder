#!/usr/bin/env python
try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name = "pyder",
    version = "0.2",
    packages = [ "pyder" ],
    scripts = [ 'pyderweb' ],

    author = "Von Welch",
    author_email = "von@vwelch.com",
    description = "A python/mako static website builder",
    license = "Apache2",

    install_requires = [ "Markdown" ],
)
