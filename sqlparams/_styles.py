"""
This module contains internal classes for defining parameter styles.
"""

#: Maps parameter style by name.
_STYLES = {}


class _Style(object):
	"""
	The :class:`._Style` class is the base class used to define a
	parameter style.
	"""

	def __init__(self, name, escape_char, escape_regex, out_format, param_regex):
		"""
		Initializes the :class:`._Style` instances.
		"""

		self.escape_char = escape_char
		"""
		*escape_char* (:class:`str`) is the escape character used to prevent
		matching a parameter.
		"""

		self.escape_regex = escape_regex
		"""
		*escape_regex* (:class:`str`) is the regular expression used to
		match the escape sequence.
		"""

		self.name = name
		"""
		*name* (:class:`str`) is the name of the parameter style.
		"""

		self.out_format = out_format
		"""
		*out_format* (:class:`str`) is the out-style parameter format
		string.
		"""

		self.param_regex = param_regex
		"""
		*param_regex* (:class:`str`) is the regular expression used to
		extract the parameter.
		"""


class _NamedStyle(_Style):
	"""
	The :class:`._NamedStyle` class is used to define a named parameter
	style.
	"""
	pass


class _NumericStyle(_Style):
	"""
	The :class:`._NumericStyle` class is used to define a numeric
	parameter style.
	"""

	def __init__(self, start, **kw):
		"""
		Initializes the :class:`._OrdinalStyle` instances.
		"""
		super().__init__(**kw)

		self.start = start
		"""
		*start* (:class:`int`) indicates to start enumerating arguments at
		the specified number (e.g., :data:`1` or :data:`0`).
		"""


class _OrdinalStyle(_Style):
	"""
	The :class:`._OrdinalStyle` class is used to define an ordinal
	parameter style.
	"""
	pass


# Define standard "format" parameter style.
_STYLES['format'] = _OrdinalStyle(
	name="format",
	escape_char="%",
	escape_regex="(?P<escape>{char}%)",
	param_regex="(?<!%)%s",
	out_format="%s",
)

# Define standard "named" parameter style.
_STYLES['named'] = _NamedStyle(
	name="named",
	escape_char=":",
	escape_regex="(?P<escape>{char}:)",
	param_regex="(?<!:):(?P<param>[A-Za-z_]\\w*)",
	out_format=":{param}"
)

# Define non-standard "named_dollar" parameter style.
_STYLES['named_dollar'] = _NamedStyle(
	name="named_dollar",
	escape_char="$",
	escape_regex="(?P<escape>{char}\\$)",
	param_regex="(?<!\\$)\\$(?P<param>[A-Za-z_]\\w*)",
	out_format="${param}",
)

# Define standard "numeric" parameter style.
_STYLES['numeric'] = _NumericStyle(
	name="numeric",
	escape_char=":",
	escape_regex="(?P<escape>{char}:)",
	param_regex="(?<!:):(?P<param>\\d+)",
	out_format=":{param}",
	start=1,
)

# Define non-standard "numeric_dollar" parameter style.
_STYLES['numeric_dollar'] = _NumericStyle(
	name="numeric_dollar",
	escape_char="$",
	escape_regex="(?P<escape>{char}\\$)",
	param_regex="(?<!\\$)\\$(?P<param>\\d+)",
	out_format="${param}",
	start=1,
)

# Define standard "pyformat" parameter style.
_STYLES['pyformat'] = _NamedStyle(
	name="pyformat",
	escape_char="%",
	escape_regex="(?P<escape>{char}%)",
	param_regex="(?<!%)%\\((?P<param>[A-Za-z_]\\w*)\\)s",
	out_format="%({param})s",
)

# Define standard "qmark" parameter style.
_STYLES['qmark'] = _OrdinalStyle(
	name="qmark",
	escape_char="?",
	escape_regex="(?P<escape>{char}\\?)",
	param_regex="(?<!\\?)\\?(?!\\?)",
	out_format="?",
)
