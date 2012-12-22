# coding: utf-8
import re
try:
	from setuptools import setup
	has_setuptools = True
except ImportError:
	from distutils.core import setup
	has_setuptools = False

import sqlparams

# Write readme file.
desc = sqlparams.__doc__
desc = re.sub(r"\|([a-zA-Z0-9.()]+)\|_?", r"*\1*", desc)
with open('README.rst', 'wb') as fh:
	fh.write(desc)

# Read changes file.
with open('CHANGES.rst', 'rb') as fh:
	changes = fh.read()

kw = {}
if has_setuptools:
	kw['test_suite'] = 'test'

setup(
	name=sqlparams.__project__,
	version=sqlparams.__version__,
	author=sqlparams.__author__,
	author_email=sqlparams.__email__,
	url="https://github.com/cpburnz/python-sql-parameters.git",
	description="Convert DB API 2.0 named parameters to ordinal parameters.",
	long_description=desc + "\n" + changes,
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2.7",
		"Topic :: Database",
		"Topic :: Software Development",
		"Topic :: Utilities"
	],
	license=sqlparams.__license__,
	packages=['sqlparams'],
	**kw
)
