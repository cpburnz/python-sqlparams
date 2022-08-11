"""
This module contains internal classes for defining parameter styles.
"""

from typing import Dict

STYLES: Dict[str, 'Style'] = {}
"""
Maps parameter style by name.
"""


class Style(object):
	"""
	The :class:`.Style` class is the base class used to define a parameter
	style.
	"""

	def __init__(
		self,
		name: str,
		escape_char: str,
		escape_regex: str,
		out_format: str,
		param_regex: str,
	) -> None:
		"""
		Initializes the :class:`.Style` instances.
		"""

		self.escape_char: str = escape_char
		"""
		*escape_char* (:class:`str`) is the escape character used to prevent
		matching a parameter.
		"""

		self.escape_regex: str = escape_regex
		"""
		*escape_regex* (:class:`str`) is the regular expression used to
		match the escape sequence.
		"""

		self.name: str = name
		"""
		*name* (:class:`str`) is the name of the parameter style.
		"""

		self.out_format: str = out_format
		"""
		*out_format* (:class:`str`) is the out-style parameter format
		string.
		"""

		self.param_regex: str = param_regex
		"""
		*param_regex* (:class:`str`) is the regular expression used to
		extract the parameter.
		"""


class NamedStyle(Style):
	"""
	The :class:`.NamedStyle` class is used to define a named parameter
	style.
	"""
	pass


class NumericStyle(Style):
	"""
	The :class:`.NumericStyle` class is used to define a numeric parameter
	style.
	"""

	def __init__(self, start: int, **kw) -> None:
		"""
		Initializes the :class:`.NumericStyle` instances.
		"""
		super().__init__(**kw)

		self.start: int = start
		"""
		*start* (:class:`int`) indicates to start enumerating arguments at
		the specified number (e.g., :data:`1` or :data:`0`).
		"""


class OrdinalStyle(Style):
	"""
	The :class:`.OrdinalStyle` class is used to define an ordinal
	parameter style.
	"""
	pass


# Define standard "format" parameter style.
STYLES['format'] = OrdinalStyle(
	name="format",
	escape_char="%",
	escape_regex="(?P<escape>{char}%)",
	param_regex="(?<!%)%s",
	out_format="%s",
)

# Define standard "named" parameter style.
STYLES['named'] = NamedStyle(
	name="named",
	escape_char=":",
	escape_regex="(?P<escape>{char}:)",
	param_regex="(?<!:):(?P<param>[A-Za-z_]\\w*)",
	out_format=":{param}"
)

# Define non-standard "named_dollar" parameter style.
STYLES['named_dollar'] = NamedStyle(
	name="named_dollar",
	escape_char="$",
	escape_regex="(?P<escape>{char}\\$)",
	param_regex="(?<!\\$)\\$(?P<param>[A-Za-z_]\\w*)",
	out_format="${param}",
)

# Define standard "numeric" parameter style.
STYLES['numeric'] = NumericStyle(
	name="numeric",
	escape_char=":",
	escape_regex="(?P<escape>{char}:)",
	param_regex="(?<!:):(?P<param>\\d+)",
	out_format=":{param}",
	start=1,
)

# Define non-standard "numeric_dollar" parameter style.
STYLES['numeric_dollar'] = NumericStyle(
	name="numeric_dollar",
	escape_char="$",
	escape_regex="(?P<escape>{char}\\$)",
	param_regex="(?<!\\$)\\$(?P<param>\\d+)",
	out_format="${param}",
	start=1,
)

# Define standard "pyformat" parameter style.
STYLES['pyformat'] = NamedStyle(
	name="pyformat",
	escape_char="%",
	escape_regex="(?P<escape>{char}%)",
	param_regex="(?<!%)%\\((?P<param>[A-Za-z_]\\w*)\\)s",
	out_format="%({param})s",
)

# Define standard "qmark" parameter style.
STYLES['qmark'] = OrdinalStyle(
	name="qmark",
	escape_char="?",
	escape_regex="(?P<escape>{char}\\?)",
	param_regex="(?<!\\?)\\?(?!\\?)",
	out_format="?",
)
