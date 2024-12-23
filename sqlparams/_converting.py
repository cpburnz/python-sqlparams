"""
This module contains internal classes used for converting parameter styles.
"""

import itertools
from collections.abc import (
	Mapping)
from functools import (
	partial)
from typing import (
	Any,
	Dict,  # Replaced by `dict` in 3.9.
	Iterable,  # Replaced by `collections.abc.Iterable` in 3.9.
	Iterator,  # Replaced by `collections.abc.Iterator` in 3.9.
	List,  # Replaced by `list` in 3.9.
	Match,  # Replaced by `re.Match` in 3.9.
	Optional,  # Replaced by `X | None` in 3.10.
	Pattern,  # Replaced by `re.Pattern` in 3.9.
	Sequence,  # Replaced by `collections.abc.Sequence` in 3.9.
	Tuple,  # Replaced by `tuple` in 3.9.
	Union)  # Replaced by `X | Y` in 3.10.

from . import _styles
from ._util import (
	is_sequence)


class Converter(object):
	"""
	The :class:`.Converter` class is the base class for implementing the
	conversion from one in-style parameter to another out-style parameter.
	"""

	def __init__(
		self,
		escape_char: Optional[str],
		expand_tuples: bool,
		in_regex: Pattern[str],
		in_style: _styles.Style,
		out_style: _styles.Style,
		allow_out_quotes: bool,
	) -> None:
		"""
		Initializes the :class:`.Converter` instance.
		"""

		self._escape_start = len(escape_char) if escape_char is not None else 0
		"""
		*_escape_start* (:class:`int`) is the offset used to skip the escape
		character.
		"""

		self._expand_tuples: bool = expand_tuples
		"""
		*_expand_tuples* (:class:`bool`) is whether to convert tuples into a
		sequence of parameters.
		"""

		self._in_regex: Pattern[str] = in_regex
		"""
		*_in_regex* (:class:`re.Pattern`) is the regular expression used to extract
		the in-style parameters.
		"""

		self._in_style: _styles.Style = in_style
		"""
		*_in_style* (:class:`._styles.Style`) is the in-style to use.
		"""

		self._out_format = out_style.out_format
		"""
		*_out_format* (:class:`str`) is the out-style parameter format
		string.
		"""

		self._out_quotes: bool = out_style.param_quotes and allow_out_quotes
		"""
		*_out_quotes* (:class:`bool`) whether to enclose out parameters in double
		quotes.
		"""

		self._out_style: _styles.Style = out_style
		"""
		*_out_style* (:class:`._styles.Style`) is the out-style to use.
		"""

	def convert(
		self,
		sql: str,
		params: Union[Dict[Union[str, int], Any], Sequence[Any]],
	) -> Tuple[str, Union[Dict[str, Any], Sequence[Any]]]:
		"""
		Convert the SQL query to use the named out-style parameters from the named
		the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Mapping` or :class:`~collections.abc.Sequence`)
		contains the set of in-style parameters.

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the out-style parameters (:class:`dict` or :class:`list`).
		"""
		raise NotImplementedError(f"{self.__class__.__qualname__} must implement convert().")

	def convert_many(
		self,
		sql: str,
		many_params: Union[Iterable[Dict[Union[str, int], Any]], Iterable[Sequence[Any]]],
	) -> Tuple[str, Union[List[Dict[Union[str, int], Any]], List[Sequence[Any]]]]:
		"""
		Convert the SQL query to use the named out-style parameters from the named
		the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters (:class:`~collections.abc.Mapping` or :class:`~collections.abc.Sequence`).

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the many out-style parameters (:class:`list` of :class:`dict` or
		:class:`list`).
		"""
		raise NotImplementedError(f"{self.__class__.__qualname__} must implement convert_many().")


class NamedConverter(Converter):
	"""
	The :class:`NamedConverter` class is the base class for implementing the
	conversion from one named in-style parameter to another out-style parameter.
	"""

	_in_style: _styles.NamedStyle


