"""
:mod:`sqlparams` is a utility package for converting between various SQL
parameter styles.
"""
from __future__ import annotations

import re
from typing import (
	Any,
	Dict,  # Replaced by `dict` in 3.9.
	Iterable,  # Replaced by `collections.abc.Iterable` in 3.9.
	List,  # Replaced by `list` in 3.9.
	Optional,  # Replaced by `X | None` in 3.10.
	Pattern,  # Replaced by `re.Pattern` in 3.9.
	Sequence,  # Replaced by `collections.abc.Sequence` in 3.9.
	Tuple,  # Replaced by `tuple` in 3.9.
	Type,  # Replaced by `type` in 3.9.
	Union)  # Replaced by `X | Y` in 3.10.

from . import _converting
from . import _styles
from . import _util
from .typing import (
	TSqlStr)

from ._meta import (
	__author__,
	__copyright__,
	__credits__,
	__license__,
	__version__)

_BYTES_ENCODING = 'latin1'
"""
The encoding to use when parsing a byte query string.
"""

DEFAULT_COMMENTS: Sequence[Union[str, Tuple[str, str]]] = (
	("/*", "*/"),
	"--",
)
"""
The default comment styles to strip. This strips single line comments beginning
with ``"--"`` and multiline comments beginning with ``"/*"`` and ending with
``"*/"``.
"""


