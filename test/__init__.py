# coding: utf-8
"""
This package tests the general implementation of sqlparams.
"""
from __future__ import unicode_literals

import os.path
import site
import unittest

import sqlparams


class SQLParamsTest(unittest.TestCase):
	"""
	The ``SQLParamsTest`` class tests the general implementation of the
	``SQLParams`` class.
	"""

	def test_00_named_to_qmark(self):
		"""
		Tests converting from::

		  ... WHERE name = :name

		to::

		  ... WHERE name = ?
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'qmark')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :id OR name = :name;
		"""
		src_params = {'id': 1, 'name': "Dwalin"}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = ? OR name = ?;
		"""
		dest_params = [1, "Dwalin"]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEquals(sql, dest_sql)
		self.assertEquals(params, dest_params)

	def test_00_numeric_to_qmark(self):
		"""
		Tests converting from::

		  ... WHERE name = :1

		to::

		  ... WHERE name = ?
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric', 'qmark')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :2 OR name = :1;
		"""
		seq_params = ["Balin", 2]
		int_params = {1: "Balin", 2: 2}
		str_params = {'1': "Balin", '2': 2}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = ? OR name = ?;
		"""
		dest_params = [2, "Balin"]

		for src_params in [seq_params, int_params, str_params]:
			# Format SQL with params.
			sql, params = query.format(src_sql, src_params)

			# Make sure desired SQL and parameters are created.
			self.assertEquals(sql, dest_sql)
			self.assertEquals(params, dest_params)

	def test_00_pyformat_to_qmark(self):
		"""
		Tests converting from::

		  ... WHERE name = %(name)s

		to::

		  ... WHERE name = ?
		"""
		# Create instance.
		query = sqlparams.SQLParams('pyformat', 'qmark')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = %(id)s OR name = %(name)s;
		"""
		src_params = {'id': 3, 'name': 'Kili'}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = ? OR name = ?;
		"""
		dest_params = [3, 'Kili']

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEquals(sql, dest_sql)
		self.assertEquals(params, dest_params)

	def test_00_named_to_format(self):
		"""
		Tests converting from::

		  ... WHERE name = :name

		to::

		  ... WHERE name = %s
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'format')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :id OR name = :name;
		"""
		src_params = {'id': 4, 'name': 'Fili'}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = %s OR name = %s;
		"""
		dest_params = [4, 'Fili']

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEquals(sql, dest_sql)
		self.assertEquals(params, dest_params)

	def test_01_tuple(self):
		"""
		Tests converting with tuples from::

		  ... WHERE name IN :names

		to::

		  ... WHERE name IN (?, ...)
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'qmark')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id IN :ids OR name IN :names;
		"""
		src_params = {'ids': (5, 6, 7), 'names': ("Dori", "Nori", "Ori")}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id IN (?,?,?) OR name IN (?,?,?);
		"""
		dest_params = [5, 6, 7, "Dori", "Nori", "Ori"]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEquals(sql, dest_sql)
		self.assertEquals(params, dest_params)

	def test_02_many(self):
		"""
		Tests converting many from::

		  ... WHERE name = :name

		to::

		  ... WHERE name = ?
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'qmark')

		# Source SQL and params.
		src_sql = """
			UPDATE users
			SET name = :name
			WHERE id = :id;
		"""
		src_params = [
			{'id': 10, 'name': "Bifur"},
			{'id': 11, 'name': "Bofur"},
			{'id': 12, 'name': "Bombur"},
		]

		# Desired SQL and params.
		dest_sql = """
			UPDATE users
			SET name = ?
			WHERE id = ?;
		"""
		dest_params = [
			["Bifur", 10],
			["Bofur", 11],
			["Bombur", 12],
		]

		# Format SQL with params.
		sql, many_params = query.formatmany(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEquals(sql, dest_sql)
		self.assertEquals(many_params, dest_params)

	def test_02_many_tuple(self):
		"""
		Tests converting many with tuples from::

		  ... WHERE name IN :names

		to::

		  ... WHERE name IN (?, ...)
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'qmark')

		ids = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)
		names = ("Dwalin", "Balin", "Kili", "Fili", "Dori", "Nori", "Ori", "Oin", "Gloin", "Bifur", "Bofur", "Bomber", "Thorin")

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE age = :age AND (id IN :ids OR name IN :names);
		"""
		src_params = [
			{'age': 'old', 'ids': ids, 'names': names},
			{'age': 'young', 'ids': ids, 'names': names},
			{'age': 'unknown', 'ids': ids, 'names': names},
		]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE age = ? AND (id IN (?,?,?,?,?,?,?,?,?,?,?,?,?) OR name IN (?,?,?,?,?,?,?,?,?,?,?,?,?));
		"""
		dest_params = [
			['old'] + list(ids) + list(names),
			['young'] + list(ids) + list(names),
			['unknown'] + list(ids) + list(names),
		]

		# Format SQL with params.
		sql, many_params = query.formatmany(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEquals(sql, dest_sql)
		self.assertEquals(many_params, dest_params)

	def test_03_format_bytes(self):
		"""
		Test byte strings when formatting a query.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'qmark')

		# Source SQL and params.
		src_sql = b"""
			SELECT *
			FROM users
			WHERE id = :id;
		"""
		src_params = {'id': 1}

		# Desired SQL and params.
		dest_sql = b"""
			SELECT *
			FROM users
			WHERE id = ?;
		"""
		dest_params = [1]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEquals(sql, dest_sql)
		self.assertEquals(params, dest_params)

	def test_03_formatmany_bytes(self):
		"""
		Test byte strings when formatting many for a query.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'qmark')

		# Source SQL and params.
		src_sql = b"""
			SELECT *
			FROM users
			WHERE id = :id;
		"""
		src_params = [{'id': 10}, {'id': 11}, {'id': 12}]

		# Desired SQL and params.
		dest_sql = b"""
			SELECT *
			FROM users
			WHERE id = ?;
		"""
		dest_params = [[10], [11], [12]]

		# Format SQL with params.
		sql, many_params = query.formatmany(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEquals(sql, dest_sql)
		self.assertEquals(many_params, dest_params)
