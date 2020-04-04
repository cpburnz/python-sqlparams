"""
This module contains internal classes used for converting parameter
styles.
"""

import itertools
from collections.abc import Mapping
from functools import partial

from . import _styles
from ._util import _is_sequence


class _Converter(object):
	"""
	The :class:`._Converter` class is the base class for implementing the
	conversion from one in-style parameter to another out-style parameter.
	"""

	def __init__(self, escape_char, expand_tuples, in_regex, in_style, out_style):
		"""
		Initializes the :class:`._Converter` instance.
		"""

		self._escape_start = len(escape_char) if escape_char is not None else 0
		"""
		*_escape_start* (:class:`int`) is the offset used to skip the escape
		character.
		"""

		self._expand_tuples = expand_tuples
		"""
		*_expand_tuples* (:class:`bool`) is whether to convert tuples into a
		sequence of parameters.
		"""

		self._in_regex = in_regex
		"""
		*_in_regex* (:class:`re.Pattern`) is the regular expression used to
		extract the in-style parameters.
		"""

		self._in_style = in_style
		"""
		*_in_style* (:class:`._styles._Style`) is the in-style to use.
		"""

		self._out_format = out_style.out_format
		"""
		*_out_format* (:class:`str`) is the out-style parameter format
		string.
		"""

		self._out_style = out_style
		"""
		*_out_style* (:class:`._styles._Style`) is the out-style to use.
		"""

	def convert(self, sql, params):
		"""
		Convert the SQL query to use the named out-style parameters from the
		named the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Mapping` or :class:`~collections.abc.Sequence`)
		contains the set of in-style parameters.

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the out-style parameters (:class:`dict` or
		:class:`list`).
		"""
		raise NotImplementedError("{} must implement convert().".format(self.__class__.__qualname__))

	def convert_many(self, sql, many_params):
		"""
		Convert the SQL query to use the named out-style parameters from the
		named the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set
		of in-style parameters (:class:`~collections.abc.Mapping` or
		:class:`~collections.abc.Sequence`).

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the many out-style parameters (:class:`list` of
		:class:`dict` or :class:`list`).
		"""
		raise NotImplementedError("{} must implement convert_many().".format(self.__class__.__qualname__))


class _NamedToNamedConverter(_Converter):
	"""
	The :class:`._NamedToNamedConverter` class is used to convert named
	in-style parameters to named out-style parameters.
	"""

	def convert(self, sql, params):
		"""
		Convert the SQL query to use the named out-style parameters from the
		named the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Mapping`) contains the in-style
		parameters.

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the out-style parameters (:class:`dict`).
		"""
		if not isinstance(params, Mapping):
			raise TypeError("params:{!r} is not a mapping.".format(params))

		# Convert query.
		param_conversions = []
		out_sql = self._in_regex.sub(partial(self._regex_replace, params, param_conversions), sql)

		# Convert parameters.
		out_params = self._convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(self, sql, many_params):
		"""
		Convert the SQL query to use the named out-style parameters from the
		named the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set
		of in-style parameters (:class:`~collections.abc.Mapping`).

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the many out-style parameters (:class:`list` of
		:class:`dict`).
		"""
		iter_params = iter(many_params)
		first_params = next(iter_params)

		if not isinstance(first_params, Mapping):
			raise TypeError("many_params[0]:{!r} is not a mapping.".format(first_params))

		# Convert query.
		param_conversions = []
		out_sql = self._in_regex.sub(partial(self._regex_replace, first_params, param_conversions), sql)

		# Convert parameters.
		out_params = self._convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	def _convert_many_params(self, many_in_params, param_conversions):
		"""
		Convert the named in-style parameters to named out-style parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each
		set of in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-name (:class:`str`), and the out-name
		  (:class:`str`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-name (:class:`str`), and the out-names
		  (:class:`list` of :class:`str`).

		Returns the many out-style parameters (:class:`list` of :class:`dict`).
		"""
		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i and not isinstance(in_params, Mapping):
				raise TypeError("many_params[{}]:{!r} is not a mapping.".format(i, in_params))

			out_params = {}
			for expand_tuple, in_name, out_name in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					out_names = out_name
					values = in_params[in_name]
					if not isinstance(values, tuple):
						raise TypeError("many_params[{}][{!r}]:{!r} was expected to be a tuple.".format(i, in_name, values))
					elif len(values) != len(out_names):
						raise ValueError("many_params[{}][{!r}]:{!r} length was expected to be {}.".format(i, in_name, values, len(out_names)))

					for sub_name, sub_value in zip(out_names, values):
						out_params[sub_name] = sub_value

				else:
					# Simple conversion.
					out_params[out_name] = in_params[in_name]

			many_out_params.append(out_params)

		return many_out_params

	def _convert_params(self, in_params, param_conversions):
		"""
		Convert the named in-style parameters to named out-style parameters.

		*in_params* (:class:`~collections.abc.Mapping`) contains the
		in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-name (:class:`str`), and the out-name
		  (:class:`str`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-name (:class:`str`), and the out-names
		  (:class:`list` of :class:`str`).

		Returns the out-style parameters (:class:`dict`).
		"""
		out_params = {}
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

	def _regex_replace(self, in_params, param_conversions, match):
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

		escape = result.get('escape')
		if escape is not None:
			# Escape sequence matched, return escaped literal.
			return escape[self._escape_start:]

		else:
			# Named parameter matched, return named out-style parameter.
			in_name = result['param']

			value = in_params[in_name]
			if self._expand_tuples and isinstance(value, tuple):
				# Convert named parameter by flattening tuple values.
				out_names = []
				out_replacements = []
				for i, sub_value in enumerate(value):
					out_name = "{}__{}_sqlp".format(in_name, i)
					out_repl = self._out_format.format(param=out_name)
					out_names.append(out_name)
					out_replacements.append(out_repl)

				param_conversions.append((True, in_name, out_names))
				return "({})".format(",".join(out_replacements))

			else:
				# Convert named parameter.
				out_repl = self._out_format.format(param=in_name)
				param_conversions.append((False, in_name, in_name))
				return out_repl


