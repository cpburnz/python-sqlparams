
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