class NamedToNamedConverter(NamedConverter):
	"""
	The :class:`.NamedToNamedConverter` class is used to convert named in-style
	parameters to named out-style parameters.
	"""

	def convert(
		self,
		sql: str,
		params: Dict[str, Any],
	) -> Tuple[str, Dict[str, Any]]:
		"""
		Convert the SQL query to use the named out-style parameters from the named
		the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Mapping`) contains the in-style
		parameters.

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the out-style parameters (:class:`dict`).
		"""
		if not isinstance(params, Mapping):
			raise TypeError(f"{params=!r} is not a mapping.")

		# Convert query.
		param_conversions = []
		out_sql = self._in_regex.sub(partial(self.__regex_replace, params, param_conversions), sql)

		# Convert parameters.
		out_params = self.__convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(
		self,
		sql: str,
		many_params: Iterable[Dict[str, Any]],
	) -> Tuple[str, List[Dict[str, Any]]]:
		"""
		Convert the SQL query to use the named out-style parameters from the named
		the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters (:class:`~collections.abc.Mapping`).

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the many out-style parameters (:class:`list` of :class:`dict`).
		"""
		iter_params = iter(many_params)
		first_params = next(iter_params)

		if not isinstance(first_params, Mapping):
			raise TypeError(f"many_params[0]={first_params!r} is not a mapping.")

		# Convert query.
		param_conversions = []
		out_sql = self._in_regex.sub(partial(self.__regex_replace, first_params, param_conversions), sql)

		# Convert parameters.
		out_params = self.__convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	@staticmethod
	def __convert_many_params(
		many_in_params: Iterable[Dict[str, Any]],
		param_conversions: List[Tuple[bool, str, Union[str, List[str]]]],
	) -> List[Dict[str, Any]]:
		"""
		Convert the named in-style parameters to named out-style parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter conversion to
		perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples (``False``), the
			in-name (:class:`str`), and the out-name (:class:`str`).

		-	A tuple conversion contains: whether to expand tuples (``True``), the
			in-name (:class:`str`), and the out-names (:class:`list` of :class:`str`).

		Returns the many out-style parameters (:class:`list` of :class:`dict`).
		"""
		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i and not isinstance(in_params, Mapping):
				raise TypeError(f"many_params[{i}]={in_params!r} is not a mapping.")

			out_params: Dict[str, Any] = {}
			for expand_tuple, in_name, out_name in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					out_names = out_name
					values = in_params[in_name]
					if not isinstance(values, tuple):
						raise TypeError(f"many_params[{i}][{in_name!r}]={values!r} was expected to be a tuple.")
					elif len(values) != len(out_names):
						raise ValueError(f"many_params[{i}][{in_name!r}]={values!r} length was expected to be {len(out_names)}.")

					for sub_name, sub_value in zip(out_names, values):
						out_params[sub_name] = sub_value

				else:
					# Simple conversion.
					out_params[out_name] = in_params[in_name]

			many_out_params.append(out_params)

		return many_out_params

	@staticmethod
	def __convert_params(
		in_params: Dict[str, Any],
		param_conversions: List[Tuple[bool, str, Union[str, List[str]]]],
	) -> Dict[str, Any]:
		"""
		Convert the named in-style parameters to named out-style parameters.

		*in_params* (:class:`~collections.abc.Mapping`) contains the
		in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples
			(``False``), the in-name (:class:`str`), and the out-name
			(:class:`str`).

		-	A tuple conversion contains: whether to expand tuples
			(``True``), the in-name (:class:`str`), and the out-names
			(:class:`list` of :class:`str`).

		Returns the out-style parameters (:class:`dict`).
		"""
		out_params: Dict[str, Any] = {}
		for expand_tuple, in_name, out_name in param_conversions:
			if expand_tuple:
				# Tuple conversion.
				out_names = out_name
				for sub_name, sub_value in zip(out_names, in_params[in_name]):
					out_params[sub_name] = sub_value

			else:
				# Simple conversion.
				out_params[out_name] = in_params[in_name]

		return out_params

	def __regex_replace(
		self,
		in_params: Dict[str, Any],
		param_conversions: List[Tuple[bool, str, Union[str, List[str]]]],
		match: Match[str],
	) -> str:
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Mapping`) contains the
		in-style parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each
		parameter conversion to perform (:class:`tuple`).

		*match* (:class:`re.Match`) is the in-parameter match.

		Returns the out-parameter replacement string (:class:`str`).
		"""
		result = match.groupdict()

		out_percent = result.get('out_percent')
		if out_percent is not None:
			# Out percent matched, escape it by doubling it.
			return "%%"

		escape = result.get('escape')
		if escape is not None:
			# Escape sequence matched, return escaped literal.
			return escape[self._escape_start:]

		else:
			# Named parameter matched, return named out-style parameter.
			in_name_sql = result['param']
			quote = result.get("quote")
			if self._in_style.param_quotes:
				in_name = in_name_sql if quote else in_name_sql.upper()
				for in_name_param, in_value in in_params.items():
					if _unquote_oracle_param(in_name_param) == in_name:
						value = in_value
						break
				else:
					raise KeyError(in_name_sql)
			else:
				in_name_param = in_name = in_name_sql
				value = in_params[in_name]

			if self._expand_tuples and isinstance(value, tuple):
				if not value:
					# Safely expand an empty tuple.
					return "(NULL)"

				# Convert named parameter by flattening tuple values.
				out_names = []
				out_replacements = []
				for i, sub_value in enumerate(value):
					out_name = f"{in_name}__{i}_sqlp"
					if self._out_quotes:
						out_name = _quote_oracle_param(out_name)

					out_repl = self._out_format.format(param=out_name)
					out_names.append(out_name)
					out_replacements.append(out_repl)

				param_conversions.append((True, in_name_param, out_names))
				return "({})".format(",".join(out_replacements))

			else:
				# Convert named parameter.
				out_name = in_name
				if self._out_quotes:
					out_name = _quote_oracle_param(out_name)

				out_repl = self._out_format.format(param=out_name)
				param_conversions.append((False, in_name_param, out_name))
				return out_repl


class NamedToNumericConverter(NamedConverter):
	"""
	The :class:`.NamedToNumericConverter` class is used to convert named
	in-style parameters to numeric out-style parameters.
	"""

	_out_style: _styles.NumericStyle

	def __init__(self, **kw) -> None:
		"""
		Initializes the :class:`.NamedToNumericConverter` instance.
		"""
		super().__init__(**kw)

		self.__out_start: int = self._out_style.start
		"""
		*__out_start* (:class:`int`) indicates to start enumerating
		out-parameters at the specified number.
		"""

	def convert(
		self,
		sql: str,
		params: Dict[str, Any],
	) -> Tuple[str, List[Any]]:
		"""
		Convert the SQL query to use the numeric out-style parameters from
		the named the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Mapping`) contains the in-style
		parameters.

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the out-style parameters (:class:`list`).
		"""
		if not isinstance(params, Mapping):
			raise TypeError(f"{params=!r} is not a mapping.")

		# Convert query.
		param_conversions = []
		out_counter = itertools.count()
		out_lookup = {}
		out_sql = self._in_regex.sub(partial(self.__regex_replace, params, param_conversions, out_counter, out_lookup), sql)

		# Convert parameters.
		out_params = self.__convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(
		self,
		sql: str,
		many_params: Iterable[Dict[str, Any]],
	) -> Tuple[str, List[List[Any]]]:
		"""
		Convert the SQL query to use the numeric out-style parameters from
		the named the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set
		of in-style parameters (:class:`~collections.abc.Mapping`).

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the many out-style parameters (:class:`list` of
		:class:`list`).
		"""
		iter_params = iter(many_params)
		first_params = next(iter_params)

		if not isinstance(first_params, Mapping):
			raise TypeError(f"many_params[0]={first_params!r} is not a mapping.")

		# Convert query.
		param_conversions = []
		out_counter = itertools.count()
		out_lookup = {}
		out_sql = self._in_regex.sub(partial(self.__regex_replace, first_params, param_conversions, out_counter, out_lookup), sql)

		# Convert parameters.
		out_params = self.__convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	@staticmethod
	def __convert_many_params(
		many_in_params: Iterable[Dict[str, Any]],
		param_conversions: List[Tuple[bool, str, Union[int, List[int]]]],
	) -> List[List[Any]]:
		"""
		Convert the named in-style parameters to numeric out-style
		parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each
		set of in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples
			(``False``), the in-name (:class:`str`), and the out-index
			(:class:`int`).

		-	A tuple conversion contains: whether to expand tuples
			(``True``), the in-name (:class:`str`), and the out-indices
			(:class:`list` of :class:`int`).

		Returns the many out-style parameters (:class:`list` of :class:`list`).
		"""
		# Get row size.
		last_conv = param_conversions[-1]
		size = (last_conv[2][-1] if last_conv[0] else last_conv[2]) + 1

		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i and not isinstance(in_params, Mapping):
				raise TypeError(f"many_params[{i}]={in_params!r} is not a mapping.")

			out_params: List[Any] = [None] * size
			for expand_tuple, in_name, out_index in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					values = in_params[in_name]
					out_indices = out_index
					if not isinstance(values, tuple):
						raise TypeError(f"many_params[{i}][{in_name!r}]={values!r} was expected to be a tuple.")
					elif len(values) != len(out_indices):
						raise ValueError(f"many_params[{i}][{in_name!r}]={values!r} length was expected to be {len(out_indices)}.")

					for sub_index, sub_value in zip(out_indices, values):
						out_params[sub_index] = sub_value

				else:
					# Simple conversion.
					out_params[out_index] = in_params[in_name]

			many_out_params.append(out_params)

		return many_out_params

	@staticmethod
	def __convert_params(
		in_params: Dict[str, Any],
		param_conversions: List[Tuple[bool, str, Union[int, List[int]]]],
	) -> List[Any]:
		"""
		Convert the named in-style parameters to numeric out-style parameters.

		*in_params* (:class:`~collections.abc.Mapping`) contains the in-style
		parameters.

		*param_conversions* (:class:`list`) contains each parameter conversion to
		perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples (``False``), the
			in-name (:class:`str`), and the out-index (:class:`int`).

		-	A tuple conversion contains: whether to expand tuples (``True``), the
			in-name (:class:`str`), and the out-indices (:class:`list` of :class:`int`).

		Returns the out-style parameters (:class:`list`).
		"""
		# Get row size.
		last_conv = param_conversions[-1]
		size = (last_conv[2][-1] if last_conv[0] else last_conv[2]) + 1

		out_params: List[Any] = [None] * size
		for expand_tuple, in_name, out_index in param_conversions:
			if expand_tuple:
				# Tuple conversion.
				out_indices = out_index
				for sub_index, sub_value in zip(out_indices, in_params[in_name]):
					out_params[sub_index] = sub_value

			else:
				# Simple conversion.
				out_params[out_index] = in_params[in_name]

		return out_params

	def __regex_replace(
		self,
		in_params: Dict[str, Any],
		param_conversions: List[Tuple[bool, str, Union[int, List[int]]]],
		out_counter: Iterator[int],
		out_lookup: Dict[Union[str, Tuple[str, int]], Tuple[int, str]],
		match: Match[str],
	) -> str:
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Mapping`) contains the in-style
		parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each parameter
		conversion to perform (:class:`tuple`).

		*out_counter* (:class:`~collections.abc.Iterator`) is used to generate new
		out-indices.

		*out_lookup* (:class:`dict`) caches out-parameter information.

		*match* (:class:`re.Match`) is the in-parameter match.

		Returns the out-parameter replacement string (:class:`str`).
		"""
		result = match.groupdict()

		escape = result.get('escape')
		if escape is not None:
			# Escape sequence matched, return escaped literal.
			return escape[self._escape_start:]

		else:
			# Named parameter matched, return numeric out-style parameter.
			in_name_sql = result['param']
			quote = result.get("quote")
			if self._in_style.param_quotes:
				in_name = in_name_sql if quote else in_name_sql.upper()
				for in_name_param, in_value in in_params.items():
					if _unquote_oracle_param(in_name_param) == in_name:
						value = in_value
						break
				else:
					raise KeyError(in_name_sql)
			else:
				in_name_param = in_name = in_name_sql
				value = in_params[in_name]

			if self._expand_tuples and isinstance(value, tuple):
				if not value:
					# Safely expand an empty tuple.
					return "(NULL)"

				# Convert named parameter by flattening tuple values.
				is_new = True
				out_indices = []
				out_replacements = []
				for i, sub_value in enumerate(value):
					# Lookup out-number and out-replacement.
					out_key = (in_name, i)
					out_result = out_lookup.get(out_key)
					if out_result is not None:
						out_index, out_repl = out_result
						is_new = False
					else:
						out_index = next(out_counter)
						out_num = out_index + self.__out_start
						out_repl = self._out_format.format(param=out_num)
						out_lookup[out_key] = (out_index, out_repl)

					out_indices.append(out_index)
					out_replacements.append(out_repl)

				if is_new:
					param_conversions.append((True, in_name_param, out_indices))

				return "({})".format(",".join(out_replacements))

			else:
				# Convert named parameter.

				# Lookup out-parameter info.
				out_result = out_lookup.get(in_name)
				if out_result is not None:
					out_repl = out_result[1]
				else:
					out_index = next(out_counter)
					out_num = out_index + self.__out_start
					out_repl = self._out_format.format(param=out_num)
					out_lookup[in_name] = (out_index, out_repl)
					param_conversions.append((False, in_name_param, out_index))

				return out_repl


