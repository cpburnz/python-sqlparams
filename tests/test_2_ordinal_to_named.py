"""
This module tests converting ordinal parameters to named parameters.
"""

import unittest

import sqlparams


class Test(unittest.TestCase):
	"""
	The :class:`Test` class tests converting ordinal parameters to named
	parameters.

	From: format, qmark.
	To: named, named_dollar, named_oracle, pyformat.
	"""

	def test_1_format_to_named(self):
		"""
		Test converting from::

		  ... WHERE name = %s

		to::

		  ... WHERE name = :_0
		"""
		# Create instance.
		query = sqlparams.SQLParams('format', 'named')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = %s OR name = %s;
		"""
		id, name = 9, "Gloin"
		seq_params = [id, name]
		int_params = {0: id, 1: name}
		str_params = {'0': id, '1': name}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :_0 OR name = :_1;
		"""
		dest_params = {'_0': id, '_1': name}

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, params = query.format(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(params, dest_params)

	def test_1_format_to_named_many(self):
		"""
		Test converting from::

		  ... WHERE name = %s

		to::

		  ... WHERE name = :_0
		"""
		# Create instance.
		query = sqlparams.SQLParams('format', 'named')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = %s OR name = %s;
		"""
		base_params = [
			{'id': 8, 'name': "Oin"},
			{'id': 10, 'name': "Bifur"},
		]
		seq_params = [[__row['id'], __row['name']] for __row in base_params]
		int_params = [{0: __row['id'], 1: __row['name']} for __row in base_params]
		str_params = [{'0': __row['id'], '1': __row['name']} for __row in base_params]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :_0 OR name = :_1;
		"""
		dest_params = [{
			'_0': __row['id'],
			'_1': __row['name'],
		} for __row in base_params]

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, many_params = query.formatmany(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(many_params, dest_params)

	def test_1_format_to_pyformat(self):
		"""
		Test converting from::

		  ... WHERE name = %s

		to::

		  ... WHERE name = %(_0)s
		"""
		# Create instance.
		query = sqlparams.SQLParams('format', 'pyformat')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = %s OR id = %s;
		"""
		id, name = 10, "Bifur"
		seq_params = [name, id]
		int_params = {1: id, 0: name}
		str_params = {'1': id, '0': name}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE name = %(_0)s OR id = %(_1)s;
		"""
		dest_params = {'_1': id, '_0': name}

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, params = query.format(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(params, dest_params)

	def test_1_format_to_pyformat_many(self):
		"""
		Test converting from::

		  ... WHERE name = %s

		to::

		  ... WHERE name = %(_0)s
		"""
		# Create instance.
		query = sqlparams.SQLParams('format', 'pyformat')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = %s OR id = %s;
		"""
		base_params = [
			{'id': 8, 'name': "Oin"},
			{'id': 7, 'name': "Ori"},
			{'id': 1, 'name': "Dwalin"},
		]
		seq_params = [[__row['name'], __row['id']] for __row in base_params]
		int_params = [{1: __row['id'], 0: __row['name']} for __row in base_params]
		str_params = [{'1': __row['id'], '0': __row['name']} for __row in base_params]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE name = %(_0)s OR id = %(_1)s;
		"""
		dest_params = [{
			'_1': __row['id'],
			'_0': __row['name'],
		} for __row in base_params]

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, many_params = query.formatmany(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(many_params, dest_params)

	def test_1_qmark_to_named_dollar(self):
		"""
		Test converting from::

		  ... WHERE name = ?

		to::

		  ... WHERE name = $_0
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'named_dollar')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = ? OR name = ?;
		"""
		id, name = 7, "Ori"
		seq_params = [id, name]
		int_params = {0: id, 1: name}
		str_params = {'0': id, '1': name}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = $_0 OR name = $_1;
		"""
		dest_params = {'_0': id, '_1': name}

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, params = query.format(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(params, dest_params)

	def test_1_qmark_to_named_dollar_many(self):
		"""
		Test converting from::

		  ... WHERE name = ?

		to::

		  ... WHERE name = $_0
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'named_dollar')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = ? OR name = ?;
		"""
		base_params = [
			{'id': 1, 'name': "Dwalin"},
			{'id': 13, 'name': "Thorin"},
			{'id': 5, 'name': "Dori"},
			{'id': 7, 'name': "Ori"},
		]
		seq_params = [[__row['id'], __row['name']] for __row in base_params]
		int_params = [{0: __row['id'], 1: __row['name']} for __row in base_params]
		str_params = [{'0': __row['id'], '1': __row['name']} for __row in base_params]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = $_0 OR name = $_1;
		"""
		dest_params = [{
			'_0': __row['id'],
			'_1': __row['name'],
		} for __row in base_params]

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, many_params = query.formatmany(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(many_params, dest_params)

	def test_1_qmark_to_named_oracle_1_no_quotes(self):
		"""
		Test converting from::

		  ... WHERE name = ?

		to::

		  ... WHERE name = :_0
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'named_oracle')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = ? OR name = ?;
		"""
		id, name = 7, "Ori"
		seq_params = [id, name]
		int_params = {0: id, 1: name}
		str_params = {'0': id, '1': name}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :_0 OR name = :_1;
		"""
		dest_params = {'_0': id, '_1': name}

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, params = query.format(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(params, dest_params)

	def test_1_qmark_to_named_oracle_1_quotes(self):
		"""
		Test converting from::

		  ... WHERE name = ?

		to::

		  ... WHERE name = :"_0"
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'named_oracle', allow_out_quotes=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = ? OR name = ?;
		"""
		id, name = 7, "Ori"
		seq_params = [id, name]
		int_params = {0: id, 1: name}
		str_params = {'0': id, '1': name}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :"_0" OR name = :"_1";
		"""
		dest_params = {'"_0"': id, '"_1"': name}

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, params = query.format(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(params, dest_params)

	def test_1_qmark_to_named_oracle_2_many_no_quotes(self):
		"""
		Test converting from::

		  ... WHERE name = ?

		to::

		  ... WHERE name = :_0
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'named_oracle')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = ? OR name = ?;
		"""
		base_params = [
			{'id': 1, 'name': "Dwalin"},
			{'id': 13, 'name': "Thorin"},
			{'id': 5, 'name': "Dori"},
			{'id': 7, 'name': "Ori"},
		]
		seq_params = [[__row['id'], __row['name']] for __row in base_params]
		int_params = [{0: __row['id'], 1: __row['name']} for __row in base_params]
		str_params = [{'0': __row['id'], '1': __row['name']} for __row in base_params]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :_0 OR name = :_1;
		"""
		dest_params = [{
			'_0': __row['id'],
			'_1': __row['name'],
		} for __row in base_params]

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, many_params = query.formatmany(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(many_params, dest_params)

	def test_1_qmark_to_named_oracle_2_many_quotes(self):
		"""
		Test converting from::

		  ... WHERE name = ?

		to::

		  ... WHERE name = :_0
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'named_oracle', allow_out_quotes=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = ? OR name = ?;
		"""
		base_params = [
			{'id': 1, 'name': "Dwalin"},
			{'id': 13, 'name': "Thorin"},
			{'id': 5, 'name': "Dori"},
			{'id': 7, 'name': "Ori"},
		]
		seq_params = [[__row['id'], __row['name']] for __row in base_params]
		int_params = [{0: __row['id'], 1: __row['name']} for __row in base_params]
		str_params = [{'0': __row['id'], '1': __row['name']} for __row in base_params]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :"_0" OR name = :"_1";
		"""
		dest_params = [{
			'"_0"': __row['id'],
			'"_1"': __row['name'],
		} for __row in base_params]

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, many_params = query.formatmany(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(many_params, dest_params)

	def test_1_qmark_to_named_sqlserver(self):
		"""
		Test converting from::

		  ... WHERE name = ?

		to::

		  ... WHERE name = @_0
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'named_sqlserver')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = ? OR name = ?;
		"""
		id, name = 7, "Ori"
		seq_params = [id, name]
		int_params = {0: id, 1: name}
		str_params = {'0': id, '1': name}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = @_0 OR name = @_1;
		"""
		dest_params = {'_0': id, '_1': name}

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, params = query.format(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(params, dest_params)

	def test_1_qmark_to_named_sqlserver_many(self):
		"""
		Test converting from::

		  ... WHERE name = ?

		to::

		  ... WHERE name = @_0
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'named_sqlserver')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = ? OR name = ?;
		"""
		base_params = [
			{'id': 1, 'name': "Dwalin"},
			{'id': 13, 'name': "Thorin"},
			{'id': 5, 'name': "Dori"},
			{'id': 7, 'name': "Ori"},
		]
		seq_params = [[__row['id'], __row['name']] for __row in base_params]
		int_params = [{0: __row['id'], 1: __row['name']} for __row in base_params]
		str_params = [{'0': __row['id'], '1': __row['name']} for __row in base_params]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = @_0 OR name = @_1;
		"""
		dest_params = [{
			'_0': __row['id'],
			'_1': __row['name'],
		} for __row in base_params]

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
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
		query = sqlparams.SQLParams('qmark', 'named', expand_tuples=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = ? AND name IN ?;
		"""
		names, race = ("Kili", "Fili"), "Dwarf"
		seq_params = [race, names]
		int_params = {0: race, 1: names}
		str_params = {'0': race, '1': names}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE race = :_0 AND name IN (:_1_0,:_1_1);
		"""
		dest_params = {'_0': race, '_1_0': names[0], '_1_1': names[1]}

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, params = query.format(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(params, dest_params)

	def test_2_expand_tuples_default(self):
		"""
		Test the default behavior for expanding tuples. A named out-style
		should be disabled by default.
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'named')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = ? AND name IN ?;
		"""
		names, race = ("Kili", "Fili"), "Dwarf"
		seq_params = [race, names]
		int_params = {0: race, 1: names}
		str_params = {'0': race, '1': names}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE race = :_0 AND name IN :_1;
		"""
		dest_params = {'_0': race, '_1': names[:]}

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
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
		query = sqlparams.SQLParams('qmark', 'named', expand_tuples=False)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = ? AND name IN ?;
		"""
		names, race = ("Kili", "Fili"), "Dwarf"
		seq_params = [race, names]
		int_params = {0: race, 1: names}
		str_params = {'0': race, '1': names}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE race = :_0 AND name IN :_1;
		"""
		dest_params = {'_0': race, '_1': names[:]}

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, params = query.format(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(params, dest_params)

	def test_2_expand_tuples_empty(self):
		"""
		Test expanding empty tuples.
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'named', expand_tuples=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = ? AND name IN ?;
		"""
		names, race = (), "Dwarf"
		seq_params = [race, names]
		int_params = {0: race, 1: names}
		str_params = {'0': race, '1': names}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE race = :_0 AND name IN (NULL);
		"""
		dest_params = {'_0': race}

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
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
		query = sqlparams.SQLParams('qmark', 'named', expand_tuples=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = ? AND name IN ?;
		"""
		base_params = [
			{'names': ("Dwalin", "Balin"), 'race': "Dwarf"},
			{'names': ("Kili", "Fili"), 'race': "Dwarf"},
			{'names': ("Oin", "Gloin"), 'race': "Dwarf"},
		]
		seq_params = [[__row['race'], __row['names']] for __row in base_params]
		int_params = [{
			0: __row['race'],
			1: __row['names'],
		} for __row in base_params]
		str_params = [{
			'0': __row['race'],
			'1': __row['names'],
		} for __row in base_params]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE race = :_0 AND name IN (:_1_0,:_1_1);
		"""
		dest_params = [{
			'_0': __row['race'],
			'_1_0': __row['names'][0],
			'_1_1': __row['names'][1],
		} for __row in base_params]

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
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
		query = sqlparams.SQLParams('qmark', 'named', expand_tuples=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = ? AND name IN ?;
		"""
		base_params = [
			{'names': ("Dori", "Ori", "Nori"), 'race': "Dwarf"},
			{'names': ("Thorin",), 'race': "Dwarf"},
		]
		seq_params = [[__row['race'], __row['names']] for __row in base_params]
		int_params = [{
			0: __row['race'],
			1: __row['names'],
		} for __row in base_params]
		str_params = [{
			'0': __row['race'],
			'1': __row['names'],
		} for __row in base_params]

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				with self.assertRaisesRegex(ValueError, "length was expected to be 3.$"):
					query.formatmany(src_sql, src_params)

	def test_2_expand_tuples_many_fail_type(self):
		"""
		Test many tuples with wrong types.
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'named', expand_tuples=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = ? AND name IN ?;
		"""
		base_params = [
			{'names': ("Dori", "Ori", "Nori"), 'race': "Dwarf"},
			{'names': "Thorin", 'race': "Dwarf"},
		]
		seq_params = [[__row['race'], __row['names']] for __row in base_params]
		int_params = [{
			0: __row['race'],
			1: __row['names'],
		} for __row in base_params]
		str_params = [{
			'0': __row['race'],
			'1': __row['names'],
		} for __row in base_params]

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				with self.assertRaisesRegex(TypeError, "was expected to be a tuple.$"):
					query.formatmany(src_sql, src_params)

	def test_3_multiple(self):
		"""
		Test converting an ordinal parameter where it occurs multiple times.
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'named')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = ? OR name = ? OR altid = ? OR altname = ?;
		"""
		id, name = 3, "Kili"
		seq_params = [id, name, id, name]
		int_params = {0: id, 1: name, 2: id, 3: name}
		str_params = {'0': id, '1': name, '2': id, '3': name}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :_0 OR name = :_1 OR altid = :_2 OR altname = :_3;
		"""
		dest_params = {'_0': id, '_1': name, '_2': id, '_3': name}

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, params = query.format(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(params, dest_params)

	def test_3_multiple_many(self):
		"""
		Test converting a ordinal parameter where it occurs multiple times.
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'named')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = ? OR name = ? OR altid = ? OR altname = ?;
		"""
		base_params = [
			{'id': 11, 'name': "Bofur"},
			{'id': 12, 'name': "Bombur"},
			{'id': 9, 'name': "Gloin"},
		]
		seq_params = [
			[__row['id'], __row['name'], __row['id'], __row['name']]
			for __row in base_params
		]
		int_params = [{
			0: __row['id'],
			1: __row['name'],
			2: __row['id'],
			3: __row['name'],
		} for __row in base_params]
		str_params = [{
			'0': __row['id'],
			'1': __row['name'],
			'2': __row['id'],
			'3': __row['name'],
		} for __row in base_params]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :_0 OR name = :_1 OR altid = :_2 OR altname = :_3;
		"""
		dest_params = [{
			'_0': __row['id'],
			'_1': __row['name'],
			'_2': __row['id'],
			'_3': __row['name'],
		} for __row in base_params]

		for src_params, src in zip(
			[seq_params, int_params, str_params],
			['seq', 'int', 'str'],
		):
			with self.subTest(src=src):
				# Format SQL with params.
				sql, many_params = query.formatmany(src_sql, src_params)

				# Make sure desired SQL and parameters are created.
				self.assertEqual(sql, dest_sql)
				self.assertEqual(many_params, dest_params)

	def test_4_format_escape_char(self):
		"""
		Test escaping a format parameter.
		"""
		# Create instance.
		query = sqlparams.SQLParams('format', 'named', escape_char=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = %s AND tag IN ('%%Y2941', '%%2941', '%%s');
		"""
		name = "Bilbo"
		src_params = [name]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE name = :_0 AND tag IN ('%Y2941', '%2941', '%s');
		"""
		dest_params = {'_0': name}

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_4_format_escape_char_disabled(self):
		"""
		Test disabling escaping of a format parameter.
		"""
		# Create instance.
		query = sqlparams.SQLParams('format', 'named', escape_char=False)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = %s AND tag IN ('%Y2941', '%2941', '%%s');
		"""
		name = "Bilbo"
		src_params = [name]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE name = :_0 AND tag IN ('%Y2941', '%2941', '%%s');
		"""
		dest_params = {'_0': name}

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_4_qmark_escape_char(self):
		"""
		Test escaping a qmark parameter.
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'named', escape_char=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = ? AND tag IN ('??Y2941', '??2941', '??');
		"""
		name = "Bilbo"
		src_params = [name]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE name = :_0 AND tag IN ('?Y2941', '?2941', '?');
		"""
		dest_params = {'_0': name}

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_4_qmark_escape_char_disabled(self):
		"""
		Test disabling escaping of a qmark parameter.
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'named', escape_char=False)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = ? AND tag IN ('??Y2941', '??2941', '??');
		"""
		name = "Bilbo"
		src_params = [name]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE name = :_0 AND tag IN ('??Y2941', '??2941', '??');
		"""
		dest_params = {'_0': name}

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_format_to_named_collapsed_percent(self):
		"""
		Test converting from::

			SELECT 5 %% %s

		to::

			SELECT 5 % :_0
		"""
		# Create instance.
		query = sqlparams.SQLParams('format', 'named', escape_char=True)

		# Source SQL and params.
		src_sql = """
			SELECT 5 %% %s;
		"""
		value = 2
		src_params = [value]

		# Desired SQL and params.
		dest_sql = """
			SELECT 5 % :_0;
		"""
		dest_params = {'_0': value}

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_format_to_pyformat_unescaped_percent(self):
		"""
		Test converting from::

			SELECT 5 %% %s

		to::

			SELECT 5 %% %(_0)s
		"""
		# Create instance.
		query = sqlparams.SQLParams('format', 'pyformat')

		# Source SQL and params.
		src_sql = """
			SELECT 5 %% %s;
		"""
		value = 2
		src_params = [value]

		# Desired SQL and params.
		dest_sql = """
			SELECT 5 %% %(_0)s;
		"""
		dest_params = {'_0': value}

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_qmark_to_named_unescaped_percent(self):
		"""
		Test converting from::

			SELECT 5 % ?

		to::

			SELECT 5 % :_0
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'named')

		# Source SQL and params.
		src_sql = """
			SELECT 5 % ?;
		"""
		value = 2
		src_params = [value]

		# Desired SQL and params.
		dest_sql = """
			SELECT 5 % :_0;
		"""
		dest_params = {'_0': value}

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_qmark_to_pyformat_unescaped_percent(self):
		"""
		Test converting from::

			SELECT 5 % ?

		to::

			SELECT 5 %% %(_0)s
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'pyformat')

		# Source SQL and params.
		src_sql = """
			SELECT 5 % ?;
		"""
		value = 2
		src_params = [value]

		# Desired SQL and params.
		dest_sql = """
			SELECT 5 %% %(_0)s;
		"""
		dest_params = {'_0': value}

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)
