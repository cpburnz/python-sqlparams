"""
This module tests converting numeric parameters to numeric parameters.
"""

import unittest

import sqlparams


class Test(unittest.TestCase):
	"""
	The :class:`Test` class tests converting numeric parameters to numeric
	parameters.

	From: numeric, numeric_dollar.
	To: numeric, numeric_dollar.
	"""

	def test_1_numeric_dollar_to_numeric(self):
		"""
		Test converting from::

			... WHERE name = $1

		to::

			... WHERE name = :1
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric_dollar', 'numeric')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = $1 OR name = $2;
		"""
		id, name = 11, "Bofur"
		seq_params = [id, name]
		int_params = {1: id, 2: name}
		str_params = {'1': id, '2': name}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :1 OR name = :2;
		"""
		dest_params = [id, name]

		for src_params, src in zip([seq_params, int_params, str_params], ['seq', 'int', 'str']):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, params = query.format(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(params, dest_params)

	def test_1_numeric_dollar_to_numeric_many(self):
		"""
		Test converting from::

			... WHERE name = $1

		to::

			... WHERE name = :1
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric_dollar', 'numeric')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = $1 OR name = $2;
		"""
		base_params = [
			{'id': 13, 'name': "Thorin"},
			{'id': 7, 'name': "Ori"},
		]
		seq_params = [[__row['id'], __row['name']] for __row in base_params]
		int_params = [{1: __row['id'], 2: __row['name']} for __row in base_params]
		str_params = [{'1': __row['id'], '2': __row['name']} for __row in base_params]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :1 OR name = :2;
		"""
		dest_params = [[__row['id'], __row['name']] for __row in base_params]

		for src_params, src in zip([seq_params, int_params, str_params], ['seq', 'int', 'str']):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, many_params = query.formatmany(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(many_params, dest_params)

	def test_1_numeric_to_numeric_dollar(self):
		"""
		Test converting from::

			... WHERE name = :1

		to::

			... WHERE name = $1
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric', 'numeric_dollar')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :2 OR name = :1;
		"""
		id, name = 5, "Dori"
		seq_params = [name, id]
		int_params = {1: name, 2: id}
		str_params = {'1': name, '2': id}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = $1 OR name = $2;
		"""
		dest_params = [id, name]

		for src_params, src in zip([seq_params, int_params, str_params], ['seq', 'int', 'str']):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, params = query.format(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(params, dest_params)

	def test_1_numeric_to_numeric_dollar_many(self):
		"""
		Test converting from::

			... WHERE name = :1

		to::

			... WHERE name = $1
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric', 'numeric_dollar')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :2 OR name = :1;
		"""
		base_params = [
			{'id': 11, 'name': "Bofur"},
			{'id': 1, 'name': "Dwalin"},
			{'id': 5, 'name': "Dori"},
		]
		seq_params = [[__row['name'], __row['id']] for __row in base_params]
		int_params = [{1: __row['name'], 2: __row['id']} for __row in base_params]
		str_params = [{'1': __row['name'], '2': __row['id']} for __row in base_params]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = $1 OR name = $2;
		"""
		dest_params = [[__row['id'], __row['name']] for __row in base_params]

		for src_params, src in zip([seq_params, int_params, str_params], ['seq', 'int', 'str']):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, many_params = query.formatmany(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(many_params, dest_params)

	def test_2_expand_tuples(self):
		"""
		Test expanding tuples.
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric', 'numeric', expand_tuples=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = :1 AND name IN :2;
		"""
		names, race = ("Kili", "Fili"), "Dwarf"
		seq_params = [race, names]
		int_params = {1: race, 2: names}
		str_params = {'1': race, '2': names}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE race = :1 AND name IN (:2,:3);
		"""
		dest_params = [race] + list(names)

		for src_params, src in zip([seq_params, int_params, str_params], ['seq', 'int', 'str']):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, params = query.format(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(params, dest_params)

	def test_2_expand_tuples_default(self):
		"""
		Test the default behavior for expanding tuples. A numeric out-style
		should be enabled by default.
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric', 'numeric')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = :1 AND name IN :2;
		"""
		names, race = ("Kili", "Fili"), "Dwarf"
		seq_params = [race, names]
		int_params = {1: race, 2: names}
		str_params = {'1': race, '2': names}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE race = :1 AND name IN (:2,:3);
		"""
		dest_params = [race] + list(names)

		for src_params, src in zip([seq_params, int_params, str_params], ['seq', 'int', 'str']):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, params = query.format(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(params, dest_params)

	def test_2_expand_tuples_disabled(self):
		"""
		Test ignoring tuples.
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric', 'numeric', expand_tuples=False)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = :1 AND name IN :2;
		"""
		names, race = ("Kili", "Fili"), "Dwarf"
		seq_params = [race, names]
		int_params = {1: race, 2: names}
		str_params = {'1': race, '2': names}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE race = :1 AND name IN :2;
		"""
		dest_params = [race, names[:]]

		for src_params, src in zip([seq_params, int_params, str_params], ['seq', 'int', 'str']):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, params = query.format(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(params, dest_params)

	def test_2_expand_tuples_many(self):
		"""
		Test expanding many tuples.
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric', 'numeric', expand_tuples=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = :1 AND name IN :2;
		"""
		base_params = [
			{'names': ("Dwalin", "Balin"), 'race': "Dwarf"},
			{'names': ("Kili", "Fili"), 'race': "Dwarf"},
			{'names': ("Oin", "Gloin"), 'race': "Dwarf"},
		]
		seq_params = [[__row['race'], __row['names']] for __row in base_params]
		int_params = [{1: __row['race'], 2: __row['names']} for __row in base_params]
		str_params = [{'1': __row['race'], '2': __row['names']} for __row in base_params]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE race = :1 AND name IN (:2,:3);
		"""
		dest_params = [[__row['race']] + list(__row['names']) for __row in base_params]

		for src_params, src in zip([seq_params, int_params, str_params], ['seq', 'int', 'str']):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, many_params = query.formatmany(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(many_params, dest_params)

	def test_2_expand_tuples_many_fail_length(self):
		"""
		Test many tuples with differing lengths.
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric', 'numeric', expand_tuples=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = :1 AND name IN :2;
		"""
		base_params = [
			{'names': ("Dori", "Ori", "Nori"), 'race': "Dwarf"},
			{'names': ("Thorin",), 'race': "Dwarf"},
		]
		seq_params = [[__row['race'], __row['names']] for __row in base_params]
		int_params = [{1: __row['race'], 2: __row['names']} for __row in base_params]
		str_params = [{'1': __row['race'], '2': __row['names']} for __row in base_params]

		for src_params, src in zip([seq_params, int_params, str_params], ['seq', 'int', 'str']):
			with self.subTest(src=src):
				# Format SQL with params.
				with self.assertRaisesRegex(ValueError, "length was expected to be 3.$"):
					query.formatmany(src_sql, src_params)

	def test_2_expand_tuples_many_fail_type(self):
		"""
		Test many tuples with wrong types.
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric', 'numeric', expand_tuples=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = :1 AND name IN :2;
		"""
		base_params = [
			{'names': ("Dori", "Ori", "Nori"), 'race': "Dwarf"},
			{'names': "Thorin", 'race': "Dwarf"},
		]
		seq_params = [[__row['race'], __row['names']] for __row in base_params]
		int_params = [{1: __row['race'], 2: __row['names']} for __row in base_params]
		str_params = [{'1': __row['race'], '2': __row['names']} for __row in base_params]

		for src_params, src in zip([seq_params, int_params, str_params], ['seq', 'int', 'str']):
			with self.subTest(src=src):
				# Format SQL with params.
				with self.assertRaisesRegex(TypeError, "was expected to be a tuple.$"):
					query.formatmany(src_sql, src_params)

	def test_3_multiple(self):
		"""
		Test converting a numeric parameter where it occurs multiple times.
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric', 'numeric')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :1 OR name = :2 OR altid = :1 OR altname = :2;
		"""
		id, name = 3, "Kili"
		seq_params = [id, name]
		int_params = {1: id, 2: name}
		str_params = {'1': id, '2': name}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :1 OR name = :2 OR altid = :1 OR altname = :2;
		"""
		dest_params = [id, name]

		for src_params, src in zip([seq_params, int_params, str_params], ['seq', 'int', 'str']):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, params = query.format(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(params, dest_params)

	def test_3_multiple_many(self):
		"""
		Test converting a numeric parameter where it occurs multiple times.
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric', 'numeric')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :1 OR name = :2 OR altid = :1 OR altname = :2;
		"""
		base_params = [
			{'id': 11, 'name': "Bofur"},
			{'id': 12, 'name': "Bombur"},
			{'id': 9, 'name': "Gloin"},
		]
		seq_params = [[__row['id'], __row['name']] for __row in base_params]
		int_params = [{1: __row['id'], 2: __row['name']} for __row in base_params]
		str_params = [{'1': __row['id'], '2': __row['name']} for __row in base_params]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :1 OR name = :2 OR altid = :1 OR altname = :2;
		"""
		dest_params = [[__row['id'], __row['name']] for __row in base_params]

		for src_params, src in zip([seq_params, int_params, str_params], ['seq', 'int', 'str']):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, many_params = query.formatmany(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(many_params, dest_params)

	def test_4_numeric_dollar_escape_char(self):
		"""
		Test escaping a numeric dollar parameter.
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric_dollar', 'numeric', escape_char=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = $1 AND tag IN ('$$Y2941', '$$2941');
		"""
		name = "Bilbo"
		src_params = [name]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE name = :1 AND tag IN ('$Y2941', '$2941');
		"""
		dest_params = [name]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_4_numeric_dollar_escape_char_disabled(self):
		"""
		Test disabling escaping of a numeric dollar parameter.
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric_dollar', 'numeric', escape_char=False)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = $1 AND tag IN ('$Y2941', '$$2941');
		"""
		name = "Bilbo"
		src_params = [name]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE name = :1 AND tag IN ('$Y2941', '$$2941');
		"""
		dest_params = [name]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_4_numeric_escape_char(self):
		"""
		Test escaping a numeric parameter.
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric', 'numeric', escape_char=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = :1 AND tag IN ('::Y2941', '::2941');
		"""
		name = "Bilbo"
		src_params = [name]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE name = :1 AND tag IN (':Y2941', ':2941');
		"""
		dest_params = [name]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_4_numeric_escape_char_disabled(self):
		"""
		Test disabling escaping of a numeric parameter.
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric', 'numeric', escape_char=False)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = :1 AND tag IN (':Y2941', '::2941');
		"""
		name = "Bilbo"
		src_params = [name]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE name = :1 AND tag IN (':Y2941', '::2941');
		"""
		dest_params = [name]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_numeric_to_numeric_dollar_unescaped_percent(self):
		"""
		Test converting from::

			SELECT 5 % :1

		to::

			SELECT 5 % $1
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric', 'numeric_dollar')

		# Source SQL and params.
		src_sql = """
			SELECT 5 % :1;
		"""
		value = 2
		src_params = [value]

		# Desired SQL and params.
		dest_sql = """
			SELECT 5 % $1;
		"""
		dest_params = [value]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_numeric_dollar_to_numeric_unescaped_percent(self):
		"""
		Test converting from::

			SELECT 5 % $1

		to::

			SELECT 5 % :1
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric_dollar', 'numeric')

		# Source SQL and params.
		src_sql = """
			SELECT 5 % $1;
		"""
		value = 2
		src_params = [value]

		# Desired SQL and params.
		dest_sql = """
			SELECT 5 % :1;
		"""
		dest_params = [value]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)
