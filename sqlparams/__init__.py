# coding: utf-8
r"""
|sqlparams|: SQL Parameters
===========================

|sqlparams| is a utility module for simplifying the use of SQL
parameters in queries. Some `Python DB API 2.0`_ compliant modules only
support the ordinal *qmark* or *format* style parameters (e.g., pyodbc_
only supports *qmark*). This utility module provides a helper class,
|SQLParams|, that is used to support named parameter styles such as
*named*, *numeric* and *pyformat*, and have them safely converted to the
desired ordinal style.

.. _`Python DB API 2.0`: http://www.python.org/dev/peps/pep-0249/
.. _pyodbc: https://github.com/mkleehammer/pyodbc


Tutorial
--------

You first create an |SQLParams| instance specifying the named
parameter style you're converting from, and what ordinal style you're
converting to. Let's convert from *named* to *qmark* style::

  >>> import sqlparams
  >>> query = sqlparams.SQLParams('named', 'qmark')

Now, lets to convert a simple SQL SELECT query using the |.format()|
method which accepts an SQL query, and a |dict| of parameters::

  >>> sql, params = query.format('SELECT * FROM users WHERE name = :name;', {'name': "Thorin"})

This returns the new SQL query using ordinal *qmark* parameters with the
corresponding list of ordinal parameters, which can be passed to the
`.execute()`_ method on a database cursor::

  >>> print sql
  SELECT * FROM users WHERE name = ?;
  >>> print params
  ['Thorin']

.. _`.execute()`: http://www.python.org/dev/peps/pep-0249/#id15

|tuple|\ s are also supported which allows for safe use of the SQL IN
operator::

  >>> sql, params = query.format("SELECT * FROM users WHERE name IN :names;", {'names': ("Dori", "Nori", "Ori")})
  >>> print sql
  SELECT * FROM users WHERE name in (?,?,?);
  >>> print params
  ['Dori', 'Nori', 'Ori']

You can also format multiple parameters for a single, shared query
useful with the `.executemany()`_ method of a database cursor::

  >>> sql, manyparams = query.formatmany("UPDATE users SET age = :age WHERE name = :name;", [{'name': "Dwalin", 'age': 169}, {'name': "Balin", 'age': 178}])
  >>> print sql
  UPDATE users SET age = ? WHERE name = ?;
  >>> print manyparams
  [[169, 'Dwalin'], [178, 'Balin']]

.. _`.executemany()`: http://www.python.org/dev/peps/pep-0249/#executeman

Please note that if a tuple is used in |.formatmany()|, the tuple must
be the same size in each of the parameter lists. Otherwise, you might
well use |.format()| in a for-loop.


Source
------

The source code for |sqlparams| is available from the GitHub repo
`cpburnz/python-sql-parameters`_.

.. _`cpburnz/python-sql-parameters`: https://github.com/cpburnz/python-sql-parameters.git


Installation
------------

|sqlparams| can be installed from source with::

  python setup.py install

|sqlparams| is also available for install through PyPI_::

  pip install sqlparams

.. _PyPI: http://pypi.python.org/pypi/sqlparams


Documentation
-------------

Documentation for |sqlparams| is available on `Read the Docs`_.

.. _`Read the Docs`: https://python-sql-parameters.readthedocs.org
"""
from __future__ import unicode_literals

__author__ = "Caleb P. Burns"
__copyright__ = "Copyright © 2012-2017 by Caleb P. Burns"
__created__ = "2012-11-30"
__email__ = "cpburnz@gmail.com"
__license__ = "MIT"
__project__ = "sqlparams"
__status__ = "Production"
__updated__ = "2018-05-04"
__version__ = "1.1.2"

import collections
import re

from .compat import iteritems, unicode

#: The encoding to use when parsing a byte query string.
_BYTES_ENCODING = 'latin1'

#: Regular expression used to match "named" style parameters.
_NAMED_STYLE_NAMED = re.compile(':(\\w+)')

#: Regular expression used to match "numeric" style paramters.
_NAMED_STYLE_NUMERIC = re.compile(':(\\d+)')

#: Regular expression used to match "pyformat" style parameters.
_NAMED_STYLE_PYFORMAT = re.compile('%\\((\\w+)\\)s')