class NamedToOrdinalConverter(NamedConverter):
	"""
	The :class:`.NamedToOrdinalConverter` class is used to convert named in-style
	parameters to ordinal out-style parameters.
	"""

	_out_style: _styles.OrdinalStyle

	def convert(
		self,
		sql: str,
		params: Dict[str, Any],
	) -> Tuple[str, List[Any]]:
		"""
		Convert the SQL query to use the ordinal out-style parameters from the named
		the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Mapping`) contains the in-style
		parameters.

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the out-style parameters (:class:`list`).
		"""
		if not isinstance(params, Mapping):
			raise TypeError(f"{params=!r} is not a mapping.")

		# Convert query.
		param_conversions = []
		out_format = self._out_style.out_format
		out_sql = self._in_regex.sub(partial(self.__regex_replace, params, param_conversions, out_format), sql)

		# Convert parameters.
		out_params = self.__convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(
		self,
		sql: str,
		many_params: Iterable[Dict[str, Any]],
	) -> Tuple[str, List[List[Any]]]:
		"""
		Convert the SQL query to use the ordinal out-style parameters from the named
		the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters (:class:`~collections.abc.Mapping`).

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the many out-style parameters (:class:`list` of :class:`list`).
		"""
		iter_params = iter(many_params)
		first_params = next(iter_params)

		if not isinstance(first_params, Mapping):
			raise TypeError(f"many_params[0]={first_params!r} is not a mapping.")

		# Convert query.
		param_conversions = []
		out_format = self._out_style.out_format
		out_sql = self._in_regex.sub(partial(self.__regex_replace, first_params, param_conversions, out_format), sql)

		# Convert parameters.
		out_params = self.__convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	@staticmethod
	def __convert_many_params(
		many_in_params: Iterable[Dict[str, Any]],
		param_conversions: List[Tuple[bool, str, Optional[int]]],
	) -> List[List[Any]]:
		"""
		Convert the named in-style parameters to ordinal out-style parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter conversion to
		perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples (``False``), the
			in-name (:class:`str`), and the out-count (``None``).

		-	A tuple conversion contains: whether to expand tuples (``True``), the
			in-name (:class:`str`), and the out-count (:class:`int` or ``None``).

		Returns the many out-style parameters (:class:`list` of :class:`list`).
		"""
		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i and not isinstance(in_params, Mapping):
				raise TypeError(f"many_params[{i}]={in_params!r} is not a mapping.")

			out_params: List[Any] = []
			for expand_tuple, in_name, out_count in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					values = in_params[in_name]
					if not isinstance(values, tuple):
						raise TypeError(f"many_params[{i}][{in_name!r}]={values!r} was expected to be a tuple.")
					elif len(values) != out_count:
						raise ValueError(f"many_params[{i}][{in_name!r}]={values!r} length was expected to be {out_count}.")

					for sub_value in values:
						out_params.append(sub_value)

				else:
					# Simple conversion.
					out_params.append(in_params[in_name])

			many_out_params.append(out_params)

		return many_out_params

	@staticmethod
	def __convert_params(
		in_params: Dict[str, Any],
		param_conversions: List[Tuple[bool, str, Optional[int]]],
	) -> List[Any]:
		"""
		Convert the named in-style parameters to ordinal out-style parameters.

		*in_params* (:class:`~collections.abc.Mapping`) contains the in-style
		parameters.

		*param_conversions* (:class:`list`) contains each parameter conversion to
		perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples (``False``), the
			in-name (:class:`str`), and the out-count (``None``).

		-	A tuple conversion contains: whether to expand tuples (``True``), the
			in-name (:class:`str`), and the out-count (:class:`int` or ``None``).

		Returns the out-style parameters (:class:`list`).
		"""
		out_params: List[Any] = []
		for expand_tuple, in_name, _out_count in param_conversions:
			if expand_tuple:
				# Tuple conversion.
				for sub_value in in_params[in_name]:
					out_params.append(sub_value)

			else:
				# Simple conversion.
				out_params.append(in_params[in_name])

		return out_params

	def __regex_replace(
		self,
		in_params: Dict[str, Any],
		param_conversions: List[Tuple[bool, str, Optional[int]]],
		out_format: str,
		match: Match[str],
	) -> str:
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Mapping`) contains the in-style
		parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each parameter
		conversion to perform (:class:`tuple`).

		*out_format* (:class:`str`) is the out-style parameter format string.

		*match* (:class:`re.Match`) is the in-parameter match.

		Returns the out-parameter replacement string (:class:`str`).
		"""
		result = match.groupdict()

		out_percent = result.get('out_percent')
		if out_percent is not None:
			# Out percent matched, escape it by doubling it.
			return "%%"

		escape = result.get('escape')
		if escape is not None:
			# Escape sequence matched, return escaped literal.
			return escape[self._escape_start:]

		else:
			# Named parameter matched, return numeric out-style parameter.
			in_name_sql = result['param']
			quote = result.get("quote")
			if self._in_style.param_quotes:
				in_name = in_name_sql if quote else in_name_sql.upper()
				for in_name_param, in_value in in_params.items():
					if _unquote_oracle_param(in_name_param) == in_name:
						value = in_value
						break
				else:
					raise KeyError(in_name_sql)
			else:
				in_name_param = in_name = in_name_sql
				value = in_params[in_name]

			if self._expand_tuples and isinstance(value, tuple):
				if not value:
					# Safely expand an empty tuple.
					return "(NULL)"

				# Convert named parameter by flattening tuple values.
				param_conversions.append((True, in_name_param, len(value)))
				return "({})".format(",".join(out_format for _ in value))

			else:
				# Convert named parameter.
				param_conversions.append((False, in_name_param, None))
				return out_format


class NumericConverter(Converter):
	"""
	The :class:`.NumericConverter` class is the base class for implementing the
	conversion from one numeric in-style parameter to another out-style parameter.
	"""

	_in_style: _styles.NumericStyle

	def __init__(self, **kw) -> None:
		"""
		Initializes the :class:`.NumericConverter` instance.
		"""
		super().__init__(**kw)

		self._in_start: int = self._in_style.start
		"""
		*_in_start* (:class:`int`) indicates to start enumerating in-parameters at
		the specified number.
		"""

	def _mapping_as_sequence(
		self,
		in_params: Dict[Union[int, str], Any],
	) -> Dict[int, Any]:
		"""
		Convert the in-parameters to mimic a sequence.

		*in_params* (:class:`~collections.abc.Mapping`) is the in-parameters.

		Returns the converted in-parameters (:class:`~collections.abc.Mapping`).
		"""
		start = self._in_start
		return {
			int(__key) - start: __value
			for __key, __value in in_params.items()
			if isinstance(__key, int) or (isinstance(__key, (str, bytes)) and __key.isdigit())
		}


class NumericToNamedConverter(NumericConverter):
	"""
	The :class:`.NumericToNamedConverter` class is used to convert numeric
	in-style parameters to named out-style parameters.
	"""

	_out_style: _styles.NamedStyle

	def convert(
		self,
		sql: str,
		params: Union[Sequence[Any], Dict[Union[int, str], Any]],
	) -> Tuple[str, Dict[str, Any]]:
		"""
		Convert the SQL query to use the named out-style parameters from the numeric
		the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Sequence` or :class:`~collections.abc.Mapping`)
		contains the in-style parameters.

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the out-style parameters (:class:`dict`).
		"""
		if is_sequence(params):
			pass
		elif isinstance(params, Mapping):
			params = self._mapping_as_sequence(params)  # noqa
		else:
			raise TypeError(f"{params=!r} is not a sequence or mapping.")

		# Convert query.
		param_conversions = []
		out_sql = self._in_regex.sub(partial(self.__regex_replace, params, param_conversions), sql)

		# Convert parameters.
		out_params = self.__convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(
		self,
		sql: str,
		many_params: Union[Iterable[Sequence[Any]], Iterable[Dict[Union[int, str], Any]]],
	) -> Tuple[str, List[Dict[str, Any]]]:
		"""
		Convert the SQL query to use the named out-style parameters from the numeric
		the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters (:class:`~collections.abc.Sequence` or
		:class:`~collections.abc.Mapping`).

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the many out-style parameters (:class:`list` of :class:`dict`).
		"""
		iter_params = iter(many_params)
		first_params = next(iter_params)

		if is_sequence(first_params):
			pass
		elif isinstance(first_params, Mapping):
			first_params = self._mapping_as_sequence(first_params)  # noqa
		else:
			raise TypeError(f"many_params[0]={first_params!r} is not a sequence or mapping.")

		# Convert query.
		param_conversions = []
		out_sql = self._in_regex.sub(partial(self.__regex_replace, first_params, param_conversions), sql)

		# Convert parameters.
		out_params = self.__convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	def __convert_many_params(
		self,
		many_in_params: Union[Iterable[Sequence[Any]], Iterable[Dict[Union[int, str], Any]]],
		param_conversions: List[Tuple[bool, int, Union[str, List[str]]]],
	) -> List[Dict[str, Any]]:
		"""
		Convert the numeric in-style parameters to named out-style parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter conversion to
		perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples (``False``), the
			in-index (:class:`int`), and the out-name (:class:`str`).

		-	A tuple conversion contains: whether to expand tuples (``True``), the
			in-index (:class:`str`), and the out-names (:class:`list` of :class:`str`).

		Returns the many out-style parameters (:class:`list` of :class:`dict`).
		"""
		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i:
				if is_sequence(in_params):
					pass
				elif isinstance(in_params, Mapping):
					in_params = self._mapping_as_sequence(in_params)  # noqa
				else:
					raise TypeError(f"many_params[{i}]={in_params!r} is not a sequence or mapping.")

			out_params: Dict[str, Any] = {}
			for expand_tuple, in_index, out_name in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					out_names = out_name
					values = in_params[in_index]
					if not isinstance(values, tuple):
						raise TypeError(f"many_params[{i}][{in_index!r}]={values!r} was expected to be a tuple.")
					elif len(values) != len(out_names):
						raise ValueError(f"many_params[{i}][{in_index!r}]={values!r} length was expected to be {len(out_names)}.")

					for sub_name, sub_value in zip(out_names, values):
						out_params[sub_name] = sub_value

				else:
					# Simple conversion.
					out_params[out_name] = in_params[in_index]

			many_out_params.append(out_params)

		return many_out_params

	@staticmethod
	def __convert_params(
		in_params: Sequence[Any],
		param_conversions: List[Tuple[bool, int, Union[str, List[str]]]],
	) -> Dict[str, Any]:
		"""
		Convert the numeric in-style parameters to named out-style parameters.

		*in_params* (:class:`~collections.abc.Sequence`) contains the in-style
		parameters.

		*param_conversions* (:class:`list`) contains each parameter conversion to
		perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples (``False``), the
			in-index (:class:`int`), and the out-name (:class:`str`).

		-	A tuple conversion contains: whether to expand tuples (``True``), the
			in-index (:class:`str`), and the out-names (:class:`list` of :class:`str`).

		Returns the out-style parameters (:class:`dict`).
		"""
		out_params: Dict[str, Any] = {}
		for expand_tuple, in_index, out_name in param_conversions:
			if expand_tuple:
				# Tuple conversion.
				out_names = out_name
				for sub_name, sub_value in zip(out_names, in_params[in_index]):
					out_params[sub_name] = sub_value

			else:
				# Simple conversion.
				out_params[out_name] = in_params[in_index]

		return out_params

	def __regex_replace(
		self,
		in_params: Sequence[Any],
		param_conversions: List[Tuple[bool, int, Union[str, List[str]]]],
		match: Match[str],
	) -> str:
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Sequence`) contains the in-style
		parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each parameter
		conversion to perform (:class:`tuple`).

		*match* (:class:`re.Match`) is the in-parameter match.

		Returns the out-parameter replacement string (:class:`str`).
		"""
		result = match.groupdict()

		out_percent = result.get('out_percent')
		if out_percent is not None:
			# Out percent matched, escape it by doubling it.
			return "%%"

		escape = result.get('escape')
		if escape is not None:
			# Escape sequence matched, return escaped literal.
			return escape[self._escape_start:]

		else:
			# Numeric parameter matched, return named out-style parameter.
			in_num_str = result['param']
			in_index = int(in_num_str) - self._in_start

			value = in_params[in_index]
			if self._expand_tuples and isinstance(value, tuple):
				if not value:
					# Safely expand an empty tuple.
					return "(NULL)"

				# Convert numeric parameter by flattening tuple values.
				out_names = []
				out_replacements = []
				for i, sub_value in enumerate(value):
					out_name = f"_{in_num_str}_{i}"
					if self._out_quotes:
						out_name = _quote_oracle_param(out_name)

					out_repl = self._out_format.format(param=out_name)
					out_names.append(out_name)
					out_replacements.append(out_repl)

				param_conversions.append((True, in_index, out_names))
				return "({})".format(",".join(out_replacements))

			else:
				# Convert numeric parameter.
				out_name = "_" + in_num_str
				if self._out_quotes:
					out_name = _quote_oracle_param(out_name)

				out_repl = self._out_format.format(param=out_name)
				param_conversions.append((False, in_index, out_name))
				return out_repl


