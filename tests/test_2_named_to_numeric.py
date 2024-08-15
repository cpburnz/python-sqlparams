"""
This module tests converting named parameters to numeric parameters.
"""

import unittest

import sqlparams


class Test(unittest.TestCase):
	"""
	The :class:`Test` class tests converting named parameters to numeric
	parameters.

	From: named, named_dollar, pyformat.
	To: numeric, numeric_dollar.
	"""

	def test_1_named_to_numeric_dollar(self):
		"""
		Test converting from::

			... WHERE name = :name

		to::

			... WHERE name = $1
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'numeric_dollar')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :id OR name = :name;
		"""
		src_params = {'id': 4, 'name': "Fili"}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = $1 OR name = $2;
		"""
		dest_params = [src_params['id'], src_params['name']]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_1_named_to_numeric_dollar_many(self):
		"""
		Test converting from::

			... WHERE name = :name

		to::

			... WHERE name = $1
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'numeric_dollar')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :id OR name = :name;
		"""
		src_params = [
			{'id': 9, 'name': "Gloin"},
			{'id': 2, 'name': "Balin"},
		]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = $1 OR name = $2;
		"""
		dest_params = [[__row['id'], __row['name']] for __row in src_params]

		# Format SQL with params.
		sql, many_params = query.formatmany(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(many_params, dest_params)

	def test_1_named_dollar_to_numeric(self):
		"""
		Test converting from::

			... WHERE name = $name

		to::

			... WHERE name = :1
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_dollar', 'numeric')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = $name OR id = $id;
		"""
		src_params = {'id': 11, 'name': "Bofur"}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE name = :1 OR id = :2;
		"""
		dest_params = [src_params['name'], src_params['id']]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_1_named_dollar_to_numeric_many(self):
		"""
		Test converting from::

			... WHERE name = $name

		to::

			... WHERE name = :1
		"""
		id, name = 11, "Bofur"

		# Create instance.
		query = sqlparams.SQLParams('named_dollar', 'numeric')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = $name OR id = $id;
		"""
		src_params = [
			{'id': 6, 'name': "Nori"},
			{'id': 13, 'name': "Thorin"},
			{'id': 1, 'name': "Dwalin"},
		]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE name = :1 OR id = :2;
		"""
		dest_params = [[__row['name'], __row['id']] for __row in src_params]

		# Format SQL with params.
		sql, many_params = query.formatmany(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(many_params, dest_params)

	def test_1_named_oracle_1_to_numeric_1_no_quotes(self):
		"""
		Test converting from::

			... WHERE name = :name

		to::

			... WHERE name = :1
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_oracle', 'numeric')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :ID OR name = :Name AND race = :race;
		"""
		src_params = {'id': 4, 'NAME': "Fili", 'Race': "dwarf"}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :1 OR name = :2 AND race = :3;
		"""
		dest_params = [src_params[__key] for __key in ['id', 'NAME', 'Race']]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_1_named_oracle_1_to_numeric_2_quotes(self):
		"""
		Test converting from::

			... WHERE name = :"name"

		to::

			... WHERE name = :1
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_oracle', 'numeric')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :"ID" OR name = :"Name" AND race = :"race";
		"""
		src_params = {'"ID"': 4, '"Name"': "Fili", '"race"': "dwarf"}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :1 OR name = :2 AND race = :3;
		"""
		dest_params = [src_params[__key] for __key in ['"ID"', '"Name"', '"race"']]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_1_named_oracle_1_to_numeric_3_mixed(self):
		"""
		Test converting from::

			... WHERE name = :"name"

		to::

			... WHERE name = :1
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_oracle', 'numeric')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :"ID" OR name = :"Name" AND race = :race;
		"""
		src_params = {'id': 4, '"Name"': "Fili", '"RACE"': "dwarf"}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :1 OR name = :2 AND race = :3;
		"""
		dest_params = [src_params[__key] for __key in ['id', '"Name"', '"RACE"']]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_1_named_oracle_2_to_numeric_many_1_no_quotes(self):
		"""
		Test converting from::

			... WHERE name = :name

		to::

			... WHERE name = :1
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_oracle', 'numeric')

		# Source SQL and params.
		# - WARNING: Only the first row is scanned for the in-parameter names. All
		#   subsequent rows must have the exact same in-parameter names.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :ID OR name = :Name AND race = :race;
		"""
		src_params = [
			{'id': 7, 'NAME': "Ori", 'Race': "dwarf"},
			{'id': 5, 'NAME': "Dori", 'Race': "dwarf"},
			{'id': 10, 'NAME': "Bifur", 'Race': "dwarf"},
		]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :1 OR name = :2 AND race = :3;
		"""
		dest_params = [
			[__row[__key] for __key in ['id', 'NAME', 'Race']]
			for __row in src_params
		]

		# Format SQL with params.
		sql, many_params = query.formatmany(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(many_params, dest_params)

	def test_1_named_oracle_2_to_numeric_many_2_quotes(self):
		"""
		Test converting from::

			... WHERE name = :"name"

		to::

			... WHERE name = :1
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_oracle', 'numeric')

		# Source SQL and params.
		# - WARNING: Only the first row is scanned for the in-parameter names. All
		#   subsequent rows must have the exact same in-parameter names.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :"ID" OR name = :"Name" AND race = :"race";
		"""
		src_params = [
			{'"ID"': 7, '"Name"': "Ori", '"race"': "dwarf"},
			{'"ID"': 5, '"Name"': "Dori", '"race"': "dwarf"},
			{'"ID"': 10, '"Name"': "Bifur", '"race"': "dwarf"},
		]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :1 OR name = :2 AND race = :3;
		"""
		dest_params = [
			[__row[__key] for __key in ['"ID"', '"Name"', '"race"']]
			for __row in src_params
		]

		# Format SQL with params.
		sql, many_params = query.formatmany(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(many_params, dest_params)

	def test_1_named_oracle_2_to_numeric_many_3_mixed(self):
		"""
		Test converting from::

			... WHERE name = :"name"

		to::

			... WHERE name = :1
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_oracle', 'numeric')

		# Source SQL and params.
		# - WARNING: Only the first row is scanned for the in-parameter names. All
		#   subsequent rows must have the exact same in-parameter names.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :"ID" OR name = :"Name" AND race = :race;
		"""
		src_params = [
			{'id': 7, '"Name"': "Ori", '"RACE"': "dwarf"},
			{'id': 5, '"Name"': "Dori", '"RACE"': "dwarf"},
			{'id': 10, '"Name"': "Bifur", '"RACE"': "dwarf"},
		]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :1 OR name = :2 AND race = :3;
		"""
		dest_params = [
			[__row[__key] for __key in ['id', '"Name"', '"RACE"']]
			for __row in src_params
		]

		# Format SQL with params.
		sql, many_params = query.formatmany(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(many_params, dest_params)

	def test_1_pyformat_to_numeric_dollar(self):
		"""
		Test converting from::

			... WHERE name = %(name)s

		to::

			... WHERE name = $1
		"""
		# Create instance.
		query = sqlparams.SQLParams('pyformat', 'numeric_dollar')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = %(id)s OR name = %(name)s;
		"""
		src_params = {'id': 8, 'name': "Oin"}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = $1 OR name = $2;
		"""
		dest_params = [src_params['id'], src_params['name']]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_1_pyformat_to_numeric_dollar_many(self):
		"""
		Test converting from::

			... WHERE name = %(name)s

		to::

			... WHERE name = $1
		"""
		# Create instance.
		query = sqlparams.SQLParams('pyformat', 'numeric_dollar')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = %(id)s OR name = %(name)s;
		"""
		src_params = [
			{'id': 7, 'name': "Ori"},
			{'id': 5, 'name': "Dori"},
			{'id': 11, 'name': "Bofur"},
			{'id': 1, 'name': "Dwalin"},
		]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = $1 OR name = $2;
		"""
		dest_params = [[__row['id'], __row['name']] for __row in src_params]

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
		query = sqlparams.SQLParams('named', 'numeric', expand_tuples=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = :race AND name IN :names;
		"""
		src_params = {'names': ("Dwalin", "Balin"), 'race': "Dwarf"}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE race = :1 AND name IN (:2,:3);
		"""
		dest_params = [src_params['race']] + list(src_params['names'])

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
		query = sqlparams.SQLParams('named', 'numeric')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = :race AND name IN :names;
		"""
		src_params = {'names': ("Dwalin", "Balin"), 'race': "Dwarf"}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE race = :1 AND name IN (:2,:3);
		"""
		dest_params = [src_params['race']] + list(src_params['names'])

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
		query = sqlparams.SQLParams('named', 'numeric', expand_tuples=False)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = :race AND name IN :names;
		"""
		src_params = {'names': ("Dwalin", "Balin"), 'race': "Dwarf"}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE race = :1 AND name IN :2;
		"""
		dest_params = [src_params['race'], src_params['names']]

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
		query = sqlparams.SQLParams('named', 'numeric', expand_tuples=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = :race AND name IN :names;
		"""
		src_params = {'names': (), 'race': "Dwarf"}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE race = :1 AND name IN (NULL);
		"""
		dest_params = [src_params['race']]

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
		query = sqlparams.SQLParams('named', 'numeric', expand_tuples=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = :race AND name IN :names;
		"""
		src_params = [
			{'names': ("Dwalin", "Balin"), 'race': "Dwarf"},
			{'names': ("Kili", "Fili"), 'race': "Dwarf"},
			{'names': ("Oin", "Gloin"), 'race': "Dwarf"},
		]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE race = :1 AND name IN (:2,:3);
		"""
		dest_params = [[__row['race']] + list(__row['names']) for __row in src_params]

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
		query = sqlparams.SQLParams('named', 'numeric', expand_tuples=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = :race AND name IN :names;
		"""
		src_params = [
			{'names': ("Dori", "Ori", "Nori"), 'race': "Dwarf"},
			{'names': ("Thorin",), 'race': "Dwarf"},
		]

		# Format SQL with params.
		with self.assertRaisesRegex(ValueError, "length was expected to be 3.$"):
			query.formatmany(src_sql, src_params)

	def test_2_expand_tuples_many_fail_type(self):
		"""
		Test many tuples with wrong types.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'numeric', expand_tuples=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE race = :race AND name IN :names;
		"""
		src_params = [
			{'names': ("Dori", "Ori", "Nori"), 'race': "Dwarf"},
			{'names': "Thorin", 'race': "Dwarf"},
		]

		# Format SQL with params.
		with self.assertRaisesRegex(TypeError, "was expected to be a tuple.$"):
			query.formatmany(src_sql, src_params)

	def test_3_multiple(self):
		"""
		Test converting a named parameter where it occurs multiple times.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'numeric')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :id OR name = :name OR altid = :id OR altname = :name;
		"""
		src_params = {'id': 4, 'name': "Fili"}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :1 OR name = :2 OR altid = :1 OR altname = :2;
		"""
		dest_params = [src_params['id'], src_params['name']]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_3_multiple_many(self):
		"""
		Test converting a named parameter where it occurs multiple times.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'numeric')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :id OR name = :name OR altid = :id OR altname = :name;
		"""
		src_params = [
			{'id': 12, 'name': "Bombur"},
			{'id': 3, 'name': "Kili"},
			{'id': 6, 'name': "Nori"},
		]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :1 OR name = :2 OR altid = :1 OR altname = :2;
		"""
		dest_params = [[__row['id'], __row['name']] for __row in src_params]

		# Format SQL with params.
		sql, many_params = query.formatmany(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(many_params, dest_params)

	def test_4_named_dollar_escape_char(self):
		"""
		Test escaping a named dollar parameter.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_dollar', 'numeric', escape_char=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = $name AND tag IN ('$$Y2941', '$$2941');
		"""
		name = "Bilbo"
		src_params = {'name': name}

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

	def test_4_named_dollar_escape_char_disabled(self):
		"""
		Test disabling escaping of a named dollar parameter.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_dollar', 'numeric', escape_char=False)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = $name AND tag IN ('$$Y2941', '$2941');
		"""
		name = "Bilbo"
		src_params = {'name': name}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE name = :1 AND tag IN ('$$Y2941', '$2941');
		"""
		dest_params = [name]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_4_named_escape_char(self):
		"""
		Test escaping a named parameter.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'numeric', escape_char=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = :name AND tag IN ('::Y2941', '::2941');
		"""
		name = "Bilbo"
		src_params = {'name': name}

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

	def test_4_named_escape_char_disabled(self):
		"""
		Test disabling escaping of a named parameter.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'numeric', escape_char=False)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = :name AND tag IN ('::Y2941', ':2941');
		"""
		name = "Bilbo"
		src_params = {'name': name}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE name = :1 AND tag IN ('::Y2941', ':2941');
		"""
		dest_params = [name]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_4_pyformat_escape_char(self):
		"""
		Test escaping a pyformat parameter.
		"""
		# Create instance.
		query = sqlparams.SQLParams('pyformat', 'numeric', escape_char=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = %(name)s AND tag IN ('%%(Y2941)s', '%%(2941)s');
		"""
		name = "Bilbo"
		src_params = {'name': name}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE name = :1 AND tag IN ('%(Y2941)s', '%(2941)s');
		"""
		dest_params = [name]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_4_pyformat_escape_char_disabled(self):
		"""
		Test disabling escaping of a pyformat parameter.
		"""
		# Create instance.
		query = sqlparams.SQLParams('pyformat', 'numeric', escape_char=False)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE name = %(name)s AND tag IN ('%%(Y2941)s', '%(2941)s');
		"""
		name = "Bilbo"
		src_params = {'name': name}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE name = :1 AND tag IN ('%%(Y2941)s', '%(2941)s');
		"""
		dest_params = [name]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_named_to_numeric_unescaped_percent(self):
		"""
		Test converting from::

			SELECT 5 % :value

		to::

			SELECT 5 % :1
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'numeric')

		# Source SQL and params.
		src_sql = """
			SELECT 5 % :value;
		"""
		value = 2
		src_params = {'value': value}

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

	def test_5_named_to_numeric_dollar_unescaped_percent(self):
		"""
		Test converting from::

			SELECT 5 % :value

		to::

			SELECT 5 % $1
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'numeric_dollar')

		# Source SQL and params.
		src_sql = """
			SELECT 5 % :value;
		"""
		value = 2
		src_params = {'value': value}

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

	def test_5_named_dollar_to_numeric_unescaped_percent(self):
		"""
		Test converting from::

			SELECT 5 % $value

		to::

			SELECT 5 % :1
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_dollar', 'numeric')

		# Source SQL and params.
		src_sql = """
			SELECT 5 % $value;
		"""
		value = 2
		src_params = {'value': value}

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

	def test_5_named_dollar_to_numeric_dollar_unescaped_percent(self):
		"""
		Test converting from::

			SELECT 5 % $value

		to::

			SELECT 5 % $1
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_dollar', 'numeric_dollar')

		# Source SQL and params.
		src_sql = """
			SELECT 5 % $value;
		"""
		value = 2
		src_params = {'value': value}

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

	def test_5_pyformat_to_numeric_collapsed_percent(self):
		"""
		Test converting from::

			SELECT 5 %% %(value)s

		to::

			SELECT 5 % :1
		"""
		# Create instance.
		query = sqlparams.SQLParams('pyformat', 'numeric', escape_char=True)

		# Source SQL and params.
		src_sql = """
			SELECT 5 %% %(value)s;
		"""
		value = 2
		src_params = {'value': value}

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

	def test_5_pyformat_to_numeric_dollar_collapsed_percent(self):
		"""
		Test converting from::

			SELECT 5 %% %(value)s;

		to::

			SELECT 5 % $1
		"""
		# Create instance.
		query = sqlparams.SQLParams('pyformat', 'numeric_dollar', escape_char=True)

		# Source SQL and params.
		src_sql = """
			SELECT 5 %% %(value)s;
		"""
		value = 2
		src_params = {'value': value}

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