class _NamedToNumericConverter(_Converter):
	"""
	The :class:`._NamedToNumericConverter` class is used to convert named
	in-style parameters to numeric out-style parameters.
	"""

	def __init__(self, **kw):
		"""
		Initializes the :class:`._NamedToNumericConverter` instance.
		"""
		super().__init__(**kw)

		self._out_start = self._out_style.start
		"""
		*_out_start* (:class:`int`) indicates to start enumerating
		out-parameters at the specified number.
		"""

	def convert(self, sql, params):
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
			raise TypeError("params:{!r} is not a mapping.".format(params))

		# Convert query.
		param_conversions = []
		out_counter = itertools.count()
		out_lookup = {}
		out_sql = self._in_regex.sub(partial(self._regex_replace, params, param_conversions, out_counter, out_lookup), sql)

		# Convert parameters.
		out_params = self._convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(self, sql, many_params):
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
			raise TypeError("many_params[0]:{!r} is not a mapping.".format(first_params))

		# Convert query.
		param_conversions = []
		out_counter = itertools.count()
		out_lookup = {}
		out_sql = self._in_regex.sub(partial(self._regex_replace, first_params, param_conversions, out_counter, out_lookup), sql)

		# Convert parameters.
		out_params = self._convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	def _convert_many_params(self, many_in_params, param_conversions):
		"""
		Convert the named in-style parameters to numeric out-style
		parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each
		set of in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-name (:class:`str`), and the out-index
		  (:class:`int`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-name (:class:`str`), and the out-indices
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
				raise TypeError("many_params[{}]:{!r} is not a mapping.".format(i, in_params))

			out_params = [None] * size
			for expand_tuple, in_name, out_index in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					values = in_params[in_name]
					out_indices = out_index
					if not isinstance(values, tuple):
						raise TypeError("many_params[{}][{!r}]:{!r} was expected to be a tuple.".format(i, in_name, values))
					elif len(values) != len(out_indices):
						raise ValueError("many_params[{}][{!r}]:{!r} length was expected to be {}.".format(i, in_name, values, len(out_indices)))

					for sub_index, sub_value in zip(out_indices, values):
						out_params[sub_index] = sub_value

				else:
					# Simple conversion.
					out_params[out_index] = in_params[in_name]

			many_out_params.append(out_params)

		return many_out_params

	def _convert_params(self, in_params, param_conversions):
		"""
		Convert the named in-style parameters to numeric out-style
		parameters.

		*in_params* (:class:`~collections.abc.Mapping`) contains the
		in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-name (:class:`str`), and the out-index
		  (:class:`int`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-name (:class:`str`), and the out-indices
		  (:class:`list` of :class:`int`).

		Returns the out-style parameters (:class:`list`).
		"""
		# Get row size.
		last_conv = param_conversions[-1]
		size = (last_conv[2][-1] if last_conv[0] else last_conv[2]) + 1

		out_params = [None] * size
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

	def _regex_replace(self, in_params, param_conversions, out_counter, out_lookup, match):
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Mapping`) contains the
		in-style parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each
		parameter conversion to perform (:class:`tuple`).

		*out_counter* (:class:`~collections.abc.Iterator`) is used to
		generate new out-indices.

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
			in_name = result['param']

			value = in_params[in_name]
			if self._expand_tuples and isinstance(value, tuple):
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
						out_num = out_index + self._out_start
						out_repl = self._out_format.format(param=out_num)
						out_lookup[out_key] = (out_index, out_repl)

					out_indices.append(out_index)
					out_replacements.append(out_repl)

				if is_new:
					param_conversions.append((True, in_name, out_indices))

				return "({})".format(",".join(out_replacements))

			else:
				# Convert named parameter.

				# Lookup out-parameter info.
				out_result = out_lookup.get(in_name)
				if out_result is not None:
					out_repl = out_result[1]
				else:
					out_index = next(out_counter)
					out_num = out_index + self._out_start
					out_repl = self._out_format.format(param=out_num)
					out_lookup[in_name] = (out_index, out_repl)
					param_conversions.append((False, in_name, out_index))

				return out_repl


class _NamedToOrdinalConverter(_Converter):
	"""
	The :class:`._NamedToOrdinalConverter` class is used to convert named
	in-style parameters to ordinal out-style parameters.
	"""

	def convert(self, sql, params):
		"""
		Convert the SQL query to use the ordinal out-style parameters from
		the named the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Mapping`) contains the in-style
		parameters.

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the out-style parameters (:class:`list`).
		"""
		if not isinstance(params, Mapping):
			raise TypeError("params:{!r} is not a mapping.".format(params))

		# Convert query.
		param_conversions = []
		out_format = self._out_style.out_format
		out_sql = self._in_regex.sub(partial(self._regex_replace, params, param_conversions, out_format), sql)

		# Convert parameters.
		out_params = self._convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(self, sql, many_params):
		"""
		Convert the SQL query to use the ordinal out-style parameters from
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
			raise TypeError("many_params[0]:{!r} is not a mapping.".format(first_params))

		# Convert query.
		param_conversions = []
		out_format = self._out_style.out_format
		out_sql = self._in_regex.sub(partial(self._regex_replace, first_params, param_conversions, out_format), sql)

		# Convert parameters.
		out_params = self._convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	def _convert_many_params(self, many_in_params, param_conversions):
		"""
		Convert the named in-style parameters to ordinal out-style
		parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each
		set of in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-name (:class:`str`), and the out-name
		  (:class:`str`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-name (:class:`str`), and the out-names
		  (:class:`list` of :class:`str`).

		Returns the many out-style parameters (:class:`list` of :class:`list`).
		"""
		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i and not isinstance(in_params, Mapping):
				raise TypeError("many_params[{}]:{!r} is not a mapping.".format(i, in_params))

			out_params = []
			for expand_tuple, in_name, out_count in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					values = in_params[in_name]
					if not isinstance(values, tuple):
						raise TypeError("many_params[{}][{!r}]:{!r} was expected to be a tuple.".format(i, in_name, values))
					elif len(values) != out_count:
						raise ValueError("many_params[{}][{!r}]:{!r} length was expected to be {}.".format(i, in_name, values, out_count))

					for sub_value in values:
						out_params.append(sub_value)

				else:
					# Simple conversion.
					out_params.append(in_params[in_name])

			many_out_params.append(out_params)

		return many_out_params

	def _convert_params(self, in_params, param_conversions):
		"""
		Convert the named in-style parameters to ordinal out-style
		parameters.

		*in_params* (:class:`~collections.abc.Mapping`) contains the
		in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-name (:class:`str`), and the out-name
		  (:class:`str`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-name (:class:`str`), and the out-names
		  (:class:`list` of :class:`str`).

		Returns the out-style parameters (:class:`list`).
		"""
		out_params = []
		for expand_tuple, in_name, _out_count in param_conversions:
			if expand_tuple:
				# Tuple conversion.
				for sub_value in in_params[in_name]:
					out_params.append(sub_value)

			else:
				# Simple conversion.
				out_params.append(in_params[in_name])

		return out_params

	def _regex_replace(self, in_params, param_conversions, out_format, match):
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Mapping`) contains the
		in-style parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each
		parameter conversion to perform (:class:`tuple`).

		*out_format* (:class:`str`) is the out-style parameter format
		string.

		*match* (:class:`re.Match`) is the in-parameter match.

		Returns the out-parameter replacement string (:class:`str`).
		"""
		result = match.groupdict()

		escape = result.get('escape')
		if escape is not None:
			# Escape sequence matched, return escaped literal.
			return escape[self._escape_start:]

		else:
			# Named parameter matched, return ordinal out-style parameter.
			in_name = result['param']

			value = in_params[in_name]
			if self._expand_tuples and isinstance(value, tuple):
				# Convert named parameter by flattening tuple values.
				param_conversions.append((True, in_name, len(value)))
				return "({})".format(",".join(out_format for _ in value))

			else:
				# Convert named parameter.
				param_conversions.append((False, in_name, None))
				return out_format


class _NumericConverter(_Converter):
	"""
	The :class:`._NumericConverter` class is the base class for
	implementing the conversion from one numeric in-style parameter to
	another out-style parameter.
	"""

	def __init__(self, **kw):
		"""
		Initializes the :class:`._NumericConverter` instance.
		"""
		super().__init__(**kw)

		self._in_start = self._in_style.start
		"""
		*_in_start* (:class:`int`) indicates to start enumerating
		in-parameters at the specified number.
		"""

	def _mapping_as_sequence(self, in_params):
		"""
		Convert the in-parameters to mimic a sequence.

		*in_params* (:class:`~collections.abc.Mapping`) is the
		in-parameters.

		Returns the converted in-parameters (:class:`~collections.abc.Mapping`).
		"""
		start = self._in_start
		return {int(__key) - start: __value for __key, __value in in_params.items() if isinstance(__key, int) or (isinstance(__key, (str, bytes)) and __key.isdigit())}


class _NumericToNamedConverter(_NumericConverter):
	"""
	The :class:`._NumericToNamedConverter` class is used to convert
	numeric in-style parameters to named out-style parameters.
	"""

	def convert(self, sql, params):
		"""
		Convert the SQL query to use the named out-style parameters from the
		numeric the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Sequence` or :class:`~collections.abc.Mapping`)
		contains the in-style parameters.

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the out-style parameters (:class:`dict`).
		"""
		if _is_sequence(params):
			pass
		elif isinstance(params, Mapping):
			params = self._mapping_as_sequence(params)
		else:
			raise TypeError("params:{!r} is not a sequence or mapping.".format(params))

		# Convert query.
		param_conversions = []
		out_sql = self._in_regex.sub(partial(self._regex_replace, params, param_conversions), sql)

		# Convert parameters.
		out_params = self._convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(self, sql, many_params):
		"""
		Convert the SQL query to use the named out-style parameters from the
		numeric the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set
		of in-style parameters (:class:`~collections.abc.Sequence` or
		:class:`~collections.abc.Mapping`).

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the many out-style parameters (:class:`list` of
		:class:`dict`).
		"""
		iter_params = iter(many_params)
		first_params = next(iter_params)

		if _is_sequence(first_params):
			pass
		elif isinstance(first_params, Mapping):
			first_params = self._mapping_as_sequence(first_params)
		else:
			raise TypeError("many_params[0]:{!r} is not a sequence or mapping.".format(first_params))

		# Convert query.
		param_conversions = []
		out_sql = self._in_regex.sub(partial(self._regex_replace, first_params, param_conversions), sql)

		# Convert parameters.
		out_params = self._convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	def _convert_many_params(self, many_in_params, param_conversions):
		"""
		Convert the numeric in-style parameters to named out-style
		parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each
		set of in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-index (:class:`int`), and the out-name
		  (:class:`str`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-index (:class:`str`), and the out-names
		  (:class:`list` of :class:`str`).

		Returns the many out-style parameters (:class:`list` of :class:`dict`).
		"""
		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i:
				if _is_sequence(in_params):
					pass
				elif isinstance(in_params, Mapping):
					in_params = self._mapping_as_sequence(in_params)
				else:
					raise TypeError("many_params[{}]:{!r} is not a sequence or mapping.".format(i, in_params))

			out_params = {}
			for expand_tuple, in_index, out_name in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					out_names = out_name
					values = in_params[in_index]
					if not isinstance(values, tuple):
						raise TypeError("many_params[{}][{!r}]:{!r} was expected to be a tuple.".format(i, in_index, values))
					elif len(values) != len(out_names):
						raise ValueError("many_params[{}][{!r}]:{!r} length was expected to be {}.".format(i, in_index, values, len(out_names)))

					for sub_name, sub_value in zip(out_names, values):
						out_params[sub_name] = sub_value

				else:
					# Simple conversion.
					out_params[out_name] = in_params[in_index]

			many_out_params.append(out_params)

		return many_out_params

	def _convert_params(self, in_params, param_conversions):
		"""
		Convert the numeric in-style parameters to named out-style
		parameters.

		*in_params* (:class:`~collections.abc.Sequence`) contains the
		in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-index (:class:`int`), and the out-name
		  (:class:`str`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-index (:class:`str`), and the out-names
		  (:class:`list` of :class:`str`).

		Returns the out-style parameters (:class:`dict`).
		"""
		out_params = {}
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

	def _regex_replace(self, in_params, param_conversions, match):
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Sequence`) contains the
		in-style parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each
		parameter conversion to perform (:class:`tuple`).

		*match* (:class:`re.Match`) is the in-parameter match.

		Returns the out-parameter replacement string (:class:`str`).
		"""
		result = match.groupdict()

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
				# Convert numeric parameter by flattening tuple values.
				out_names = []
				out_replacements = []
				for i, sub_value in enumerate(value):
					out_name = "_{}_{}".format(in_num_str, i)
					out_repl = self._out_format.format(param=out_name)
					out_names.append(out_name)
					out_replacements.append(out_repl)

				param_conversions.append((True, in_index, out_names))
				return "({})".format(",".join(out_replacements))

			else:
				# Convert numeric parameter.
				out_name = "_" + in_num_str
				out_repl = self._out_format.format(param=out_name)
				param_conversions.append((False, in_index, out_name))
				return out_repl


class _NumericToNumericConverter(_NumericConverter):
	"""
	The :class:`._NumericToNumericConverter` class is used to convert
	numeric in-style parameters to numeric out-style parameters.
	"""

	def __init__(self, **kw):
		"""
		Initializes the :class:`._NumericToNumericConverter` instance.
		"""
		super().__init__(**kw)

		self._out_start = self._out_style.start
		"""
		*start* (:class:`int`) indicates to start enumerating out-parameters
		at the specified number.
		"""

	def convert(self, sql, params):
		"""
		Convert the SQL query to use the numeric out-style parameters from
		the numeric the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Sequence` or :class:`~collections.abc.Mapping`)
		contains the in-style parameters.

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the out-style parameters (:class:`list`).
		"""
		if _is_sequence(params):
			pass
		elif isinstance(params, Mapping):
			params = self._mapping_as_sequence(params)
		else:
			raise TypeError("params:{!r} is not a sequence or mapping.".format(params))

		# Convert query.
		param_conversions = []
		out_counter = itertools.count()
		out_lookup = {}
		out_sql = self._in_regex.sub(partial(self._regex_replace, params, param_conversions, out_counter, out_lookup), sql)

		# Convert parameters.
		out_params = self._convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(self, sql, many_params):
		"""
		Convert the SQL query to use the numeric out-style parameters from
		the numeric the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set
		of in-style parameters (:class:`~collections.abc.Sequence` or
		:class:`~collections.abc.Mapping`).

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the many out-style parameters (:class:`list` of
		:class:`list`).
		"""
		iter_params = iter(many_params)
		first_params = next(iter_params)

		if _is_sequence(first_params):
			pass
		elif isinstance(first_params, Mapping):
			first_params = self._mapping_as_sequence(first_params)
		else:
			raise TypeError("many_params[0]:{!r} is not a sequence or mapping.".format(first_params))

		# Convert query.
		param_conversions = []
		out_counter = itertools.count()
		out_lookup = {}
		out_sql = self._in_regex.sub(partial(self._regex_replace, first_params, param_conversions, out_counter, out_lookup), sql)

		# Convert parameters.
		out_params = self._convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	def _convert_many_params(self, many_in_params, param_conversions):
		"""
		Convert the numeric in-style parameters to numeric out-style
		parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each
		set of in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-index (:class:`int`), and the out-index
		  (:class:`int`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-index (:class:`int`), and the out-indices
		  (:class:`list` of :class:`int`).

		Returns the many out-style parameters (:class:`list` of :class:`list`).
		"""
		# Get row size.
		last_conv = param_conversions[-1]
		size = (last_conv[2][-1] if last_conv[0] else last_conv[2]) + 1

		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i:
				if _is_sequence(in_params):
					pass
				elif isinstance(in_params, Mapping):
					in_params = self._mapping_as_sequence(in_params)
				else:
					raise TypeError("many_params[{}]:{!r} is not a mapping.".format(i, in_params))

			out_params = [None] * size
			for expand_tuple, in_index, out_index in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					values = in_params[in_index]
					out_indices = out_index
					if not isinstance(values, tuple):
						raise TypeError("many_params[{}][{!r}]:{!r} was expected to be a tuple.".format(i, in_index, values))
					elif len(values) != len(out_indices):
						raise ValueError("many_params[{}][{!r}]:{!r} length was expected to be {}.".format(i, in_index, values, len(out_indices)))

					for sub_index, sub_value in zip(out_indices, values):
						out_params[sub_index] = sub_value

				else:
					# Simple conversion.
					out_params[out_index] = in_params[in_index]

			many_out_params.append(out_params)

		return many_out_params

	def _convert_params(self, in_params, param_conversions):
		"""
		Convert the numeric in-style parameters to numeric out-style
		parameters.

		*in_params* (:class:`~collections.abc.Sequence`) contains the
		in-style parameters to sample.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-index (:class:`int`), and the out-index
		  (:class:`int`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-index (:class:`int`), and the out-indices
		  (:class:`list` of :class:`int`).

		Returns the out-style parameters (:class:`list`).
		"""
		# Get row size.
		last_conv = param_conversions[-1]
		size = (last_conv[2][-1] if last_conv[0] else last_conv[2]) + 1

		out_params = [None] * size
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

	def _regex_replace(self, in_params, param_conversions, out_counter, out_lookup, match):
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Sequence`) contains the
		in-style parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each
		parameter conversion to perform (:class:`tuple`).

		*out_counter* (:class:`~collections.abc.Iterator`) is used to
		generate new out-indices.

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
						out_num = out_index + self._out_start
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
					out_num = out_index + self._out_start
					out_repl = self._out_format.format(param=out_num)
					out_lookup[in_index] = (out_index, out_repl)
					param_conversions.append((False, in_index, out_index))

				return out_repl