class NumericToNumericConverter(NumericConverter):
	"""
	The :class:`.NumericToNumericConverter` class is used to convert numeric
	in-style parameters to numeric out-style parameters.
	"""

	_out_style: _styles.NumericStyle

	def __init__(self, **kw) -> None:
		"""
		Initializes the :class:`.NumericToNumericConverter` instance.
		"""
		super().__init__(**kw)

		self.__out_start: int = self._out_style.start
		"""
		*__out_start* (:class:`int`) indicates to start enumerating out-parameters
		at the specified number.
		"""

	def convert(
		self,
		sql: str,
		params: Union[Sequence[Any], Dict[Union[int, str], Any]],
	) -> Tuple[str, List[Any]]:
		"""
		Convert the SQL query to use the numeric out-style parameters from the
		numeric the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Sequence` or :class:`~collections.abc.Mapping`)
		contains the in-style parameters.

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the out-style parameters (:class:`list`).
		"""
		if is_sequence(params):
			pass
		elif isinstance(params, Mapping):
			params = self._mapping_as_sequence(params)  # noqa
		else:
			raise TypeError(f"{params=!r} is not a sequence or mapping.")

		# Convert query.
		param_conversions = []
		out_counter = itertools.count()
		out_lookup = {}
		out_sql = self._in_regex.sub(partial(self.__regex_replace, params, param_conversions, out_counter, out_lookup), sql)

		# Convert parameters.
		out_params = self.__convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(
		self,
		sql: str,
		many_params: Union[Iterable[Sequence[Any]], Iterable[Dict[Union[int, str], Any]]],
	) -> Tuple[str, List[List[Any]]]:
		"""
		Convert the SQL query to use the numeric out-style parameters from the
		numeric the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters (:class:`~collections.abc.Sequence` or
		:class:`~collections.abc.Mapping`).

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the many out-style parameters (:class:`list` of :class:`list`).
		"""
		iter_params = iter(many_params)
		first_params = next(iter_params)

		if is_sequence(first_params):
			pass
		elif isinstance(first_params, Mapping):
			first_params = self._mapping_as_sequence(first_params)  # noqa
		else:
			raise TypeError(f"many_params[0]={first_params!r} is not a sequence or mapping.")

		# Convert query.
		param_conversions = []
		out_counter = itertools.count()
		out_lookup = {}
		out_sql = self._in_regex.sub(partial(self.__regex_replace, first_params, param_conversions, out_counter, out_lookup), sql)

		# Convert parameters.
		out_params = self.__convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	def __convert_many_params(
		self,
		many_in_params: Union[Iterable[Sequence[Any]], Iterable[Dict[Union[int, str], Any]]],
		param_conversions: List[Tuple[bool, int, Union[int, List[int]]]],
	) -> List[List[Any]]:
		"""
		Convert the numeric in-style parameters to numeric out-style parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter conversion to
		perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples (``False``), the
			in-index (:class:`int`), and the out-index (:class:`int`).

		-	A tuple conversion contains: whether to expand tuples (``True``), the
			in-index (:class:`int`), and the out-indices (:class:`list` of :class:`int`).

		Returns the many out-style parameters (:class:`list` of :class:`list`).
		"""
		# Get row size.
		last_conv = param_conversions[-1]
		size = (last_conv[2][-1] if last_conv[0] else last_conv[2]) + 1

		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i:
				if is_sequence(in_params):
					pass
				elif isinstance(in_params, Mapping):
					in_params = self._mapping_as_sequence(in_params)  # noqa
				else:
					raise TypeError(f"many_params[{i}]={in_params!r} is not a mapping.")

			out_params: List[Any] = [None] * size
			for expand_tuple, in_index, out_index in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					values = in_params[in_index]
					out_indices = out_index
					if not isinstance(values, tuple):
						raise TypeError(f"many_params[{i}][{in_index!r}]={values!r} was expected to be a tuple.")
					elif len(values) != len(out_indices):
						raise ValueError(f"many_params[{i}][{in_index!r}]={values!r} length was expected to be {len(out_indices)}.")

					for sub_index, sub_value in zip(out_indices, values):
						out_params[sub_index] = sub_value

				else:
					# Simple conversion.
					out_params[out_index] = in_params[in_index]

			many_out_params.append(out_params)

		return many_out_params

	@staticmethod
	def __convert_params(
		in_params: Sequence[Any],
		param_conversions: List[Tuple[bool, int, Union[int, List[int]]]],
	) -> List[Any]:
		"""
		Convert the numeric in-style parameters to numeric out-style parameters.

		*in_params* (:class:`~collections.abc.Sequence`) contains the in-style
		parameters to sample.

		*param_conversions* (:class:`list`) contains each parameter conversion to
		perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples (``False``), the
			in-index (:class:`int`), and the out-index (:class:`int`).

		-	A tuple conversion contains: whether to expand tuples (``True``), the
			in-index (:class:`int`), and the out-indices (:class:`list` of :class:`int`).

		Returns the out-style parameters (:class:`list`).
		"""
		# Get row size.
		last_conv = param_conversions[-1]
		size = (last_conv[2][-1] if last_conv[0] else last_conv[2]) + 1

		out_params: List[Any] = [None] * size
		for expand_tuple, in_index, out_index in param_conversions:
			if expand_tuple:
				# Tuple conversion.
				out_indices = out_index
				for sub_index, sub_value in zip(out_indices, in_params[in_index]):
					out_params[sub_index] = sub_value

			else:
				# Simple conversion.
				out_params[out_index] = in_params[in_index]

		return out_params

	def __regex_replace(
		self,
		in_params: Sequence[Any],
		param_conversions: List[Tuple[bool, int, Union[int, List[int]]]],
		out_counter: Iterator[int],
		out_lookup: Dict[Union[int, Tuple[int, int]], Tuple[int, str]],
		match: Match[str],
	) -> str:
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Sequence`) contains the in-style
		parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each parameter
		conversion to perform (:class:`tuple`).

		*out_counter* (:class:`~collections.abc.Iterator`) is used to generate new
		out-indices.

		*out_lookup* (:class:`dict`) caches out-parameter information.

		*match* (:class:`re.Match`) is the in-parameter match.

		Returns the out-parameter replacement string (:class:`str`).
		"""
		result = match.groupdict()

		escape = result.get('escape')
		if escape is not None:
			# Escape sequence matched, return escaped literal.
			return escape[self._escape_start:]

		else:
			# Numeric parameter matched, return numeric out-style parameter.
			in_index = int(result['param']) - self._in_start

			value = in_params[in_index]
			if self._expand_tuples and isinstance(value, tuple):
				if not value:
					# Safely expand an empty tuple.
					return "(NULL)"

				# Convert numeric parameter by flattening tuple values.
				is_new = True
				out_indices = []
				out_replacements = []
				for i, sub_value in enumerate(value):
					# Lookup out-number and out-replacement.
					out_key = (in_index, i)
					out_result = out_lookup.get(out_key)
					if out_result is not None:
						out_index, out_repl = out_result
						is_new = False
					else:
						out_index = next(out_counter)
						out_num = out_index + self.__out_start
						out_repl = self._out_format.format(param=out_num)
						out_lookup[out_key] = (out_index, out_repl)

					out_indices.append(out_index)
					out_replacements.append(out_repl)

				if is_new:
					param_conversions.append((True, in_index, out_indices))

				return "({})".format(",".join(out_replacements))

			else:
				# Convert numeric parameter.

				# Lookup out-parameter info.
				out_result = out_lookup.get(in_index)
				if out_result is not None:
					out_repl = out_result[1]
				else:
					out_index = next(out_counter)
					out_num = out_index + self.__out_start
					out_repl = self._out_format.format(param=out_num)
					out_lookup[in_index] = (out_index, out_repl)
					param_conversions.append((False, in_index, out_index))

				return out_repl


class NumericToOrdinalConverter(NumericConverter):
	"""
	The :class:`.NumericToOrdinalConverter` class is used to convert numeric
	in-style parameters to ordinal out-style parameters.
	"""

	_out_style: _styles.OrdinalStyle

	def convert(
		self,
		sql: str,
		params: Union[Sequence[Any], Dict[Union[int, str], Any]],
	) -> Tuple[str, List[Any]]:
		"""
		Convert the SQL query to use the ordinal out-style parameters from the
		numeric the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Sequence` or :class:`~collections.abc.Mapping`)
		contains the in-style parameters.

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the out-style parameters (:class:`list`).
		"""
		if is_sequence(params):
			pass
		elif isinstance(params, Mapping):
			params = self._mapping_as_sequence(params)  # noqa
		else:
			raise TypeError(f"{params=!r} is not a sequence or mapping.")

		# Convert query.
		param_conversions = []
		out_format = self._out_style.out_format
		out_sql = self._in_regex.sub(partial(self.__regex_replace, params, param_conversions, out_format), sql)

		# Convert parameters.
		out_params = self.__convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(
		self,
		sql: str,
		many_params: Union[Iterable[Sequence[Any]], Iterable[Dict[Union[int, str], Any]]],
	) -> Tuple[str, List[List[Any]]]:
		"""
		Convert the SQL query to use the ordinal out-style parameters from the
		numeric the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters (:class:`~collections.abc.Sequence` or
		:class:`~collections.abc.Mapping`).

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the many out-style parameters (:class:`list` of :class:`list`).
		"""
		iter_params = iter(many_params)
		first_params = next(iter_params)

		if is_sequence(first_params):
			pass
		elif isinstance(first_params, Mapping):
			first_params = self._mapping_as_sequence(first_params)  # noqa
		else:
			raise TypeError(f"many_params[0]={first_params!r} is not a sequence or mapping.")

		# Convert query.
		param_conversions = []
		out_format = self._out_style.out_format
		out_sql = self._in_regex.sub(partial(self.__regex_replace, first_params, param_conversions, out_format), sql)

		# Convert parameters.
		out_params = self.__convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	def __convert_many_params(
		self,
		many_in_params: Iterable[Sequence[Any]],
		param_conversions: List[Tuple[bool, int, Optional[int]]],
	) -> List[List[Any]]:
		"""
		Convert the numeric in-style parameters to ordinal out-style parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter conversion to
		perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples (``False``), the
			in-index (:class:`int`), and the out-count (``None``).

		-	A tuple conversion contains: whether to expand tuples (``True``), the
			in-index (:class:`int`), and the out-count (:class:`int`).

		Returns the many out-style parameters (:class:`list` of :class:`list`).
		"""
		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i:
				if is_sequence(in_params):
					pass
				elif isinstance(in_params, Mapping):
					in_params = self._mapping_as_sequence(in_params)  # noqa
				else:
					raise TypeError(f"many_params[{i}]={in_params!r} is not a mapping.")

			out_params: List[Any] = []
			for expand_tuple, in_index, out_count in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					values = in_params[in_index]
					if not isinstance(values, tuple):
						raise TypeError(f"many_params[{i}][{in_index!r}]={values!r} was expected to be a tuple.")
					elif len(values) != out_count:
						raise ValueError(f"many_params[{i}][{in_index!r}]={values!r} length was expected to be {out_count}.")

					for sub_value in values:
						out_params.append(sub_value)

				else:
					# Simple conversion.
					out_params.append(in_params[in_index])

			many_out_params.append(out_params)

		return many_out_params

	@staticmethod
	def __convert_params(
		in_params: Sequence[Any],
		param_conversions: List[Tuple[bool, int, Optional[int]]],
	) -> List[Any]:
		"""
		Convert the numeric in-style parameters to ordinal out-style parameters.

		*in_params* (:class:`~collections.abc.Sequence`) contains the in-style
		parameters to sample.

		*param_conversions* (:class:`list`) contains each parameter conversion to
		perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples (``False``), the
			in-index (:class:`int`), and the out-count (``None``).

		-	A tuple conversion contains: whether to expand tuples (``True``), the
			in-index (:class:`int`), and the out-count (:class:`int`).

		Returns the out-style parameters (:class:`list`).
		"""
		out_params: List[Any] = []
		for expand_tuple, in_index, _out_count in param_conversions:
			if expand_tuple:
				# Tuple conversion.
				for sub_value in in_params[in_index]:
					out_params.append(sub_value)

			else:
				# Simple conversion.
				out_params.append(in_params[in_index])

		return out_params

	def __regex_replace(
		self,
		in_params: Sequence[Any],
		param_conversions: List[Tuple[bool, int, Optional[int]]],
		out_format: str,
		match: Match[str],
	) -> str:
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Sequence`) contains the in-style
		parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each parameter
		conversion to perform (:class:`tuple`).

		*out_format* (:class:`str`) is the out-style parameter format string.

		*match* (:class:`re.Match`) is the in-parameter match.

		Returns the out-parameter replacement string (:class:`str`).
		"""
		result = match.groupdict()

		out_percent = result.get('out_percent')
		if out_percent is not None:
			# Out percent matched, escape it by doubling it.
			return "%%"

		escape = result.get('escape')
		if escape is not None:
			# Escape sequence matched, return escaped literal.
			return escape[self._escape_start:]

		else:
			# Numeric parameter matched, return ordinal out-style parameter.
			in_index = int(result['param']) - self._in_start

			value = in_params[in_index]
			if self._expand_tuples and isinstance(value, tuple):
				if not value:
					# Safely expand an empty tuple.
					return "(NULL)"

				# Convert numeric parameter by flattening tuple values.
				param_conversions.append((True, in_index, len(value)))
				return "({})".format(",".join(out_format for _ in value))

			else:
				# Convert numeric parameter.
				param_conversions.append((False, in_index, None))
				return out_format


