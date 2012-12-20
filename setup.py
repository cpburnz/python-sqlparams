# coding: utf-8
try:
	from setuptools import setup
	has_setuptools = True
except ImportError:
	from distutils.core import setup
	has_setuptools = False

import sqlparams

# Write readme file.
with open('README.rst', 'wb') as fh:
	fh.write(sqlparams.__doc__)

# Read changes file.
with open('CHANGES.rst', 'rb') as fh:
	changes = fh.read()

kw = {}
if has_setuptools:
	kw['test_suite'] = 'test'

setup(
	name='sqlparams',
	version=sqlparams.__version__,
	author="Caleb P. Burns",
	author_email="cpburnz@gmail.com",
	url="https://github.com/cpburnz/python-sql-parameters.git",
	description="Convert DB API 2.0 named parameters to ordinal parameters.",
	long_description=sqlparams.__doc__ + "\n" + changes,
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
	license="MIT",
	packages=['sqlparams'],
	**kw
)
