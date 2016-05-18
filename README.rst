
*sqlparams*: SQL Parameters
===========================

*sqlparams* is a utility module for simplifying the use of SQL
parameters in queries. Some `Python DB API 2.0`_ compliant modules only
support the ordinal *qmark* or *format* style parameters (e.g., pyodbc_
only supports *qmark*). This utility module provides a helper class,
*SQLParams*, that is used to support named parameter styles such as
*named*, *numeric* and *pyformat*, and have them safely converted to the
desired ordinal style.

.. _`Python DB API 2.0`: http://www.python.org/dev/peps/pep-0249/
.. _pyodbc: http://code.google.com/p/pyodbc/


Tutorial
--------

You first create an *SQLParams* instance specifying the named
parameter style you're converting from, and what ordinal style you're
converting to. Let's convert from *named* to *qmark* style::

  >>> import sqlparams
  >>> query = sqlparams.SQLParams('named', 'qmark')

Now, lets to convert a simple SQL SELECT query using the *.format()*
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

You can also format multiple parameters for a single, shared query
useful with the `.executemany()`_ method of a database cursor::

  >>> sql, manyparams = query.formatmany("UPDATE users SET age = :age WHERE name = :name;", [{'name': "Dwalin", 'age': 169}, {'name': "Balin", 'age': 178}])
  >>> print sql
  UPDATE users SET age = ? WHERE name = ?;
  >>> print manyparams
  [[169, 'Dwalin'], [178, 'Balin']]
  
.. _`.executemany()`: http://www.python.org/dev/peps/pep-0249/#executeman
  
Please note that if a tuple is used in *.formatmany()*, the tuple must
be the same size in each of the parameter lists. Otherwise, you might
well use *.format()* in a for-loop.


Source
------

The source code for *sqlparams* is available from the GitHub repo
`cpburnz/python-sql-parameters`_.

.. _`cpburnz/python-sql-parameters`: https://github.com/cpburnz/python-sql-parameters.git


Installation
------------

*sqlparams* can be installed from source with::

  python setup.py install
  
*sqlparams* is also available for install through PyPI_::

  pip install sqlparams
  
.. _PyPI: http://pypi.python.org/pypi/sqlparams


Documentation
-------------

Documentation for *sqlparams* is available on `Read the Docs`_.

.. _`Read the Docs`: https://python-sql-parameters.readthedocs.org