class OrdinalConverter(Converter):
	"""
	The :class:`.OrdinalConverter` class is the base class for implementing the
	conversion from one ordinal in-style parameter to another out-style parameter.
	"""

	@staticmethod
	def _mapping_as_sequence(
		in_params: Dict[Union[int, str], Any],
	) -> Dict[int, Any]:
		"""
		Convert the in-parameters to mimic a sequence.

		*in_params* (:class:`~collections.abc.Mapping`) is the in-parameters.

		Returns the converted in-parameters (:class:`~collections.abc.Mapping`).
		"""
		return {
			int(__key): __value
			for __key, __value in in_params.items()
			if isinstance(__key, int) or (isinstance(__key, (str, bytes)) and __key.isdigit())
		}


class OrdinalToNamedConverter(OrdinalConverter):
	"""
	The :class:`.OrdinalToNamedConverter` class is used to convert ordinal
	in-style parameters to named out-style parameters.
	"""

	_out_style: _styles.NamedStyle

	def convert(
		self,
		sql: str,
		params: Union[Sequence[Any], Dict[Union[int, str], Any]],
	) -> Tuple[str, Dict[str, Any]]:
		"""
		Convert the SQL query to use the named out-style parameters from the ordinal
		the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Sequence` or :class:`~collections.abc.Mapping`)
		contains the in-style parameters.

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the out-style parameters (:class:`dict`).
		"""
		if is_sequence(params):
			pass
		elif isinstance(params, Mapping):
			params = self._mapping_as_sequence(params)  # noqa
		else:
			raise TypeError(f"{params=!r} is not a sequence or mapping.")

		# Convert query.
		param_conversions = []
		in_counter = itertools.count()
		out_sql = self._in_regex.sub(partial(self.__regex_replace, params, param_conversions, in_counter), sql)

		# Convert parameters.
		out_params = self.__convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(
		self,
		sql: str,
		many_params: Union[Iterable[Sequence[Any]], Iterable[Dict[Union[int, str], Any]]],
	) -> Tuple[str, List[Dict[str, Any]]]:
		"""
		Convert the SQL query to use the named out-style parameters from the ordinal
		the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters (:class:`~collections.abc.Sequence` or
		:class:`~collections.abc.Mapping`).

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the many out-style parameters (:class:`list` of :class:`dict`).
		"""
		iter_params = iter(many_params)
		first_params = next(iter_params)

		if is_sequence(first_params):
			pass
		elif isinstance(first_params, Mapping):
			first_params = self._mapping_as_sequence(first_params)  # noqa
		else:
			raise TypeError(f"many_params[0]={first_params!r} is not a sequence or mapping.")

		# Convert query.
		param_conversions = []
		in_counter = itertools.count()
		out_sql = self._in_regex.sub(partial(self.__regex_replace, first_params, param_conversions, in_counter), sql)

		# Convert parameters.
		out_params = self.__convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	@classmethod
	def __convert_many_params(
		cls,
		many_in_params: Union[Iterable[Sequence[Any]], Iterable[Dict[Union[int, str], Any]]],
		param_conversions: List[Tuple[bool, int, Union[str, List[str]]]],
	) -> List[Dict[str, Any]]:
		"""
		Convert the ordinal in-style parameters to named out-style parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter conversion to
		perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples (``False``), the
		in-index (:class:`int`), and the out-name (:class:`str`).

		-	A tuple conversion contains: whether to expand tuples (``True``), the
			in-index (:class:`str`), and the out-names (:class:`list` of :class:`str`).

		Returns the many out-style parameters (:class:`list` of :class:`dict`).
		"""
		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i:
				if is_sequence(in_params):
					pass
				elif isinstance(in_params, Mapping):
					in_params = cls._mapping_as_sequence(in_params)  # noqa
				else:
					raise TypeError(f"many_params[{i}]={in_params!r} is not a sequence or mapping.")

			out_params: Dict[str, Any] = {}
			for expand_tuple, in_index, out_name in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					out_names = out_name
					values = in_params[in_index]
					if not isinstance(values, tuple):
						raise TypeError(f"many_params[{i}][{in_index!r}]={values!r} was expected to be a tuple.")
					elif len(values) != len(out_names):
						raise ValueError(f"many_params[{i}][{in_index!r}]={values!r} length was expected to be {len(out_names)}.")

					for sub_name, sub_value in zip(out_names, values):
						out_params[sub_name] = sub_value

				else:
					# Simple conversion.
					out_params[out_name] = in_params[in_index]

			many_out_params.append(out_params)

		return many_out_params

	@staticmethod
	def __convert_params(
		in_params: Sequence[Any],
		param_conversions: List[Tuple[bool, int, Union[str, List[str]]]],
	) -> Dict[str, Any]:
		"""
		Convert the ordinal in-style parameters to named out-style parameters.

		*in_params* (:class:`~collections.abc.Sequence`) contains the in-style
		parameters.

		*param_conversions* (:class:`list`) contains each parameter conversion to
		perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples (``False``), the
			in-index (:class:`int`), and the out-name (:class:`str`).

		-	A tuple conversion contains: whether to expand tuples (``True``), the
			in-index (:class:`str`), and the out-names (:class:`list` of :class:`str`).

		Returns the out-style parameters (:class:`dict`).
		"""
		out_params: Dict[str, Any] = {}
		for expand_tuple, in_index, out_name in param_conversions:
			if expand_tuple:
				# Tuple conversion.
				out_names = out_name
				for sub_name, sub_value in zip(out_names, in_params[in_index]):
					out_params[sub_name] = sub_value

			else:
				# Simple conversion.
				out_params[out_name] = in_params[in_index]

		return out_params

	def __regex_replace(
		self,
		in_params: Sequence[Any],
		param_conversions: List[Tuple[bool, int, Union[str, List[str]]]],
		in_counter: Iterator[int],
		match: Match[str],
	) -> str:
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Sequence`) contains the in-style
		parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each parameter
		conversion to perform (:class:`tuple`).

		*in_counter* (:class:`~collections.abc.Iterator`) is used to generate next
		in-indices.

		*match* (:class:`re.Match`) is the in-parameter match.

		Returns the out-parameter replacement string (:class:`str`).
		"""
		result = match.groupdict()

		out_percent = result.get('out_percent')
		if out_percent is not None:
			# Out percent matched, escape it by doubling it.
			return "%%"

		escape = result.get('escape')
		if escape is not None:
			# Escape sequence matched, return escaped literal.
			return escape[self._escape_start:]

		else:
			# Ordinal parameter matched, return named out-style parameter.
			in_index = next(in_counter)

			value = in_params[in_index]
			if self._expand_tuples and isinstance(value, tuple):
				if not value:
					# Safely expand an empty tuple.
					return "(NULL)"

				# Convert ordinal parameter by flattening tuple values.
				out_names = []
				out_replacements = []
				for i, sub_value in enumerate(value):
					out_name = f"_{in_index}_{i}"
					if self._out_quotes:
						out_name = _quote_oracle_param(out_name)

					out_repl = self._out_format.format(param=out_name)
					out_names.append(out_name)
					out_replacements.append(out_repl)

				param_conversions.append((True, in_index, out_names))
				return "({})".format(",".join(out_replacements))

			else:
				# Convert ordinal parameter.
				out_name = f"_{in_index}"
				if self._out_quotes:
					out_name = _quote_oracle_param(out_name)

				out_repl = self._out_format.format(param=out_name)
				param_conversions.append((False, in_index, out_name))
				return out_repl


class OrdinalToNumericConverter(OrdinalConverter):
	"""
	The :class:`.OrdinalToNumericConverter` class is used to convert ordinal
	in-style parameters to numeric out-style parameters.
	"""

	_out_style: _styles.NumericStyle

	def __init__(self, **kw):
		"""
		Initializes the :class:`.OrdinalToNumericConverter` instance.
		"""
		super().__init__(**kw)

		self.__out_start = self._out_style.start
		"""
		*__out_start* (:class:`int`) indicates to start enumerating out-parameters
		at the specified number.
		"""

	def convert(
		self,
		sql: str,
		params: Union[Sequence[Any], Dict[Union[int, str], Any]],
	) -> Tuple[str, List[Any]]:
		"""
		Convert the SQL query to use the numeric out-style parameters from the
		ordinal the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Sequence` or :class:`~collections.abc.Mapping`)
		contains the in-style parameters.

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the out-style parameters (:class:`list`).
		"""
		if is_sequence(params):
			pass
		elif isinstance(params, Mapping):
			params = self._mapping_as_sequence(params)  # noqa
		else:
			raise TypeError(f"{params=!r} is not a sequence or mapping.")

		# Convert query.
		param_conversions = []
		in_counter = itertools.count()
		out_counter = itertools.count()
		out_sql = self._in_regex.sub(partial(self.__regex_replace, params, param_conversions, in_counter, out_counter), sql)

		# Convert parameters.
		out_params = self.__convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(
		self,
		sql: str,
		many_params: Union[Iterable[Sequence[Any]], Iterable[Dict[Union[int, str], Any]]],
	) -> Tuple[str, List[List[Any]]]:
		"""
		Convert the SQL query to use the numeric out-style parameters from the
		ordinal the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters (:class:`~collections.abc.Sequence` or
		:class:`~collections.abc.Mapping`).

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the many out-style parameters (:class:`list` of :class:`list`).
		"""
		iter_params = iter(many_params)
		first_params = next(iter_params)

		if is_sequence(first_params):
			pass
		elif isinstance(first_params, Mapping):
			first_params = self._mapping_as_sequence(first_params)  # noqa
		else:
			raise TypeError(f"many_params[0]={first_params!r} is not a sequence or mapping.")

		# Convert query.
		param_conversions = []
		in_counter = itertools.count()
		out_counter = itertools.count()
		out_sql = self._in_regex.sub(partial(self.__regex_replace, first_params, param_conversions, in_counter, out_counter), sql)

		# Convert parameters.
		out_params = self.__convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	@classmethod
	def __convert_many_params(
		cls,
		many_in_params: Union[Iterable[Sequence[Any]], Iterable[Dict[Union[int, str], Any]]],
		param_conversions: List[Tuple[bool, int, Union[int, List[int]]]],
	) -> List[List[Any]]:
		"""
		Convert the ordinal in-style parameters to numeric out-style parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter conversion to
		perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples (``False``), the
			in-index (:class:`int`), and the out-index (:class:`int`).

		-	A tuple conversion contains: whether to expand tuples (``True``), the
			in-index (:class:`int`), and the out-indices (:class:`list` of :class:`int`).

		Returns the many out-style parameters (:class:`list` of :class:`list`).
		"""
		# Get row size.
		last_conv = param_conversions[-1]
		size = (last_conv[2][-1] if last_conv[0] else last_conv[2]) + 1

		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i:
				if is_sequence(in_params):
					pass
				elif isinstance(in_params, Mapping):
					in_params = cls._mapping_as_sequence(in_params)  # noqa
				else:
					raise TypeError(f"many_params[{i}]={in_params!r} is not a mapping.")

			out_params: List[Any] = [None] * size
			for expand_tuple, in_index, out_index in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					values = in_params[in_index]
					out_indices = out_index
					if not isinstance(values, tuple):
						raise TypeError(f"many_params[{i}][{in_index!r}]={values!r} was expected to be a tuple.")
					elif len(values) != len(out_indices):
						raise ValueError(f"many_params[{i}][{in_index!r}]={values!r} length was expected to be {len(out_indices)}.")

					for sub_index, sub_value in zip(out_indices, values):
						out_params[sub_index] = sub_value

				else:
					# Simple conversion.
					out_params[out_index] = in_params[in_index]

			many_out_params.append(out_params)

		return many_out_params

	@staticmethod
	def __convert_params(
		in_params: Sequence[Any],
		param_conversions: List[Tuple[bool, int, Union[int, List[int]]]],
	) -> List[Any]:
		"""
		Convert the ordinal in-style parameters to numeric out-style parameters.

		*in_params* (:class:`~collections.abc.Sequence`) contains the in-style
		parameters to sample.

		*param_conversions* (:class:`list`) contains each parameter conversion to
		perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples (``False``), the
			in-index (:class:`int`), and the out-index (:class:`int`).

		-	A tuple conversion contains: whether to expand tuples (``True``), the
			in-index (:class:`int`), and the out-indices (:class:`list` of :class:`int`).

		Returns the out-style parameters (:class:`list`).
		"""
		# Get row size.
		last_conv = param_conversions[-1]
		size = (last_conv[2][-1] if last_conv[0] else last_conv[2]) + 1

		out_params: List[Any] = [None] * size
		for expand_tuple, in_index, out_index in param_conversions:
			if expand_tuple:
				# Tuple conversion.
				out_indices = out_index
				for sub_index, sub_value in zip(out_indices, in_params[in_index]):
					out_params[sub_index] = sub_value

			else:
				# Simple conversion.
				out_params[out_index] = in_params[in_index]

		return out_params

	def __regex_replace(
		self,
		in_params: Sequence[Any],
		param_conversions: List[Tuple[bool, int, Union[int, List[int]]]],
		in_counter: Iterator[int],
		out_counter: Iterator[int],
		match: Match[str],
	) -> str:
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Sequence`) contains the in-style
		parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each parameter
		conversion to perform (:class:`tuple`).

		*in_counter* (:class:`~collections.abc.Iterator`) is used to generate next
		in-indices.

		*out_counter* (:class:`~collections.abc.Iterator`) is used to generate new
		out-indices.

		*match* (:class:`re.Match`) is the in-parameter match.

		Returns the out-parameter replacement string (:class:`str`).
		"""
		result = match.groupdict()

		escape = result.get('escape')
		if escape is not None:
			# Escape sequence matched, return escaped literal.
			return escape[self._escape_start:]

		else:
			# Ordinal parameter matched, return numeric out-style parameter.
			in_index = next(in_counter)

			value = in_params[in_index]
			if self._expand_tuples and isinstance(value, tuple):
				if not value:
					# Safely expand an empty tuple.
					return "(NULL)"

				# Convert ordinal parameter by flattening tuple values.
				out_indices = []
				out_replacements = []
				for i, sub_value in enumerate(value):
					out_index = next(out_counter)
					out_num = out_index + self.__out_start
					out_repl = self._out_format.format(param=out_num)
					out_indices.append(out_index)
					out_replacements.append(out_repl)

				param_conversions.append((True, in_index, out_indices))
				return "({})".format(",".join(out_replacements))

			else:
				# Convert ordinal parameter.
				out_index = next(out_counter)
				out_num = out_index + self.__out_start
				out_repl = self._out_format.format(param=out_num)
				param_conversions.append((False, in_index, out_index))
				return out_repl