class _NumericToOrdinalConverter(_NumericConverter):
	"""
	The :class:`._NumericToOrdinalConverter` class is used to convert
	numeric in-style parameters to ordinal out-style parameters.
	"""

	def convert(self, sql, params):
		"""
		Convert the SQL query to use the ordinal out-style parameters from
		the numeric the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Sequence` or :class:`~collections.abc.Mapping`)
		contains the in-style parameters.

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the out-style parameters (:class:`list`).
		"""
		if _is_sequence(params):
			pass
		elif isinstance(params, Mapping):
			params = self._mapping_as_sequence(params)
		else:
			raise TypeError("params:{!r} is not a sequence or mapping.".format(params))

		# Convert query.
		param_conversions = []
		out_format = self._out_style.out_format
		out_sql = self._in_regex.sub(partial(self._regex_replace, params, param_conversions, out_format), sql)

		# Convert parameters.
		out_params = self._convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(self, sql, many_params):
		"""
		Convert the SQL query to use the ordinal out-style parameters from
		the numeric the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set
		of in-style parameters (:class:`~collections.abc.Sequence` or
		:class:`~collections.abc.Mapping`).

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the many out-style parameters (:class:`list` of
		:class:`list`).
		"""
		iter_params = iter(many_params)
		first_params = next(iter_params)

		if _is_sequence(first_params):
			pass
		elif isinstance(first_params, Mapping):
			first_params = self._mapping_as_sequence(first_params)
		else:
			raise TypeError("many_params[0]:{!r} is not a sequence or mapping.".format(first_params))

		# Convert query.
		param_conversions = []
		out_format = self._out_style.out_format
		out_sql = self._in_regex.sub(partial(self._regex_replace, first_params, param_conversions, out_format), sql)

		# Convert parameters.
		out_params = self._convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	def _convert_many_params(self, many_in_params, param_conversions):
		"""
		Convert the numeric in-style parameters to ordinal out-style
		parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each
		set of in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-index (:class:`int`), and the out-name
		  (:class:`str`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-index (:class:`int`), and the out-names
		  (:class:`list` of :class:`str`).

		Returns the many out-style parameters (:class:`list` of :class:`list`).
		"""
		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i:
				if _is_sequence(in_params):
					pass
				elif isinstance(in_params, Mapping):
					in_params = self._mapping_as_sequence(in_params)
				else:
					raise TypeError("many_params[{}]:{!r} is not a mapping.".format(i, in_params))

			out_params = []
			for expand_tuple, in_index, out_count in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					values = in_params[in_index]
					if not isinstance(values, tuple):
						raise TypeError("many_params[{}][{!r}]:{!r} was expected to be a tuple.".format(i, in_index, values))
					elif len(values) != out_count:
						raise ValueError("many_params[{}][{!r}]:{!r} length was expected to be {}.".format(i, in_index, values, out_count))

					for sub_value in values:
						out_params.append(sub_value)

				else:
					# Simple conversion.
					out_params.append(in_params[in_index])

			many_out_params.append(out_params)

		return many_out_params

	def _convert_params(self, in_params, param_conversions):
		"""
		Convert the numeric in-style parameters to ordinal out-style
		parameters.

		*in_params* (:class:`~collections.abc.Sequence`) contains the
		in-style parameters to sample.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-index (:class:`int`), and the out-name
		  (:class:`str`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-index (:class:`int`), and the out-names
		  (:class:`list` of :class:`str`).

		Returns the out-style parameters (:class:`list`).
		"""
		out_params = []
		for expand_tuple, in_index, _out_count in param_conversions:
			if expand_tuple:
				# Tuple conversion.
				for sub_value in in_params[in_index]:
					out_params.append(sub_value)

			else:
				# Simple conversion.
				out_params.append(in_params[in_index])

		return out_params

	def _regex_replace(self, in_params, param_conversions, out_format, match):
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Sequence`) contains the
		in-style parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each
		parameter conversion to perform (:class:`tuple`).

		*out_format* (:class:`str`) is the out-style parameter format
		string.

		*match* (:class:`re.Match`) is the in-parameter match.

		Returns the out-parameter replacement string (:class:`str`).
		"""
		result = match.groupdict()

		escape = result.get('escape')
		if escape is not None:
			# Escape sequence matched, return escaped literal.
			return escape[self._escape_start:]

		else:
			# Numeric parameter matched, return ordinal out-style parameter.
			in_index = int(result['param']) - self._in_start

			value = in_params[in_index]
			if self._expand_tuples and isinstance(value, tuple):
				# Convert numeric parameter by flattening tuple values.
				param_conversions.append((True, in_index, len(value)))
				return "({})".format(",".join(out_format for _ in value))

			else:
				# Convert numeric parameter.
				param_conversions.append((False, in_index, None))
				return out_format


class _OrdinalConverter(_Converter):
	"""
	The :class:`._OrdinalConverter` class is the base class for
	implementing the conversion from one ordinal in-style parameter to
	another out-style parameter.
	"""

	@staticmethod
	def _mapping_as_sequence(in_params):
		"""
		Convert the in-parameters to mimic a sequence.

		*in_params* (:class:`~collections.abc.Mapping`) is the
		in-parameters.

		Returns the converted in-parameters (:class:`~collections.abc.Mapping`).
		"""
		return {int(__key): __value for __key, __value in in_params.items() if isinstance(__key, int) or (isinstance(__key, (str, bytes)) and __key.isdigit())}


class _OrdinalToNamedConverter(_OrdinalConverter):
	"""
	The :class:`._OrdinalToNamedConverter` class is used to convert
	ordinal in-style parameters to named out-style parameters.
	"""

	def convert(self, sql, params):
		"""
		Convert the SQL query to use the named out-style parameters from the
		ordinal the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Sequence` or :class:`~collections.abc.Mapping`)
		contains the in-style parameters.

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the out-style parameters (:class:`dict`).
		"""
		if _is_sequence(params):
			pass
		elif isinstance(params, Mapping):
			params = self._mapping_as_sequence(params)
		else:
			raise TypeError("params:{!r} is not a sequence or mapping.".format(params))

		# Convert query.
		param_conversions = []
		in_counter = itertools.count()
		out_sql = self._in_regex.sub(partial(self._regex_replace, params, param_conversions, in_counter), sql)

		# Convert parameters.
		out_params = self._convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(self, sql, many_params):
		"""
		Convert the SQL query to use the named out-style parameters from the
		ordinal the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set
		of in-style parameters (:class:`~collections.abc.Sequence` or
		:class:`~collections.abc.Mapping`).

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the many out-style parameters (:class:`list` of
		:class:`dict`).
		"""
		iter_params = iter(many_params)
		first_params = next(iter_params)

		if _is_sequence(first_params):
			pass
		elif isinstance(first_params, Mapping):
			first_params = self._mapping_as_sequence(first_params)
		else:
			raise TypeError("many_params[0]:{!r} is not a sequence or mapping.".format(first_params))

		# Convert query.
		param_conversions = []
		in_counter = itertools.count()
		out_sql = self._in_regex.sub(partial(self._regex_replace, first_params, param_conversions, in_counter), sql)

		# Convert parameters.
		out_params = self._convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	def _convert_many_params(self, many_in_params, param_conversions):
		"""
		Convert the ordinal in-style parameters to named out-style
		parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each
		set of in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-index (:class:`int`), and the out-name
		  (:class:`str`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-index (:class:`str`), and the out-names
		  (:class:`list` of :class:`str`).

		Returns the many out-style parameters (:class:`list` of :class:`dict`).
		"""
		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i:
				if _is_sequence(in_params):
					pass
				elif isinstance(in_params, Mapping):
					in_params = self._mapping_as_sequence(in_params)
				else:
					raise TypeError("many_params[{}]:{!r} is not a sequence or mapping.".format(i, in_params))

			out_params = {}
			for expand_tuple, in_index, out_name in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					out_names = out_name
					values = in_params[in_index]
					if not isinstance(values, tuple):
						raise TypeError("many_params[{}][{!r}]:{!r} was expected to be a tuple.".format(i, in_index, values))
					elif len(values) != len(out_names):
						raise ValueError("many_params[{}][{!r}]:{!r} length was expected to be {}.".format(i, in_index, values, len(out_names)))

					for sub_name, sub_value in zip(out_names, values):
						out_params[sub_name] = sub_value

				else:
					# Simple conversion.
					out_params[out_name] = in_params[in_index]

			many_out_params.append(out_params)

		return many_out_params

	def _convert_params(self, in_params, param_conversions):
		"""
		Convert the ordinal in-style parameters to named out-style
		parameters.

		*in_params* (:class:`~collections.abc.Sequence`) contains the
		in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-index (:class:`int`), and the out-name
		  (:class:`str`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-index (:class:`str`), and the out-names
		  (:class:`list` of :class:`str`).

		Returns the out-style parameters (:class:`dict`).
		"""
		out_params = {}
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

	def _regex_replace(self, in_params, param_conversions, in_counter, match):
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Sequence`) contains the
		in-style parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each
		parameter conversion to perform (:class:`tuple`).

		*in_counter* (:class:`~collections.abc.Iterator`) is used to
		generate next in-indices.

		*match* (:class:`re.Match`) is the in-parameter match.

		Returns the out-parameter replacement string (:class:`str`).
		"""
		result = match.groupdict()

		escape = result.get('escape')
		if escape is not None:
			# Escape sequence matched, return escaped literal.
			return escape[self._escape_start:]

		else:
			# Ordinal parameter matched, return named out-style parameter.
			in_index = next(in_counter)

			value = in_params[in_index]
			if self._expand_tuples and isinstance(value, tuple):
				# Convert ordinal parameter by flattening tuple values.
				out_names = []
				out_replacements = []
				for i, sub_value in enumerate(value):
					out_name = "_{}_{}".format(in_index, i)
					out_repl = self._out_format.format(param=out_name)
					out_names.append(out_name)
					out_replacements.append(out_repl)

				param_conversions.append((True, in_index, out_names))
				return "({})".format(",".join(out_replacements))

			else:
				# Convert ordinal parameter.
				out_name = "_{}".format(in_index)
				out_repl = self._out_format.format(param=out_name)
				param_conversions.append((False, in_index, out_name))
				return out_repl


class _OrdinalToNumericConverter(_OrdinalConverter):
	"""
	The :class:`._OrdinalToNumericConverter` class is used to convert
	ordinal in-style parameters to numeric out-style parameters.
	"""

	def __init__(self, **kw):
		"""
		Initializes the :class:`._OrdinalToNumericConverter` instance.
		"""
		super().__init__(**kw)

		self._out_start = self._out_style.start
		"""
		*start* (:class:`int`) indicates to start enumerating out-parameters
		at the specified number.
		"""

	def convert(self, sql, params):
		"""
		Convert the SQL query to use the numeric out-style parameters from
		the ordinal the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Sequence` or :class:`~collections.abc.Mapping`)
		contains the in-style parameters.

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the out-style parameters (:class:`list`).
		"""
		if _is_sequence(params):
			pass
		elif isinstance(params, Mapping):
			params = self._mapping_as_sequence(params)
		else:
			raise TypeError("params:{!r} is not a sequence or mapping.".format(params))

		# Convert query.
		param_conversions = []
		in_counter = itertools.count()
		out_counter = itertools.count()
		out_sql = self._in_regex.sub(partial(self._regex_replace, params, param_conversions, in_counter, out_counter), sql)

		# Convert parameters.
		out_params = self._convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(self, sql, many_params):
		"""
		Convert the SQL query to use the numeric out-style parameters from
		the ordinal the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set
		of in-style parameters (:class:`~collections.abc.Sequence` or
		:class:`~collections.abc.Mapping`).

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the many out-style parameters (:class:`list` of
		:class:`list`).
		"""
		iter_params = iter(many_params)
		first_params = next(iter_params)

		if _is_sequence(first_params):
			pass
		elif isinstance(first_params, Mapping):
			first_params = self._mapping_as_sequence(first_params)
		else:
			raise TypeError("many_params[0]:{!r} is not a sequence or mapping.".format(first_params))

		# Convert query.
		param_conversions = []
		in_counter = itertools.count()
		out_counter = itertools.count()
		out_sql = self._in_regex.sub(partial(self._regex_replace, first_params, param_conversions, in_counter, out_counter), sql)

		# Convert parameters.
		out_params = self._convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	def _convert_many_params(self, many_in_params, param_conversions):
		"""
		Convert the ordinal in-style parameters to numeric out-style
		parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each
		set of in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-index (:class:`int`), and the out-index
		  (:class:`int`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-index (:class:`int`), and the out-indices
		  (:class:`list` of :class:`int`).

		Returns the many out-style parameters (:class:`list` of :class:`list`).
		"""
		# Get row size.
		last_conv = param_conversions[-1]
		size = (last_conv[2][-1] if last_conv[0] else last_conv[2]) + 1

		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i:
				if _is_sequence(in_params):
					pass
				elif isinstance(in_params, Mapping):
					in_params = self._mapping_as_sequence(in_params)
				else:
					raise TypeError("many_params[{}]:{!r} is not a mapping.".format(i, in_params))

			out_params = [None] * size
			for expand_tuple, in_index, out_index in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					values = in_params[in_index]
					out_indices = out_index
					if not isinstance(values, tuple):
						raise TypeError("many_params[{}][{!r}]:{!r} was expected to be a tuple.".format(i, in_index, values))
					elif len(values) != len(out_indices):
						raise ValueError("many_params[{}][{!r}]:{!r} length was expected to be {}.".format(i, in_index, values, len(out_indices)))

					for sub_index, sub_value in zip(out_indices, values):
						out_params[sub_index] = sub_value

				else:
					# Simple conversion.
					out_params[out_index] = in_params[in_index]

			many_out_params.append(out_params)

		return many_out_params

	def _convert_params(self, in_params, param_conversions):
		"""
		Convert the ordinal in-style parameters to numeric out-style
		parameters.

		*in_params* (:class:`~collections.abc.Sequence`) contains the
		in-style parameters to sample.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-index (:class:`int`), and the out-index
		  (:class:`int`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-index (:class:`int`), and the out-indices
		  (:class:`list` of :class:`int`).

		Returns the out-style parameters (:class:`list`).
		"""
		# Get row size.
		last_conv = param_conversions[-1]
		size = (last_conv[2][-1] if last_conv[0] else last_conv[2]) + 1

		out_params = [None] * size
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

	def _regex_replace(self, in_params, param_conversions, in_counter, out_counter, match):
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Sequence`) contains the
		in-style parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each
		parameter conversion to perform (:class:`tuple`).

		*in_counter* (:class:`~collections.abc.Iterator`) is used to
		generate next in-indices.

		*out_counter* (:class:`~collections.abc.Iterator`) is used to
		generate new out-indices.

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
				# Convert ordinal parameter by flattening tuple values.
				out_indices = []
				out_replacements = []
				for i, sub_value in enumerate(value):
					out_index = next(out_counter)
					out_num = out_index + self._out_start
					out_repl = self._out_format.format(param=out_num)
					out_indices.append(out_index)
					out_replacements.append(out_repl)

				param_conversions.append((True, in_index, out_indices))
				return "({})".format(",".join(out_replacements))

			else:
				# Convert ordinal parameter.
				out_index = next(out_counter)
				out_num = out_index + self._out_start
				out_repl = self._out_format.format(param=out_num)
				param_conversions.append((False, in_index, out_index))
				return out_repl


class _OrdinalToOrdinalConverter(_OrdinalConverter):
	"""
	The :class:`._OrdinalToOrdinalConverter` class is used to convert
	ordinal in-style parameters to ordinal out-style parameters.
	"""

	def convert(self, sql, params):
		"""
		Convert the SQL query to use the ordinal out-style parameters from
		the ordinal the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*params* (:class:`~collections.abc.Sequence` or :class:`~collections.abc.Mapping`)
		contains the in-style parameters.

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the out-style parameters (:class:`list`).
		"""
		if _is_sequence(params):
			pass
		elif isinstance(params, Mapping):
			params = self._mapping_as_sequence(params)
		else:
			raise TypeError("params:{!r} is not a sequence or mapping.".format(params))

		# Convert query.
		param_conversions = []
		in_counter = itertools.count()
		out_format = self._out_style.out_format
		out_sql = self._in_regex.sub(partial(self._regex_replace, params, param_conversions, in_counter, out_format), sql)

		# Convert parameters.
		out_params = self._convert_params(params, param_conversions)

		return out_sql, out_params

	def convert_many(self, sql, many_params):
		"""
		Convert the SQL query to use the ordinal out-style parameters from
		the ordinal the in-style parameters.

		*sql* (:class:`str`) is the SQL query.

		*many_params* (:class:`~collections.abc.Iterable`) contains each set
		of in-style parameters (:class:`~collections.abc.Sequence` or
		:class:`~collections.abc.Mapping`).

		Returns a :class:`tuple` containing: the converted SQL query
		(:class:`str`), and the many out-style parameters (:class:`list` of
		:class:`list`).
		"""
		iter_params = iter(many_params)
		first_params = next(iter_params)

		if _is_sequence(first_params):
			pass
		elif isinstance(first_params, Mapping):
			first_params = self._mapping_as_sequence(first_params)
		else:
			raise TypeError("many_params[0]:{!r} is not a sequence or mapping.".format(first_params))

		# Convert query.
		param_conversions = []
		in_counter = itertools.count()
		out_format = self._out_style.out_format
		out_sql = self._in_regex.sub(partial(self._regex_replace, first_params, param_conversions, in_counter, out_format), sql)

		# Convert parameters.
		out_params = self._convert_many_params(itertools.chain((first_params,), iter_params), param_conversions)

		return out_sql, out_params

	def _convert_many_params(self, many_in_params, param_conversions):
		"""
		Convert the ordinal in-style parameters to ordinal out-style
		parameters.

		*many_in_params* (:class:`~collections.abc.Iterable`) contains each
		set of in-style parameters.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-index (:class:`int`), and the out-name
		  (:class:`str`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-index (:class:`int`), and the out-names
		  (:class:`list` of :class:`str`).

		Returns the many out-style parameters (:class:`list` of :class:`list`).
		"""
		many_out_params = []
		for i, in_params in enumerate(many_in_params):
			# NOTE: First set has already been checked.
			if i:
				if _is_sequence(in_params):
					pass
				elif isinstance(in_params, Mapping):
					in_params = self._mapping_as_sequence(in_params)
				else:
					raise TypeError("many_params[{}]:{!r} is not a mapping.".format(i, in_params))

			out_params = []
			for expand_tuple, in_index, out_count in param_conversions:
				if expand_tuple:
					# Tuple conversion.
					values = in_params[in_index]
					if not isinstance(values, tuple):
						raise TypeError("many_params[{}][{!r}]:{!r} was expected to be a tuple.".format(i, in_index, values))
					elif len(values) != out_count:
						raise ValueError("many_params[{}][{!r}]:{!r} length was expected to be {}.".format(i, in_index, values, out_count))

					for sub_value in values:
						out_params.append(sub_value)

				else:
					# Simple conversion.
					out_params.append(in_params[in_index])

			many_out_params.append(out_params)

		return many_out_params

	def _convert_params(self, in_params, param_conversions):
		"""
		Convert the ordinal in-style parameters to ordinal out-style
		parameters.

		*in_params* (:class:`~collections.abc.Sequence`) contains the
		in-style parameters to sample.

		*param_conversions* (:class:`list`) contains each parameter
		conversion to perform (:class:`tuple`).

		- A simple conversion contains: whether to expand tuples
		  (:data:`False`), the in-index (:class:`int`), and the out-name
		  (:class:`str`).

		- A tuple conversion contains: whether to expand tuples
		  (:data:`True`), the in-index (:class:`int`), and the out-names
		  (:class:`list` of :class:`str`).

		Returns the out-style parameters (:class:`list`).
		"""
		out_params = []
		for expand_tuple, in_index, _out_count in param_conversions:
			if expand_tuple:
				# Tuple conversion.
				for sub_value in in_params[in_index]:
					out_params.append(sub_value)

			else:
				# Simple conversion.
				out_params.append(in_params[in_index])

		return out_params

	def _regex_replace(self, in_params, param_conversions, in_counter, out_format, match):
		"""
		Regular expression replace callback.

		*in_params* (:class:`~collections.abc.Sequence`) contains the
		in-style parameters to sample.

		*param_conversions* (:class:`list`) will be outputted with each
		parameter conversion to perform (:class:`tuple`).

		*in_counter* (:class:`~collections.abc.Iterator`) is used to
		generate next in-indices.

		*out_format* (:class:`str`) is the out-style parameter format
		string.

		*match* (:class:`re.Match`) is the in-parameter match.

		Returns the out-parameter replacement string (:class:`str`).
		"""
		result = match.groupdict()

		escape = result.get('escape')
		if escape is not None:
			# Escape sequence matched, return escaped literal.
			return escape[self._escape_start:]

		else:
			# Ordinal parameter matched, return ordinal out-style parameter.
			in_index = next(in_counter)

			value = in_params[in_index]
			if self._expand_tuples and isinstance(value, tuple):
				# Convert ordinal parameter by flattening tuple values.
				param_conversions.append((True, in_index, len(value)))
				return "({})".format(",".join(out_format for _ in value))

			else:
				# Convert ordinal parameter.
				param_conversions.append((False, in_index, None))
				return out_format