class SQLParams(object):
	"""
	The :class:`.SQLParams` class is used to support named parameters in
	SQL queries where they are not otherwise supported (e.g., pyodbc).
	This is done by converting from one parameter style query to another
	parameter style query.

	By default, when converting to a numeric or ordinal style any
	:class:`tuple` parameter will be expanded into "(?,?,...)" to support
	the widely used "IN {tuple}" SQL expression without leaking any
	unescaped values.
	"""

	def __init__(
		self,
		in_style: str,
		out_style: str,
		escape_char: Union[str, bool, None] = None,
		expand_tuples: Optional[bool] = None,
		strip_comments: Union[Sequence[Union[str, Tuple[str, str]]], bool, None] = None,
	) -> None:
		"""
		Instantiates the :class:`.SQLParams` instance.

		*in_style* (:class:`str`) is the parameter style that will be used in an SQL
		query before being parsed and converted to :attr:`.SQLParams.out_style`.

		*out_style* (:class:`str`) is the parameter style that the SQL query will be
		converted to.

		*escape_char* (:class:`str`, :class:`bool`, or ``None``) is the escape
		character used to prevent matching an in-style parameter. If ``True``, use
		the default escape character (repeat the initial character to escape it;
		e.g., "%%"). If ``False``, do not use an escape character. Default is
		``None`` for ``False``.

		*expand_tuples* (:class:`bool` or ``None``) is whether to expand tuples into
		a sequence of parameters. Default is ``None`` to let it be determined by
		*out_style* (to maintain backward compatibility). If *out_style* is a
		numeric or ordinal style, expand tuples by default (``True``). If
		*out_style* is a named style, do not expand tuples by default (``False``).

		.. NOTE:: Empty tuples will be safely expanded to ``(NULL)`` to prevent SQL
		   syntax errors,

		*strip_comments* (:class:`~collections.abc.Sequence`, :class:`bool`, or
		``None``) whether to strip out comments and what style of comments to
		remove. If a :class:`~collections.abc.Sequence`, this defines the comment
		styles. A single line comment is defined using a :class:`str` (e.g., ``"--"``
		or ``"#"``). A multiline comment is defined using a :class:`tuple` of
		:class:`str` (e.g., ``("/*", "*/")``). In order for a comment to be matched,
		it must be the first string of non-whitespace characters on the line.
		Trailing comments are not supported and will be ignored. A multiline comment
		will consume characters until the ending string is matched. If ``True``,
		``DEFAULT_COMMENTS`` will be used (``"--"`` and ``("/*", "*/")`` styles).
		Default is ``None`` to not remove comments.

		The following parameter styles are supported by both *in_style* and
		*out_style*:

		-	For all named styles the parameter keys must be valid `Python identifiers`_.
			They cannot start with a digit. This is to help preven incorrectly
			matching common strings such as date-times.

			Named styles:

			-	"named" indicates parameters will use the named style::

					... WHERE name = :name

			-	"named_dollar" indicates parameters will use the named dollar sign
				style::

					... WHERE name = $name

				.. NOTE:: This is not defined by `PEP 249`_.

			-	"pyformat" indicates parameters will use the named Python extended
				format style::

					... WHERE name = %(name)s

				.. NOTE:: Strictly speaking, `PEP 249`_ only specifies "%(name)s" for
				   the "pyformat" parameter style so only that form (without any other
				   conversions or flags) is supported.

		-	All numeric styles start at ``1``. When using a :class:`~collections.abc.Sequence`
			for the parameters, the 1st parameter (e.g., ":1") will correspond to the
			1st element of the sequence (i.e., index ``0``). When using a
			:class:`~collections.abc.Mapping` for the parameters, the 1st parameter
			(e.g., ":1") will correspond to the matching key (i.e., ``1`` or ``"1"``).

			Numeric styles:

			-	"numeric" indicates parameters will use the numeric style::

					... WHERE name = :1

			-	"numeric_dollar" indicates parameters will use the numeric dollar sign
				style (starts at ``1``)::

					... WHERE name = $1

				.. NOTE:: This is not defined by `PEP 249`_.

		- Ordinal styles:

			-	"format" indicates parameters will use the ordinal Python format style::

					... WHERE name = %s

				.. NOTE:: Strictly speaking, `PEP 249`_ only specifies "%s" for the
				   "format" parameter styles so only that form (without any other
				   conversions or flags) is supported.

			-	"qmark" indicates parameters will use the ordinal question mark style::

					... WHERE name = ?

		.. _`PEP 249`: http://www.python.org/dev/peps/pep-0249/

		.. _`Python identifiers`: https://docs.python.org/3/reference/lexical_analysis.html#identifiers
		"""

		if not isinstance(in_style, str):
			raise TypeError(f"{in_style=!r} is not a string.")

		if not isinstance(out_style, str):
			raise TypeError(f"{out_style=!r} is not a string.")

		in_obj = _styles.STYLES[in_style]
		out_obj = _styles.STYLES[out_style]

		if escape_char is True:
			use_char = in_obj.escape_char
		elif not escape_char:
			use_char = None
		elif isinstance(escape_char, str):
			use_char = escape_char
		else:
			raise TypeError(f"{escape_char=!r} is not a string or bool.")

		if expand_tuples is None:
			expand_tuples = not isinstance(out_obj, _styles.NamedStyle)
		else:
			expand_tuples = bool(expand_tuples)

		if strip_comments is True:
			strip_comments = DEFAULT_COMMENTS
		elif strip_comments is False:
			strip_comments = None

		in_regex = self.__create_in_regex(
			escape_char=use_char,
			in_obj=in_obj,
			out_obj=out_obj,
		)

		self.__converter: _converting.Converter = self.__create_converter(
			escape_char=use_char,
			expand_tuples=expand_tuples,
			in_obj=in_obj,
			in_regex=in_regex,
			in_style=in_style,
			out_obj=out_obj,
			out_style=out_style,
		)
		"""
		*__converter* (:class:`._converting.Converter`) is the parameter converter
		to use.
		"""

		self.__escape_char: Optional[str] = use_char
		"""
		*__escape_char* (:class:`str` or ``None``) is the escape character used to
		prevent matching an in-style parameter.
		"""

		self.__expand_tuples: bool = expand_tuples
		"""
		*__expand_tuples* (:class:`bool`) is whether to convert tuples into a
		sequence of parameters.
		"""

		self.__in_obj: _styles.Style = in_obj
		"""
		*__in_obj* (:class:`._styles.Style`) is the in-style parameter object.
		"""

		self.__in_regex: Pattern = in_regex
		"""
		*__in_regex* (:class:`re.Pattern`) is the regular expression used to extract
		the in-style parameters.
		"""

		self.__in_style: str = in_style
		"""
		*__in_style* (:class:`str`) is the parameter style that will be used in an
		SQL query before being parsed and converted to :attr:`.SQLParams.out_style`.
		"""

		self.__out_obj: _styles.Style = out_obj
		"""
		*__out_obj* (:class:`._styles.Style`) is the out-style parameter object.
		"""

		self.__out_style: str = out_style
		"""
		*__out_style* (:class:`str`) is the parameter style that the SQL query will
		be converted to.
		"""

		self.__strip_comment_regexes: List[Pattern] = self.__create_strip_comment_regexes(
			strip_comments=strip_comments,
		)
		"""
		*__strip_comment_regexes* (:class:`list` of :class:`Pattern`) contains the
		regular expressions to strip out comments.
		"""

		self.__strip_comments: Optional[Sequence[Union[str, Tuple[str, str]]]] = strip_comments
		"""
		*__strip_comments* (:class:`~collections.abc.Sequence` or ``None``) contains
		the comment styles to remove.
		"""

	def __repr__(self) -> str:
		"""
		Returns the canonical string representation (:class:`str`) of this instance.
		"""
		return "{}.{}({!r}, {!r})".format(
			self.__class__.__module__,
			self.__class__.__name__,
			self.__in_style,
			self.__out_style,
		)

	@staticmethod
	def __create_converter(
		escape_char: Optional[str],
		expand_tuples: bool,
		in_obj: _styles.Style,
		in_regex: Pattern,
		in_style: str,
		out_obj: _styles.Style,
		out_style: str,
	) -> _converting.Converter:
		"""
		Create the parameter style converter.

		*escape_char* (:class:`str` or ``None``) is the escape character used to
		prevent matching an in-style parameter.

		*expand_tuples* (:class:`bool`) is whether to convert tuples into a sequence
		of parameters.

		*in_obj* (:class:`._styles.Style`) is the in-style parameter object.

		*in_style* (:class:`str`) is the in-style name.

		*in_regex* (:class:`re.Pattern`) is the regular expression used to extract
		the in-style parameters.

		*out_obj* (:class:`._styles.Style`) is the out-style parameter object.

		*out_style* (:class:`str`) is the out-style name.

		Returns the parameter style converter (:class:`._converting.Converter`).
		"""
		# Determine converter class.
		converter_class: Type[_converting.Converter]
		if isinstance(in_obj, _styles.NamedStyle):
			if isinstance(out_obj, _styles.NamedStyle):
				converter_class = _converting.NamedToNamedConverter
			elif isinstance(out_obj, _styles.NumericStyle):
				converter_class = _converting.NamedToNumericConverter
			elif isinstance(out_obj, _styles.OrdinalStyle):
				converter_class = _converting.NamedToOrdinalConverter
			else:
				raise TypeError(f"{out_style=!r} maps to an unexpected type: {out_obj!r}")

		elif isinstance(in_obj, _styles.NumericStyle):
			if isinstance(out_obj, _styles.NamedStyle):
				converter_class = _converting.NumericToNamedConverter
			elif isinstance(out_obj, _styles.NumericStyle):
				converter_class = _converting.NumericToNumericConverter
			elif isinstance(out_obj, _styles.OrdinalStyle):
				converter_class = _converting.NumericToOrdinalConverter
			else:
				raise TypeError(f"{out_style=!r} maps to an unexpected type: {out_obj!r}")

		elif isinstance(in_obj, _styles.OrdinalStyle):
			if isinstance(out_obj, _styles.NamedStyle):
				converter_class = _converting.OrdinalToNamedConverter
			elif isinstance(out_obj, _styles.NumericStyle):
				converter_class = _converting.OrdinalToNumericConverter
			elif isinstance(out_obj, _styles.OrdinalStyle):
				converter_class = _converting.OrdinalToOrdinalConverter
			else:
				raise TypeError(f"{out_style=!r} maps to an unexpected type: {out_obj!r}")

		else:
			raise TypeError(f"{in_style=!r} maps to an unexpected type: {in_obj!r}")

		# Create converter.
		converter = converter_class(
			escape_char=escape_char,
			expand_tuples=expand_tuples,
			in_regex=in_regex,
			in_style=in_obj,
			out_style=out_obj,
		)
		return converter

	@staticmethod
	def __create_in_regex(
		escape_char: str,
		in_obj: _styles.Style,
		out_obj: _styles.Style,
	) -> Pattern:
		"""
		Create the in-style parameter regular expression.

		*escape_char* (:class:`str` or ``None``) is the escape character to prevent
		matching an in-style parameter.

		*in_obj* (:class:`._styles.Style`) is the in-style parameter object.

		*out_obj* (:class:`._styles.Style`) is the out-style parameter object.

		Returns the in-style parameter regular expression (:class:`re.Pattern`).
		"""
		regex_parts = []

		if in_obj.escape_char != "%" and out_obj.escape_char == "%":
			regex_parts.append("(?P<out_percent>%)")

		if escape_char:
			# Escaping is enabled.
			escape = in_obj.escape_regex.format(char=re.escape(escape_char))
			regex_parts.append(escape)

		regex_parts.append(in_obj.param_regex)

		return re.compile("|".join(regex_parts))

	@staticmethod
	def __create_strip_comment_regexes(
		strip_comments: Optional[Sequence[Union[str, Tuple[str, str]]]],
	) -> List[Pattern]:
		"""
		Create the regular expressions to strip comments.

		*strip_comments* (:class:`~collections.abc.Sequence` or ``None``) contains
		the comment styles to remove.

		Returns the regular expressions (:class:`list` of :class:`re.Pattern`).
		"""
		if strip_comments is None:
			return []

		out_regexes = []
		for i, comment_style in enumerate(strip_comments):
			if isinstance(comment_style, str):
				# Compile regular expression to strip single line comment.
				out_regexes.append(re.compile("^[ \t]*{comment}.*(?:\n|\r\n)?".format(
					comment=re.escape(comment_style),
				), re.M))

			elif _util.is_sequence(comment_style):
				# Compile regular expression to strip multiline comment.
				start_comment, end_comment = comment_style  # type: str
				out_regexes.append(re.compile("^[ \t]*{start}.*?{end}(?:\n|\r\n)?".format(
					start=re.escape(start_comment),
					end=re.escape(end_comment),
				), re.DOTALL | re.M))
				pass

			else:
				raise TypeError(f"strip_comments[{i}]={comment_style!r} must be either a str or tuple.")

		return out_regexes

	@property
	def escape_char(self) -> Optional[str]:
		"""
		*escape_char* (:class:`str` or ``None``) is the escape character used to
		prevent matching an in-style parameter.
		"""
		return self.__escape_char

	@property
	def expand_tuples(self) -> bool:
		"""
		*expand_tuples* (:class:`bool`) is whether to convert tuples into a sequence
		of parameters.
		"""
		return self.__expand_tuples

	def format(
		self,
		sql: TSqlStr,
		params: Union[Dict[Union[str, int], Any], Sequence[Any]],
	) -> Tuple[TSqlStr, Union[Dict[str, Any], Sequence[Any]]]:
		"""
		Convert the SQL query to use the out-style parameters instead of the
		in-style parameters.

		*sql* (:class:`LiteralString`, :class:`str`, or :class:`bytes`) is the SQL
		query.

		*params* (:class:`~collections.abc.Mapping` or :class:`~collections.abc.Sequence`)
		contains the set of in-style parameters. It maps each parameter (:class:`str`
		or :class:`int`) to value. If :attr:`.SQLParams.in_style` is a named
		parameter style. then *params* must be a :class:`~collections.abc.Mapping`.
		If :attr:`.SQLParams.in_style` is an ordinal parameter style, then *params*
		must be a :class:`~collections.abc.Sequence`.

		Returns a :class:`tuple` containing:

		-	The formatted SQL query (:class:`LiteralString`, :class:`str` or :class:`bytes`).

		-	The set of converted out-style parameters (:class:`dict` or :class:`list`).
		"""
		# Normalize query encoding to simplify processing.
		if isinstance(sql, str):
			use_sql = sql
			string_type = str
		elif isinstance(sql, bytes):
			use_sql = sql.decode(_BYTES_ENCODING)
			string_type = bytes
		else:
			raise TypeError(f"{sql=!r} is not a unicode or byte string.")

		# Strip comments.
		use_sql = self.__strip_comments_from_sql(use_sql)

		# Replace in-style with out-style parameters.
		use_sql, out_params = self.__converter.convert(use_sql, params)

		# Make sure the query is returned as the proper string type.
		if string_type is bytes:
			out_sql = use_sql.encode(_BYTES_ENCODING)
		else:
			out_sql = use_sql

		# Return converted SQL and out-parameters.
		return out_sql, out_params

	def formatmany(
		self,
		sql: TSqlStr,
		many_params: Union[Iterable[Dict[Union[str, int], Any]], Iterable[Sequence[Any]]],
	) -> Tuple[TSqlStr, Union[List[Dict[str, Any]], List[Sequence[Any]]]]:
		"""
		Convert the SQL query to use the out-style parameters instead of the
		in-style parameters.

		*sql* (:class:`LiteralString`, :class:`str` or :class:`bytes`) is the SQL
		query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters (*params*).

		-	*params* (:class:`~collections.abc.Mapping` or :class:`~collections.abc.Sequence`)
			contains the set of in-style parameters. It maps each parameter (:class:`str`
			or :class:`int`) to value. If :attr:`.SQLParams.in_style` is a named
			parameter style. then *params* must be a :class:`~collections.abc.Mapping`.
			If :attr:`.SQLParams.in_style` is an ordinal parameter style. then *params*
			must be a :class:`~collections.abc.Sequence`.

		Returns a :class:`tuple` containing:

		-	The formatted SQL query (:class:`LiteralString`, :class:`str` or
			:class:`bytes`).

		-	A :class:`list` containing each set of converted out-style
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
			raise TypeError(f"{sql=!r} is not a unicode or byte string.")

		if not _util.is_iterable(many_params):
			raise TypeError(f"{many_params=!r} is not iterable.")

		# Strip comments.
		use_sql = self.__strip_comments_from_sql(use_sql)

		# Replace in-style with out-style parameters.
		use_sql, many_out_params = self.__converter.convert_many(use_sql, many_params)

		# Make sure the query is returned as the proper string type.
		if string_type is bytes:
			out_sql = use_sql.encode(_BYTES_ENCODING)
		else:
			out_sql = use_sql

		# Return converted SQL and out-parameters.
		return out_sql, many_out_params

	@property
	def in_style(self) -> str:
		"""
		*in_style* (:class:`str`) is the parameter style to expect in an SQL query
		when being parsed.
		"""
		return self.__in_style

	@property
	def out_style(self) -> str:
		"""
		*out_style* (:class:`str`) is the parameter style that the SQL query will be
		converted to.
		"""
		return self.__out_style

	@property
	def strip_comments(self) -> Optional[Sequence[Union[str, Tuple[str, str]]]]:
		"""
		*strip_comments* (:class:`~collections.abc.Sequence` or ``None``) contains
		the comment styles to remove.
		"""
		return self.__strip_comments

	def __strip_comments_from_sql(self, sql: str) -> str:
		"""
		Strip comments from the SQL.

		*sql* (:class:`str`) is the SQL query.

		Returns the stripped SQL query (:class:`str`).
		"""
		out_sql = sql
		for comment_regex in self.__strip_comment_regexes:
			out_sql = comment_regex.sub("", out_sql)

		return out_sql
