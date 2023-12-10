"""
This module defines type hints.
"""
from __future__ import annotations

from typing import (
	TypeVar,
	Union)  # Replaced by `X | Y` in 3.10.

# LiteralString: Python 3.11+
try:
	from typing import LiteralString
except ImportError:
	try:
		from typing_extensions import LiteralString
	except ImportError:
		LiteralString = str

TSqlStr = TypeVar('TSqlStr', bound=Union[LiteralString, str, bytes])
"""
Constrained type variable for SQL strings (:class:`LiteralString`,
:class:`str`, :class:`bytes`).
"""

