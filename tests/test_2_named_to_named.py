"""
This module tests converting named parameters to named parameters.
"""

import copy
import unittest

import sqlparams


class Test(unittest.TestCase):
	"""
	The :class:`Test` class tests converting named parameters to named
	parameters.

	From: named, named_dollar, pyformat.
	To: named, named_dollar, pyformat.
	"""

	def test_1_named_to_named_dollar(self):
		"""
		Test converting from::

			... WHERE name = :name

		to::

			... WHERE name = $name
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'named_dollar')

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
			WHERE id = $id OR name = $name;
		"""
		dest_params = copy.deepcopy(src_params)

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_1_named_to_named_dollar_many(self):
		"""
		Test converting many from::

			... WHERE name = :name

		to::

			... WHERE name = $name
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'named_dollar')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :id OR name = :name;
		"""
		src_params = [
			{'id': 1, 'name': "Dwalin"},
			{'id': 9, 'name': "Gloin"},
		]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = $id OR name = $name;
		"""
		dest_params = copy.deepcopy(src_params)

		# Format SQL with params.
		sql, many_params = query.formatmany(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(many_params, dest_params)

	def test_1_named_dollar_to_pyformat(self):
		"""
		Test converting from::

			... WHERE name = :name

		to::

			... WHERE name = %(name)s
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_dollar', 'pyformat')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = $id OR name = $name;
		"""
		src_params = {'id': 2, 'name': "Balin"}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = %(id)s OR name = %(name)s;
		"""
		dest_params = copy.deepcopy(src_params)

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_1_named_dollar_to_pyformat_many(self):
		"""
		Test converting many from::

			... WHERE name = :name

		to::

			... WHERE name = %(name)s
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_dollar', 'pyformat')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = $id OR name = $name;
		"""
		src_params = [
			{'id': 6, 'name': "Nori"},
			{'id': 2, 'name': "Balin"},
			{'id': 10, 'name': "Bifur"},
		]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = %(id)s OR name = %(name)s;
		"""
		dest_params = copy.deepcopy(src_params)

		# Format SQL with params.
		sql, many_params = query.formatmany(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(many_params, dest_params)

	def test_1_pyformat_to_named(self):
		"""
		Test converting from::

			... WHERE name = %(name)s

		to::

			... WHERE name = :name
		"""
		# Create instance.
		query = sqlparams.SQLParams('pyformat', 'named')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = %(id)s OR name = %(name)s;
		"""
		src_params = {'id': 12, 'name': "Bombur"}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :id OR name = :name;
		"""
		dest_params = copy.deepcopy(src_params)

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_1_pyformat_to_named_many(self):
		"""
		Test converting from::

			... WHERE name = %(name)s

		to::

			... WHERE name = :name
		"""
		# Create instance.
		query = sqlparams.SQLParams('pyformat', 'named')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = %(id)s OR name = %(name)s;
		"""
		src_params = [
			{'id': 13, 'name': "Thorin"},
			{'id': 6, 'name': "Nori"},
			{'id': 12, 'name': "Bombur"},
			{'id': 11, 'name': "Bofur"},
		]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :id OR name = :name;
		"""
		dest_params = copy.deepcopy(src_params)

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
		query = sqlparams.SQLParams('named', 'named', expand_tuples=True)

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
			WHERE race = :race AND name IN (:names__0_sqlp,:names__1_sqlp);
		"""
		dest_params = {'race': src_params['race'], 'names__0_sqlp': src_params['names'][0], 'names__1_sqlp': src_params['names'][1]}

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
		query = sqlparams.SQLParams('named', 'named')

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
			WHERE race = :race AND name IN :names;
		"""
		dest_params = copy.deepcopy(src_params)

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
		query = sqlparams.SQLParams('named', 'named', expand_tuples=False)

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
			WHERE race = :race AND name IN :names;
		"""
		dest_params = copy.deepcopy(src_params)

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
		query = sqlparams.SQLParams('named', 'named', expand_tuples=True)

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
			WHERE race = :race AND name IN (NULL);
		"""
		dest_params = {'race': src_params['race']}

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
		query = sqlparams.SQLParams('named', 'named', expand_tuples=True)

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
			WHERE race = :race AND name IN (:names__0_sqlp,:names__1_sqlp);
		"""
		dest_params = [{'race': __row['race'], 'names__0_sqlp': __row['names'][0], 'names__1_sqlp': __row['names'][1]} for __row in src_params]

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
		query = sqlparams.SQLParams('named', 'named', expand_tuples=True)

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
		query = sqlparams.SQLParams('named', 'named', expand_tuples=True)

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
		query = sqlparams.SQLParams('named', 'named')

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
			WHERE id = :id OR name = :name OR altid = :id OR altname = :name;
		"""
		dest_params = copy.deepcopy(src_params)

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
		query = sqlparams.SQLParams('named', 'named')

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
			WHERE id = :id OR name = :name OR altid = :id OR altname = :name;
		"""
		dest_params = copy.deepcopy(src_params)

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
		query = sqlparams.SQLParams('named_dollar', 'named', escape_char=True)

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
			WHERE name = :name AND tag IN ('$Y2941', '$2941');
		"""
		dest_params = copy.deepcopy(src_params)

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
		query = sqlparams.SQLParams('named_dollar', 'named', escape_char=False)

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
			WHERE name = :name AND tag IN ('$$Y2941', '$2941');
		"""
		dest_params = copy.deepcopy(src_params)

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
		query = sqlparams.SQLParams('named', 'named', escape_char=True)

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
			WHERE name = :name AND tag IN (':Y2941', ':2941');
		"""
		dest_params = copy.deepcopy(src_params)

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
		query = sqlparams.SQLParams('named', 'named', escape_char=False)

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
			WHERE name = :name AND tag IN ('::Y2941', ':2941');
		"""
		dest_params = copy.deepcopy(src_params)

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
		query = sqlparams.SQLParams('pyformat', 'named', escape_char=True)

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
			WHERE name = :name AND tag IN ('%(Y2941)s', '%(2941)s');
		"""
		dest_params = copy.deepcopy(src_params)

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
		query = sqlparams.SQLParams('pyformat', 'named', escape_char=False)

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
			WHERE name = :name AND tag IN ('%%(Y2941)s', '%(2941)s');
		"""
		dest_params = copy.deepcopy(src_params)

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_named_to_named_dollar_unescaped_percent(self):
		"""
		Test converting from::

			SELECT 5 % :value

		to::

			SELECT 5 % $value
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'named_dollar')

		# Source SQL and params.
		src_sql = """
			SELECT 5 % :value;
		"""
		src_params = {'value': 2}

		# Desired SQL and params.
		dest_sql = """
			SELECT 5 % $value;
		"""
		dest_params = copy.deepcopy(src_params)

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_named_to_pyformat_escaped_percent(self):
		"""
		Test converting from::

			SELECT 5 % :value

		to::

			SELECT 5 %% %(value)s
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'pyformat')

		# Source SQL and params.
		src_sql = """
			SELECT 5 % :value;
		"""
		src_params = {'value': 2}

		# Desired SQL and params.
		dest_sql = """
			SELECT 5 %% %(value)s;
		"""
		dest_params = copy.deepcopy(src_params)

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_named_dollar_to_named_unescaped_percent(self):
		"""
		Test converting from::

			SELECT 5 % $value

		to::

			SELECT 5 % :value
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_dollar', 'named')

		# Source SQL and params.
		src_sql = """
			SELECT 5 % $value;
		"""
		src_params = {'value': 2}

		# Desired SQL and params.
		dest_sql = """
			SELECT 5 % :value;
		"""
		dest_params = copy.deepcopy(src_params)

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_named_dollar_to_pyformat_escaped_percent(self):
		"""
		Test converting from::

			SELECT 5 % $value

		to::

			SELECT 5 %% %(value)s
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_dollar', 'pyformat')

		# Source SQL and params.
		src_sql = """
			SELECT 5 % $value;
		"""
		src_params = {'value': 2}

		# Desired SQL and params.
		dest_sql = """
			SELECT 5 %% %(value)s;
		"""
		dest_params = copy.deepcopy(src_params)

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_pyformat_to_named_collapsed_percent(self):
		"""
		Test converting from::

			SELECT 5 %% %(value)s

		to::

			SELECT 5 % :value
		"""
		# Create instance.
		query = sqlparams.SQLParams('pyformat', 'named', escape_char=True)

		# Source SQL and params.
		src_sql = """
			SELECT 5 %% %(value)s;
		"""
		src_params = {'value': 2}

		# Desired SQL and params.
		dest_sql = """
			SELECT 5 % :value;
		"""
		dest_params = copy.deepcopy(src_params)

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_pyformat_to_named_dollar_collapsed_percent(self):
		"""
		Test converting from::

			SELECT 5 %% %(value)s

		to::

			SELECT 5 % $value
		"""
		# Create instance.
		query = sqlparams.SQLParams('pyformat', 'named_dollar', escape_char=True)

		# Source SQL and params.
		src_sql = """
			SELECT 5 %% %(value)s;
		"""
		src_params = {'value': 2}

		# Desired SQL and params.
		dest_sql = """
			SELECT 5 % $value;
		"""
		dest_params = copy.deepcopy(src_params)

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)