#: Maps named parameter style to its regular expression.
_LOOKUP_NAMED_STYLE = {
	'named': _NAMED_STYLE_NAMED,
	'numeric': _NAMED_STYLE_NUMERIC,
	'pyformat': _NAMED_STYLE_PYFORMAT,
}

#: The "format" ordinal parameter style.
_ORDINAL_STYLE_FORMAT = '%s'

#: The "qmark" ordinal parameter style.
_ORDINAL_STYLE_QMARK = '?'

#: Maps ordinal parameter style to its string.
_LOOKUP_ORDINAL_STYLE = {
	'format': _ORDINAL_STYLE_FORMAT,
	'qmark': _ORDINAL_STYLE_QMARK,
}


class SQLParams(object):
	"""
	The |SQLParams| class is used to support named parameters in SQL
	queries where they are not otherwise supported (e.g., pyodbc). This is
	done by converting from a named parameter style query to an ordinal
	style.

	Any |tuple| parameter will be expanded into "(?,?,...)" to support the
	widely used "IN {tuple}" SQL expression without leaking any unescaped
	values.
	"""

	def __init__(self, named, ordinal):
		"""
		Instantiates the |SQLParams| instance.

		*named* (|string|) is the named parameter style that will be used in
		an SQL query before being parsed and formatted to *ordinal*.

		- "named" indicates that the parameters will be in named style::

		    ... WHERE name = :name

		- "numeric" indicates that the parameters will be in numeric,
		  positional style::

		    ... WHERE name = :1

		- "pyformat" indicates that the parameters will be in python
		  extended format codes::

		    ... WHERE name = %(name)s

		*ordinal* (|string|) is the ordinal parameter style that the SQL
		query will be formatted to.

		- "format" indicates that parameters will be converted into format
		  style::

		    ... WHERE name = %s

		- "qmark" indicates that parameters will be converted into question
		  mark style::

		    ... WHERE name = ?

	  .. NOTE:: Strictly speaking, `PEP 249`_ only specifies "%s" and
	     "%(name)s" for the "format" and "pyformat" parameter styles so
	     only those two (without any other conversions or flags) are
	     supported by |SQLParams|.

		.. _`PEP 249`: http://www.python.org/dev/peps/pep-0249/
		"""

		self.named = None
		"""
		*named* (|string|) is the named parameter style that will be used
		in an SQL query before being parsed and formatted to |self.ordinal|.
		"""

		self.ordinal = None
		"""
		*ordinal* (|string|) is the ordinal parameter style that the SQL
		query will be formatted to.
		"""

		self.match = None
		"""
		*match* (|RegexObject|) is the regular expression that matches
		parameter style of |self.named|.
		"""

		self.replace = None
		"""
		*replace* (|string|) is what each matched string from |self.match|
		will be replaced with.
		"""

		if not isinstance(named, (unicode, bytes)):
			raise TypeError("named:{!r} is not a string.".format(named))

		if not isinstance(ordinal, (unicode, bytes)):
			raise TypeError("ordinal:{!r} is not a string.".format(ordinal))

		self.named = named
		self.ordinal = ordinal

		self.match = _LOOKUP_NAMED_STYLE[named]
		self.replace = _LOOKUP_ORDINAL_STYLE[ordinal]

	def __repr__(self):
		"""
		Returns the canonical string representation (|string|) of this
		instance.
		"""
		return "{}.{}({!r}, {!r})".format(self.__class__.__module__, self.__class__.__name__, self.named, self.ordinal)

	def format(self, sql, params):
		"""
		Formats the SQL query to use ordinal parameters instead of named
		parameters.

		*sql* (|string|) is the SQL query.

		*params* (|dict|) maps each named parameter (|string|) to value
		(|object|). If |self.named| is "numeric", then *params* can be
		simply a |sequence| of values mapped by index.

		Returns a 2-|tuple| containing: the formatted SQL query (|string|),
		and the ordinal parameters (|list|).
		"""
		if isinstance(sql, unicode):
			string_type = unicode
		elif isinstance(sql, bytes):
			string_type = bytes
			sql = sql.decode(_BYTES_ENCODING)
		else:
			raise TypeError("sql:{!r} is not a unicode or byte string.".format(sql))

		if self.named == 'numeric':
			if isinstance(params, collections.Mapping):
				params = {string_type(idx): val for idx, val in iteritems(params)}
			elif isinstance(params, collections.Sequence) and not isinstance(params, (unicode, bytes)):
				params = {string_type(idx): val for idx, val in enumerate(params, 1)}

		if not isinstance(params, collections.Mapping):
			raise TypeError("params:{!r} is not a dict.".format(params))

		# Find named parameters.
		names = self.match.findall(sql)

		# Map named parameters to ordinals.
		ord_params = []
		name_to_ords = {}
		for name in names:
			value = params[name]
			if isinstance(value, tuple):
				ord_params.extend(value)
				if name not in name_to_ords:
					name_to_ords[name] = '(' + ','.join((self.replace,) * len(value)) + ')'
			else:
				ord_params.append(value)
				if name not in name_to_ords:
					name_to_ords[name] = self.replace

		# Replace named parameters with ordinals.
		sql = self.match.sub(lambda m: name_to_ords[m.group(1)], sql)

		# Make sure the query is returned as the proper string type.
		if string_type is bytes:
			sql = sql.encode(_BYTES_ENCODING)

		# Return formatted SQL and new ordinal parameters.
		return sql, ord_params

	def formatmany(self, sql, many_params):
		"""
		Formats the SQL query to use ordinal parameters instead of named
		parameters.

		*sql* (|string|) is the SQL query.

		*many_params* (|iterable|) contains each *params* to format.

		- *params* (|dict|) maps each named parameter (|string|) to value
		  (|object|). If |self.named| is "numeric", then *params* can be
		  simply a |sequence| of values mapped by index.

		Returns a 2-|tuple| containing: the formatted SQL query (|string|),
		and a |list| containing each ordinal parameters (|list|).
		"""
		if isinstance(sql, unicode):
			string_type = unicode
		elif isinstance(sql, bytes):
			string_type = bytes
			sql = sql.decode(_BYTES_ENCODING)
		else:
			raise TypeError("sql:{!r} is not a unicode or byte string.".format(sql))

		if not isinstance(many_params, collections.Iterable) or isinstance(many_params, (unicode, bytes)):
			raise TypeError("many_params:{!r} is not iterable.".format(many_params))

		# Find named parameters.
		names = self.match.findall(sql)
		name_set = set(names)

		# Map named parameters to ordinals.
		many_ord_params = []
		name_to_ords = {}
		name_to_len = {}
		repl_str = self.replace
		repl_tuple = (repl_str,)
		for i, params in enumerate(many_params):
			if self.named == 'numeric':
				if isinstance(params, collections.Mapping):
					params = {string_type(idx): val for idx, val in iteritems(params)}
				elif isinstance(params, collections.Sequence) and not isinstance(params, (unicode, bytes)):
					params = {string_type(idx): val for idx, val in enumerate(params, 1)}

			if not isinstance(params, collections.Mapping):
				raise TypeError("many_params[{}]:{!r} is not a dict.".format(i, params))

			if not i: # first
				# Map names to ordinals, and determine what names are tuples and
				# what their lengths are.
				for name in name_set:
					value = params[name]
					if isinstance(value, tuple):
						tuple_len = len(value)
						name_to_ords[name] = '(' + ','.join(repl_tuple * tuple_len) + ')'
						name_to_len[name] = tuple_len
					else:
						name_to_ords[name] = repl_str
						name_to_len[name] = None

			# Make sure tuples match up and collapse tuples into ordinals.
			ord_params = []
			for name in names:
				value = params[name]
				tuple_len = name_to_len[name]
				if tuple_len is not None:
					if not isinstance(value, tuple):
						raise TypeError("many_params[{}][{!r}]:{!r} was expected to be a tuple.".format(i, name, value))
					elif len(value) != tuple_len:
						raise ValueError("many_params[{}][{!r}]:{!r} length was expected to be {}.".format(i, name, value, tuple_len))
					ord_params.extend(value)
				else:
					ord_params.append(value)
			many_ord_params.append(ord_params)

		# Replace named parameters with ordinals.
		sql = self.match.sub(lambda m: name_to_ords[m.group(1)], sql)

		# Make sure the query is returned as the proper string type.
		if string_type is bytes:
			sql = sql.encode(_BYTES_ENCODING)

		# Return formatted SQL and new ordinal parameters.
		return sql, many_ord_params
