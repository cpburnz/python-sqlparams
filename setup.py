# coding: utf-8
from __future__ import unicode_literals

import io
import re
try:
	from setuptools import setup
	has_setuptools = True
except ImportError:
	from distutils.core import setup
	has_setuptools = False

from sqlparams import __author__, __doc__, __email__, __license__, __project__, __version__

# Write readme file.
description = __doc__
description = re.sub('\\|([a-zA-Z0-9.()]+)\\|_?', '*\\1*', description)
with io.open('README.rst', mode='w', encoding='UTF-8') as fh:
	fh.write(description)

# Read changes file.
with io.open('CHANGES.rst', mode='r', encoding='UTF-8') as fh:
	changes = fh.read().strip()

setup(
	name=__project__,
	version=__version__,
	author=__author__,
	author_email=__email__,
	url="https://github.com/cpburnz/python-sql-parameters.git",
	description="Convert DB API 2.0 named parameters to ordinal parameters.",
	long_description=description + "\n\n" + changes,
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.2",
		"Programming Language :: Python :: 3.3",
		"Programming Language :: Python :: 3.4",
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: Implementation :: CPython",
		"Programming Language :: Python :: Implementation :: PyPy",
		"Topic :: Database",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: Utilities"
	],
	license=__license__,
	packages=['sqlparams'],
	**(dict(
		test_suite='test',
	) if has_setuptools else {})
)
