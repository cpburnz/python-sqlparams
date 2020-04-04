"""
:mod:`sqlparams` is a utility package for converting between various SQL
parameter styles.
"""

import re

from . import _converting
from . import _styles
from ._util import _is_iterable

from ._meta import (
	__author__,
	__copyright__,
	__credits__,
	__license__,
	__version__,
)

#: The encoding to use when parsing a byte query string.
_BYTES_ENCODING = 'latin1'

#: Maps parameter style by name.
_STYLES = {}


class SQLParams(object):
	"""
	The :class:`.SQLParams` class is used to support named parameters in
	SQL queries where they are not otherwise supported (e.g., pyodbc).
	This is done by converting from one parameter style query to another
	parameter style query..

	By default when converting to a numeric or ordinal style any
	:class:`tuple` parameter will be expanded into "(?,?,...)" to support
	the widely used "IN {tuple}" SQL expression without leaking any
	unescaped values.
	"""

	def __init__(self, in_style=None, out_style=None, escape_char=None, expand_tuples=None):
		"""
		Instantiates the :class:`.SQLParams` instance.

		*in_style* (:class:`str`) is the parameter style that will be used
		in an SQL query before being parsed and converted to :attr:`.SQLParams.out_style`.

		*out_style* (:class:`str`) is the parameter style that the SQL query
		will be converted to.

		*escape_char* (:class:`str`, :class:`bool`, or :data:`None`) is the
		escape character used to prevent matching a in-style parameter. If
		:data:`True`, use the default escape character (repeat the initial
		character to escape it; e.g., "%%"). If :data:`False`, do not use an
		escape character. Default is :data:`None` for :data:`False`.

		*expand_tuples* (:class:`bool` or :data:`None`) is whether to
		expand tuples into a sequence of parameters. Default is :data:`None`
		to let it be determined by *out_style* (to maintain backward). If
		*out_style* is a numeric or ordinal style, expand tuples by default
		(:data:`True`). If *out_style* is a named style, do not expand
		tuples by default (:data:`False`).

		The following parameter styles are supported by both *in_style* and
		*out_style*:

		- For all named styles the parameter keys must be valid `Python identifiers`_.
		  They cannot start with a digit. This is to help prevent
		  incorrectly matching common strings such as datetimes.

		  Named styles:

		  - "named" indicates parameters will use the named style::

		      ... WHERE name = :name

		  - "named_dollar" indicates parameters will use the named dollar
		    sign style::

		      ... WHERE name = $name

		    .. NOTE:: This is not defined by `PEP 249`_.

		  - "pyformat" indicates parameters will use the named Python
		    extended format style::

		      ... WHERE name = %(name)s

		    .. NOTE:: Strictly speaking, `PEP 249`_ only specifies
		       "%(name)s" for the "pyformat" parameter style so only that
		       form (without any other conversions or flags) is supported.

		- All numeric styles start at :data:`1`. When using a
		  :class:`~collections.abc.Sequence` for the parameters, the 1st
		  parameter (e.g., ":1") will correspond to the 1st element of the
		  sequence (i.e., index :data:`0`). When using a :class:`~collections.abc.Mapping`
		  for the parameters, the 1st parameter (e.g., ":1") will correspond
		  to the matching key (i.e., :data:`1` or :data:`"1"`).

		  Numeric styles:

		  - "numeric" indicates parameters will use the numeric style::

		      ... WHERE name = :1

		  - "numeric_dollar" indicates parameters will use the numeric
		    dollar sign style (starts at :data:`1`)::

		      ... WHERE name = $1

		    .. NOTE:: This is not defined by `PEP 249`_.

		- Ordinal styles:

		  - "format" indicates parameters will use the ordinal Python format
		    style::

		      ... WHERE name = %s

		    .. NOTE:: Strictly speaking, `PEP 249`_ only specifies "%s" for
		       the "format" parameter styles so only that form (without any
		       other conversions or flags) is supported.

		  - "qmark" indicates parameters will use the ordinal question mark
		    style::

		      ... WHERE name = ?

		.. _`PEP 249`: http://www.python.org/dev/peps/pep-0249/

		.. _`Python identifiers`: https://docs.python.org/3/reference/lexical_analysis.html#identifiers
		"""

		self._converter = None
		"""
		*_converter* (:class:`._converting._Converter`) is the parameter
		converter to use.
		"""

		self._escape_char = None
		"""
		*_escape_char* (:class:`str` or :data:`None`) is the escape
		character used to prevent matching a in-style parameter.
		"""

		self._expand_tuples = None
		"""
		*_expand_tuples* (:class:`bool`) is whether to convert tuples into a
		sequence of parameters.
		"""

		self._in_obj = None
		"""
		*_in_obj* (:class:`._styles._Style`) is the in-style parameter object.
		"""

		self._in_regex = None
		"""
		*_in_regex* (:class:`re.Pattern`) is the regular expression used to
		extract the in-style parameters.
		"""

		self._in_style = None
		"""
		*_in_style* (:class:`str`) is the parameter style that will be used
		in an SQL query before being parsed and converted to :attr:`.SQLParams.out_style`.
		"""

		self._out_obj = None
		"""
		*_out_obj* (:class:`._styles._Style`) is the out-style parameter object.
		"""

		self._out_style = None
		"""
		*_out_style* (:class:`str`) is the parameter style that the SQL query
		will be converted to.
		"""

		if not isinstance(in_style, str):
			raise TypeError("in_style:{!r} is not a string.".format(in_style))

		if not isinstance(out_style, str):
			raise TypeError("out_style:{!r} is not a string.".format(out_style))

		self._in_style = in_style
		self._out_style = out_style

		self._in_obj = _styles._STYLES[self._in_style]
		self._out_obj = _styles._STYLES[self._out_style]

		if escape_char is True:
			use_char = self._in_obj.escape_char
		elif not escape_char:
			use_char = None
		elif isinstance(escape_char, str):
			use_char = escape_char
		else:
			raise TypeError("escape_char:{!r} is not a string or bool.")

		if expand_tuples is None:
			expand_tuples = not isinstance(self._out_obj, _styles._NamedStyle)

		self._escape_char = use_char
		self._expand_tuples = bool(expand_tuples)

		# TODO: Enable expand tuples when converting to numeric or ordinal.

		self._in_regex = self._create_in_regex()
		self._converter = self._create_converter()

	def __repr__(self):
		"""
		Returns the canonical string representation (:class:`str`) of this
		instance.
		"""
		return "{}.{}({!r}, {!r})".format(self.__class__.__module__, self.__class__.__name__, self._in_style, self._out_style)

	def _create_converter(self):
		"""
		Create the parameter style converter.

		Returns the parameter style converter (:class:`._converting._Converter`).
		"""
		assert self._in_regex is not None, self._in_regex
		assert self._out_obj is not None, self._out_obj

		# Determine converter class.
		if isinstance(self._in_obj, _styles._NamedStyle):
			if isinstance(self._out_obj, _styles._NamedStyle):
				converter_class = _converting._NamedToNamedConverter
			elif isinstance(self._out_obj, _styles._NumericStyle):
				converter_class = _converting._NamedToNumericConverter
			elif isinstance(self._out_obj, _styles._OrdinalStyle):
				converter_class = _converting._NamedToOrdinalConverter
			else:
				raise TypeError("out_style:{!r} maps to an unexpected type: {!r}".format(self._out_style, self._out_obj))

		elif isinstance(self._in_obj, _styles._NumericStyle):
			if isinstance(self._out_obj, _styles._NamedStyle):
				converter_class = _converting._NumericToNamedConverter
			elif isinstance(self._out_obj, _styles._NumericStyle):
				converter_class = _converting._NumericToNumericConverter
			elif isinstance(self._out_obj, _styles._OrdinalStyle):
				converter_class = _converting._NumericToOrdinalConverter
			else:
				raise TypeError("out_style:{!r} maps to an unexpected type: {!r}".format(self._out_style, self._out_obj))

		elif isinstance(self._in_obj, _styles._OrdinalStyle):
			if isinstance(self._out_obj, _styles._NamedStyle):
				converter_class = _converting._OrdinalToNamedConverter
			elif isinstance(self._out_obj, _styles._NumericStyle):
				converter_class = _converting._OrdinalToNumericConverter
			elif isinstance(self._out_obj, _styles._OrdinalStyle):
				converter_class = _converting._OrdinalToOrdinalConverter
			else:
				raise TypeError("out_style:{!r} maps to an unexpected type: {!r}".format(self._out_style, self._out_obj))

		else:
			raise TypeError("in_style:{!r} maps to an unexpected type: {!r}".format(self._in_style, self._in_obj))

		# Create converter.
		converter = converter_class(
			escape_char=self._escape_char,
			expand_tuples=self._expand_tuples,
			in_regex=self._in_regex,
			in_style=self._in_obj,
			out_style=self._out_obj,
		)
		return converter

	def _create_in_regex(self):
		"""
		Create the in-style parameter regular expression.

		Returns the in-style parameter regular expression (:class:`re.Pattern`).
		"""
		if self.escape_char:
			# Escaping is enabled.
			return re.compile("{}|{}".format(
				self._in_obj.escape_regex.format(char=re.escape(self.escape_char)),
				self._in_obj.param_regex,
			))

		else:
			# Escaping is disabled.
			return re.compile(self._in_obj.param_regex)

	@property
	def escape_char(self):
		"""
		*escape_char* (:class:`str` or :data:`None`) is the escape character
		used to prevent matching a in-style parameter.
		"""
		return self._escape_char

	@property
	def expand_tuples(self):
		"""
		*expand_tuples* (:class:`bool`) is whether to convert tuples into a
		sequence of parameters.
		"""
		return self._expand_tuples

	def format(self, sql, params):
		"""
		Convert the SQL query to use the out-style parameters instead of
		the in-style parameters.

		*sql* (:class:`str` or :class:`bytes`) is the SQL query.

		*params* (:class:`~collections.abc.Mapping` or :class:`~collections.abc.Sequence`)
		contains the set of in-style parameters. It maps each parameter
		(:class:`str` or :class:`int`) to value. If :attr:`.SQLParams.in_style`
		is a named parameter style. then *params* must be a :class:`~collections.abc.Mapping`.
		If :attr:`.SQLParams.in_style` is an ordinal parameter style, then
		*params* must be a :class:`~collections.abc.Sequence`.

		Returns a :class:`tuple` containing:

		- The formatted SQL query (:class:`str` or :class:`bytes`).

		- The set of converted out-style parameters (:class:`dict` or
		  :class:`list`).
		"""
		# Normalize query encoding to simplify processing.
		if isinstance(sql, str):
			use_sql = sql
			string_type = str
		elif isinstance(sql, bytes):
			use_sql = sql.decode(_BYTES_ENCODING)
			string_type = bytes
		else:
			raise TypeError("sql:{!r} is not a unicode or byte string.".format(sql))

		# Replace in-style with out-style parameters.
		use_sql, out_params = self._converter.convert(use_sql, params)

		# Make sure the query is returned as the proper string type.
		if string_type is bytes:
			out_sql = use_sql.encode(_BYTES_ENCODING)
		else:
			out_sql = use_sql

		# Return converted SQL and out-parameters.
		return out_sql, out_params

	def formatmany(self, sql, many_params):
		"""
		Convert the SQL query to use the out-style parameters instead of the
		in-style parameters.

		*sql* (:class:`str` or :class:`bytes`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set
		of in-style parameters (*params*).

		- *params* (:class:`~collections.abc.Mapping` or :class:`~collections.abc.Sequence`)
		  contains the set of in-style parameters. It maps each parameter
		  (:class:`str` or :class:`int`) to value. If :attr:`.SQLParams.in_style`
		  is a named parameter style. then *params* must be a :class:`~collections.abc.Mapping`.
		  If :attr:`.SQLParams.in_style` is an ordinal parameter style. then
		  *params* must be a :class:`~collections.abc.Sequence`.

		Returns a :class:`tuple` containing:

		- The formatted SQL query (:class:`str` or :class:`bytes`).

		- A :class:`list` containing each set of converted out-style
		  parameters (:class:`dict` or :class:`list`).
		"""
		# Normalize query encoding to simplify processing.
		if isinstance(sql, str):
			use_sql = sql
			string_type = str
		elif isinstance(sql, bytes):
			use_sql = sql.decode(_BYTES_ENCODING)
			string_type = bytes
		else:
			raise TypeError("sql:{!r} is not a unicode or byte string.".format(sql))

		if not _is_iterable(many_params):
			raise TypeError("many_params:{!r} is not iterable.".format(many_params))

		# Replace in-style with out-style parameters.
		use_sql, many_out_params = self._converter.convert_many(use_sql, many_params)

		# Make sure the query is returned as the proper string type.
		if string_type is bytes:
			out_sql = use_sql.encode(_BYTES_ENCODING)
		else:
			out_sql = use_sql

		# Return converted SQL and out-parameters.
		return out_sql, many_out_params

	@property
	def in_style(self):
		"""
		*in_style* (:class:`str`) is the parameter style to expect in an SQL
		query when being parsed.
		"""
		return self._in_style

	@property
	def out_style(self):
		"""
		*out_style* (:class:`str`) is the parameter style that the SQL query
		will be converted to.
		"""
		return self._out_style
