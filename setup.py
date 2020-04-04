"""
This script is used to build :mod:`sqlparams`.
"""

import re

from setuptools import setup
from setuptools.command.build_py import build_py


class BuildCommand(build_py):
	"""
	Hook into setuptools's build system to generate "README.rst".
	"""

	def run(self):
		generate_readme()
		super().run()


def generate_readme():
	"""
	Generate the "README.rst" file from "README.rst.in".
	"""
	with open("README.in", 'r', encoding='UTF-8') as fh:
		readme = fh.read()

	for old, new in [
		(":class:`dict`", "*dict*"),
		(":class:`tuple`", "*tuple*"),
		(":class:`.SQLParams`", "`SQLParams`_"),
		(":meth:`.SQLParams.format`", "`SQLParams.format`_"),
		(":meth:`.SQLParams.formatmany`", "`SQLParams.formatmany`_"),
		(":mod:`sqlparams`", "*sqlparams*"),
	]:
		readme = readme.replace(old, new)

	readme += "\n"
	readme += ".. _`SQLParams`: https://python-sql-parameters.readthedocs.io/en/latest/sqlparams.html#sqlparams.SQLParams\n"
	readme += ".. _`SQLParams.format`: https://python-sql-parameters.readthedocs.io/en/latest/sqlparams.html#sqlparams.SQLParams.format\n"
	readme += ".. _`SQLParams.formatmany`: https://python-sql-parameters.readthedocs.io/en/latest/sqlparams.html#sqlparams.SQLParams.formatmany\n"

	with open("README.rst", 'w', encoding='UTF-8') as fh:
		fh.write(readme)


# Run setuptools.
setup(cmdclass={'build_py': BuildCommand})