class OrdinalToOrdinalConverter(OrdinalConverter):
	"""
	The :class:`.OrdinalToOrdinalConverter` class is used to convert ordinal
	in-style parameters to ordinal out-style parameters.
	"""

	_out_style: _styles.OrdinalStyle

	def convert(
		self,
		sql: str,
		params: Union[Sequence[Any], Dict[Union[int, str], Any]],
	) -> Tuple[str, List[Any]]:
		"""
		Convert the SQL query to use the ordinal out-style parameters from the
		ordinal the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Sequence` or :class:`~collections.abc.Mapping`)
		contains the in-style parameters.

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the out-style parameters (:class:`list`).
		"""
		if is_sequence(params):
			pass
		elif isinstance(params, Mapping):
			params = self._mapping_as_sequence(params)  # noqa
		else:
			raise TypeError(f"{params=!r} is not a sequence or mapping.")

		# Convert query.
		param_conversions = []
		in_counter = itertools.count()
		out_format = self._out_style.out_format
		out_sql = self._in_regex.sub(partial(self.__regex_replace, params, param_conversions, in_counter, out_format), sql)

		# Convert parameters.
		out_params = self.__convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(
		self,
		sql: str,
		many_params: Union[Iterable[Sequence[Any]], Iterable[Dict[Union[int, str], Any]]],
	) -> Tuple[str, List[List[Any]]]:
		"""
		Convert the SQL query to use the ordinal out-style parameters from the
		ordinal the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters (:class:`~collections.abc.Sequence` or
		:class:`~collections.abc.Mapping`).

		Returns a :class:`tuple` containing: the converted SQL query (:class:`str`),
		and the many out-style parameters (:class:`list` of
		:class:`list`).
		"""
		iter_params = iter(many_params)
		first_params = next(iter_params)

		if is_sequence(first_params):
			pass
		elif isinstance(first_params, Mapping):
			first_params = self._mapping_as_sequence(first_params)  # noqa
		else:
			raise TypeError(f"many_params[0]={first_params!r} is not a sequence or mapping.")

		# Convert query.
		param_conversions = []
		in_counter = itertools.count()
		out_format = self._out_style.out_format
		out_sql = self._in_regex.sub(partial(self.__regex_replace, first_params, param_conversions, in_counter, out_format), sql)

		# Convert parameters.
		out_params = self.__convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	@classmethod
	def __convert_many_params(
		cls,
		many_in_params: Iterable[Sequence[Any]],
		param_conversions: List[Tuple[bool, int, Optional[int]]],
	) -> List[List[Any]]:
		"""
		Convert the ordinal in-style parameters to ordinal out-style parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each set of
		in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter conversion to
		perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples (``False``), the
			in-index (:class:`int`), and the out-count (``None``).

		-	A tuple conversion contains: whether to expand tuples (``True``), the
			in-index (:class:`int`), and the out-count (:class:`int`).

		Returns the many out-style parameters (:class:`list` of :class:`list`).
		"""
		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i:
				if is_sequence(in_params):
					pass
				elif isinstance(in_params, Mapping):
					in_params = cls._mapping_as_sequence(in_params)  # noqa
				else:
					raise TypeError(f"many_params[{i}]={in_params!r} is not a mapping.")

			out_params: List[Any] = []
			for expand_tuple, in_index, out_count in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					values = in_params[in_index]
					if not isinstance(values, tuple):
						raise TypeError(f"many_params[{i}][{in_index!r}]={values!r} was expected to be a tuple.")
					elif len(values) != out_count:
						raise ValueError(f"many_params[{i}][{in_index!r}]={values!r} length was expected to be {out_count}.")

					for sub_value in values:
						out_params.append(sub_value)

				else:
					# Simple conversion.
					out_params.append(in_params[in_index])

			many_out_params.append(out_params)

		return many_out_params

	@staticmethod
	def __convert_params(
		in_params: Sequence[Any],
		param_conversions: List[Tuple[bool, int, Optional[int]]],
	) -> List[Any]:
		"""
		Convert the ordinal in-style parameters to ordinal out-style parameters.

		*in_params* (:class:`~collections.abc.Sequence`) contains the in-style
		parameters to sample.

		*param_conversions* (:class:`list`) contains each parameter conversion to
		perform (:class:`tuple`).

		-	A simple conversion contains: whether to expand tuples (``False``), the
			in-index (:class:`int`), and the out-count (``None``).

		-	A tuple conversion contains: whether to expand tuples (``True``), the
			in-index (:class:`int`), and the out-count (:class:`int`).

		Returns the out-style parameters (:class:`list`).
		"""
		out_params: List[Any] = []
		for expand_tuple, in_index, _out_count in param_conversions:
			if expand_tuple:
				# Tuple conversion.
				for sub_value in in_params[in_index]:
					out_params.append(sub_value)

			else:
				# Simple conversion.
				out_params.append(in_params[in_index])

		return out_params

	def __regex_replace(
		self,
		in_params,
		param_conversions: List[Tuple[bool, int, Optional[int]]],
		in_counter: Iterator[int],
		out_format: str,
		match: Match[str],
	) -> str:
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Sequence`) contains the in-style
		parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each parameter
		conversion to perform (:class:`tuple`).

		*in_counter* (:class:`~collections.abc.Iterator`) is used to generate next
		in-indices.

		*out_format* (:class:`str`) is the out-style parameter format string.

		*match* (:class:`re.Match`) is the in-parameter match.

		Returns the out-parameter replacement string (:class:`str`).
		"""
		result = match.groupdict()

		out_percent = result.get('out_percent')
		if out_percent is not None:
			# Out percent matched, escape it by doubling it.
			return "%%"

		escape = result.get('escape')
		if escape is not None:
			# Escape sequence matched, return escaped literal.
			return escape[self._escape_start:]

		else:
			# Ordinal parameter matched, return ordinal out-style parameter.
			in_index = next(in_counter)

			value = in_params[in_index]
			if self._expand_tuples and isinstance(value, tuple):
				if not value:
					# Safely expand an empty tuple.
					return "(NULL)"

				# Convert ordinal parameter by flattening tuple values.
				param_conversions.append((True, in_index, len(value)))
				return "({})".format(",".join(out_format for _ in value))

			else:
				# Convert ordinal parameter.
				param_conversions.append((False, in_index, None))
				return out_format


def _quote_oracle_param(param: str) -> str:
	"""
	Quote the Oracle parameter.

	*param* (:class:`str`) is the out-parameter.

	Returns the quoted parameter (:class:`str`).
	"""
	out_name = param.replace('"', '""')
	return f'"{out_name}"'


def _unquote_oracle_param(param: str) -> str:
	"""
	Unquote the Oracle parameter.

	*param* (:class:`str`) is the in-parameter.

	Returns the unquoted parameter (:class:`str`).
	"""
	if len(param) > 1 and param[0] == param[-1] == '"':
		return param[1:-1]
	elif len(param) > 0 and (param[0] == '"' or param[-1] == '"'):
		raise KeyError(param)
	return param.upper()
