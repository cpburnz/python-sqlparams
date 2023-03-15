SQL Params
==========

*sqlparams* is a utility package for converting between various SQL
parameter styles. This can simplify the use of SQL parameters in queries by
allowing the use of named parameters where only ordinal are supported. Some
`Python DB API 2.0`_ compliant modules only support the ordinal *qmark* or
*format* style parameters (e.g., `pyodbc`_ only supports *qmark*). This
package provides a helper class, `SQLParams`_, that is used to convert
from any parameter style (*qmark*, *numeric*, *named*, *format*, *pyformat*;
and the non-standard *numeric_dollar* and *named_dollar*), and have them
safely converted to the desired parameter style.

.. _`Python DB API 2.0`: http://www.python.org/dev/peps/pep-0249/
.. _`pyodbc`: https://github.com/mkleehammer/pyodbc


Tutorial
--------

You first create an `SQLParams`_ instance specifying the named
parameter style you're converting from, and what ordinal style you're
converting to. Let's convert from *named* to *qmark* style::

  >>> import sqlparams
  >>> query = sqlparams.SQLParams('named', 'qmark')

Now, lets to convert a simple SQL SELECT query using the `SQLParams.format`_
method which accepts an SQL query, and a *dict* of parameters::

  >>> sql, params = query.format('SELECT * FROM users WHERE name = :name;', {'name': "Thorin"})

This returns the new SQL query using ordinal *qmark* parameters with the
corresponding list of ordinal parameters, which can be passed to the
`.execute()`_ method on a database cursor::

  >>> print sql
  SELECT * FROM users WHERE name = ?;
  >>> print params
  ['Thorin']

.. _`.execute()`: http://www.python.org/dev/peps/pep-0249/#id15

*tuple*\ s are also supported which allows for safe use of the SQL IN
operator::

  >>> sql, params = query.format("SELECT * FROM users WHERE name IN :names;", {'names': ("Dori", "Nori", "Ori")})
  >>> print sql
  SELECT * FROM users WHERE name in (?,?,?);
  >>> print params
  ['Dori', 'Nori', 'Ori']

You can also format multiple parameters for a single, shared query useful with
the `.executemany()`_ method of a database cursor::

  >>> sql, manyparams = query.formatmany("UPDATE users SET age = :age WHERE name = :name;", [{'name': "Dwalin", 'age': 169}, {'name': "Balin", 'age': 178}])
  >>> print sql
  UPDATE users SET age = ? WHERE name = ?;
  >>> print manyparams
  [[169, 'Dwalin'], [178, 'Balin']]

.. _`.executemany()`: http://www.python.org/dev/peps/pep-0249/#executemany

Please note that if an expanded *tuple* is used in `SQLParams.formatmany`_,
the tuple must be the same size in each of the parameter lists. Otherwise, you
might well use `SQLParams.format`_ in a for-loop.


Source
------

The source code for *sqlparams* is available from the GitHub repo
`cpburnz/python-sql-parameters`_.

.. _`cpburnz/python-sql-parameters`: https://github.com/cpburnz/python-sql-parameters.git


Installation
------------

*sqlparams* can be installed from source with::

  python setup.py install

*sqlparams* is also available for install through `PyPI`_::

  pip install sqlparams

.. _`PyPI`: http://pypi.python.org/pypi/sqlparams


Documentation
-------------

Documentation for *sqlparams* is available on `Read the Docs`_.

.. _`Read the Docs`: https://python-sql-parameters.readthedocs.org

.. _`SQLParams`: https://python-sql-parameters.readthedocs.io/en/latest/sqlparams.html#sqlparams.SQLParams
.. _`SQLParams.format`: https://python-sql-parameters.readthedocs.io/en/latest/sqlparams.html#sqlparams.SQLParams.format
.. _`SQLParams.formatmany`: https://python-sql-parameters.readthedocs.io/en/latest/sqlparams.html#sqlparams.SQLParams.formatmany



Change History
==============


5.1.0 (2023-03-14)
------------------

Improvements:

- Support `LiteralString`_.

.. _`LiteralString`: https://docs.python.org/3/library/typing.html#typing.LiteralString


5.0.0 (2022-08-11)
------------------

- Dropped support of EOL Python 3.6.
- Support Python 3.11.
- Changed build system to `pyproject.toml`_ and build backend to `setuptools.build_meta`_ which may have unforeseen consequences.
- Safely expand empty tuples. Fixes `Issue #8`_.
- Add support for stripping comments. This helps prevent expansion of unexpected variables in comments. Fixes `Issue #9`_.
- Rename GitHub project from `python-sql-parameters`_ to `python-sqlparams`_.

.. _`pyproject.toml`: https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/
.. _`setuptools.build_meta`: https://setuptools.pypa.io/en/latest/build_meta.html
.. _`Issue #8`: https://github.com/cpburnz/python-sqlparams/issues/8
.. _`Issue #9`: https://github.com/cpburnz/python-sqlparams/issues/9
.. _`python-sql-parameters`: https://github.com/cpburnz/python-sql-parameters
.. _`python-sqlparams`: https://github.com/cpburnz/python-sqlparams


4.0.0 (2022-06-06)
------------------

- Drop support for EOL Python 3.5.
-	`Issue #10`_: When converting to 'format'/'pyformat' types, escape existing '%' characters.
-	When converting from 'format'/'pyformat' types, set `escape_char=True` to unescape double '%' characters.

.. _`Issue #10`: https://github.com/cpburnz/python-sqlparams/issues/10



3.0.0 (2020-04-04)
------------------

- Major changes to internal implementation.
- Support converting any parameter style to any parameter style (all named,
  numeric, and ordinal styles).
- Renamed attribute `named` to `in_style` on `sqlparams.SQLParams`.
- Renamed attribute `ordinal` to `out_style` on `sqlparams.SQLParams`.
- Removed attributes `match` and `replace` from `sqlparams.SQLParams` which
  should have been private.
- Named parameters must now be valid identifiers (can no longer start with a
  digit to help prevent incorrectly matching common strings such as
  datetimes). Fixes `Issue #4`_.
- `Issue #7`_: Support dollar sign style for numeric and named parameters.

.. _`Issue #4`: https://github.com/cpburnz/python-sqlparams/issues/4
.. _`Issue #7`: https://github.com/cpburnz/python-sqlparams/issues/7


2.0.0 (2020-02-26)
------------------

- Drop support for EOL Python 2.7, 3.2, 3.3, 3.4.


1.2.0 (2020-02-26)
------------------

- Require setuptools.
- Support up to Python 3.8.


1.1.2 (2018-05-04)
------------------

- Improved support for byte strings.


1.1.1 (2017-09-07)
------------------

- Fixed support for byte strings.


1.1.0 (2017-08-30)
------------------

- Support Python 3.2+.


1.0.3 (2012-12-28)
------------------

- Fixed documentation for `issue 1`_.

.. _`issue 1`: https://github.com/cpburnz/python-sqlparams/issues/1


1.0.2 (2012-12-22)
------------------

- Added sphinx documentation.


1.0.1 (2012-12-20)
------------------

- Fixed running test as a script.


1.0.0 (2012-12-20)
------------------

- Initial release.
