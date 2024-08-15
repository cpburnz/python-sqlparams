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

	def test_1_named_oracle_1_to_pyformat_1_no_quotes(self):
		"""
		Test converting from::

			... WHERE name = :name

		to::

			... WHERE name = %(NAME)s
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_oracle', 'pyformat')

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
			WHERE id = %(ID)s OR name = %(NAME)s AND race = %(RACE)s;
		"""
		dest_params = {__key.upper(): __val for __key, __val in src_params.items()}

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_1_named_oracle_1_to_pyformat_2_quotes(self):
		"""
		Test converting from::

			... WHERE name = :"name"

		to::

			... WHERE name = %(name)s
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_oracle', 'pyformat')

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
			WHERE id = %(ID)s OR name = %(Name)s AND race = %(race)s;
		"""
		dest_params = {
			__key.strip('"'): __val for __key, __val in src_params.items()
		}

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_1_named_oracle_1_to_pyformat_3_mixed(self):
		"""
		Test converting from::

			... WHERE name = :"name"

		to::

			... WHERE name = %(name)s
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_oracle', 'pyformat')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :"ID" OR name = :"Name" AND race = :race;
		"""
		src_params = {'id': 4, '"Name"': "Fili", '"RACE"': "Dwarf"}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = %(ID)s OR name = %(Name)s AND race = %(RACE)s;
		"""
		dest_params = {
			(__key.strip('"') if '"' in __key else __key.upper()): __val
			for __key, __val in src_params.items()
		}

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_1_named_oracle_2_to_pyformat_1_many_no_quotes(self):
		"""
		Test converting many from::

			... WHERE name = :name

		to::

			... WHERE name = %(NAME)s
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_oracle', 'pyformat')

		# Source SQL and params.
		# - WARNING: Only the first row is scanned for the in-parameter names. All
		#   subsequent rows must have the exact same in-parameter names.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :ID OR name = :Name AND race = :race;
		"""
		src_params = [
			{'id': 6, 'NAME': "Nori", 'Race': "dwarf"},
			{'id': 2, 'NAME': "Balin", 'Race': "dwarf"},
			{'id': 10, 'NAME': "Bifur", 'Race': "dwarf"},
		]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = %(ID)s OR name = %(NAME)s AND race = %(RACE)s;
		"""
		dest_params = [
			{__key.upper(): __val for __key, __val in __row.items()}
			for __row in src_params
		]

		# Format SQL with params.
		sql, many_params = query.formatmany(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(many_params, dest_params)

	def test_1_named_oracle_2_to_pyformat_2_many_quotes(self):
		"""
		Test converting many from::

			... WHERE name = :"name"

		to::

			... WHERE name = %(NAME)s
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_oracle', 'pyformat')

		# Source SQL and params.
		# - WARNING: Only the first row is scanned for the in-parameter names. All
		#   subsequent rows must have the exact same in-parameter names.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :"ID" OR name = :"Name" AND race = :"race";
		"""
		src_params = [
			{'"ID"': 6, '"Name"': "Nori", '"race"': "dwarf"},
			{'"ID"': 2, '"Name"': "Balin", '"race"': "dwarf"},
			{'"ID"': 10, '"Name"': "Bifur", '"race"': "dwarf"},
		]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = %(ID)s OR name = %(Name)s AND race = %(race)s;
		"""
		dest_params = [
			{__key.strip('"'): __val for __key, __val in __row.items()}
			for __row in src_params
		]

		# Format SQL with params.
		sql, many_params = query.formatmany(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(many_params, dest_params)

	def test_1_named_oracle_2_to_pyformat_3_many_mixed(self):
		"""
		Test converting many from::

			... WHERE name = :"name"

		to::

			... WHERE name = %(NAME)s
		"""
		# Create instance.
		query = sqlparams.SQLParams('named_oracle', 'pyformat')

		# Source SQL and params.
		# - WARNING: Only the first row is scanned for the in-parameter names. All
		#   subsequent rows must have the exact same in-parameter names.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :"ID" OR name = :"Name" AND race = :race;
		"""
		src_params = [
			{'id': 6, '"Name"': "Nori", '"RACE"': "dwarf"},
			{'id': 2, '"Name"': "Balin", '"RACE"': "dwarf"},
			{'id': 10, '"Name"': "Bifur", '"RACE"': "dwarf"},
		]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = %(ID)s OR name = %(Name)s AND race = %(RACE)s;
		"""
		dest_params = [{
			(__key.strip('"') if '"' in __key else __key.upper()): __val
			for __key, __val in __row.items()
		} for __row in src_params]

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

	def test_1_pyformat_to_named_oracle_no_quote(self):
		"""
		Test converting from::

			... WHERE name = %(name)s

		to::

			... WHERE name = :name
		"""
		# Create instance.
		query = sqlparams.SQLParams('pyformat', 'named_oracle')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = %(id)s OR name = %(name)s;
		"""
		src_params = {'id': 4, 'name': "Fili"}

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

	def test_1_pyformat_to_named_oracle_quote(self):
		"""
		Test converting from::

			... WHERE name = %(name)s

		to::

			... WHERE name = :"name"
		"""
		# Create instance.
		query = sqlparams.SQLParams('pyformat', 'named_oracle', allow_out_quotes=True)

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = %(id)s OR name = %(name)s;
		"""
		src_params = {'id': 4, 'name': "Fili"}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = :"id" OR name = :"name";
		"""
		dest_params = {f'"{k}"': src_params[k] for k in src_params}

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

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
		dest_params = {
			'race': src_params['race'],
			'names__0_sqlp': src_params['names'][0],
			'names__1_sqlp': src_params['names'][1],
		}

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_2_expand_tuples_oracle(self):
		"""
		Test expanding tuples.
		"""
		# Create instance.
		query = sqlparams.SQLParams(
			in_style='named',
			out_style='named_oracle',
			expand_tuples=True,
			allow_out_quotes=True,
		)

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
			WHERE race = :"race" AND name IN (:"names__0_sqlp",:"names__1_sqlp");
		"""
		dest_params = {
			'"race"': src_params['race'],
			'"names__0_sqlp"': src_params['names'][0],
			'"names__1_sqlp"': src_params['names'][1],
		}

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_2_expand_tuples_default(self):
		"""
		Test the default behavior for expanding tuples. A named out-style should be
		disabled by default.
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
		dest_params = [{
			'race': __row['race'],
			'names__0_sqlp': __row['names'][0],
			'names__1_sqlp': __row['names'][1],
		} for __row in src_params]

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
