"""
This module defines internal utility methods.
"""

from collections.abc import (
	Iterable,
	Sequence)
from typing import (
	TypeVar)

# LiteralString: Python 3.11+
try:
	from typing import LiteralString
except ImportError:
	try:
		from typing_extensions import LiteralString
	except ImportError:
		LiteralString = str

SqlStr = TypeVar('SqlStr', LiteralString, str, bytes)
"""
Constrained type variable for SQL strings (:class:`LiteralString`,
:class:`str`, :class:`bytes`).
"""


def is_iterable(value):
	"""
	Check whether the value is an iterable (excludes strings).

	*value* is the value to check,

	Returns whether *value* is a iterable (:class:`bool`).
	"""
	return isinstance(value, Iterable) and not isinstance(value, (str, bytes))


def is_sequence(value):
	"""
	Check whether the value is a sequence (excludes strings).

	*value* is the value to check,

	Returns whether *value* is a sequence (:class:`bool`).
	"""
	return isinstance(value, Sequence) and not isinstance(value, (str, bytes))
