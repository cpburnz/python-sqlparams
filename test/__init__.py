# coding: utf-8
"""
This package tests the general implementation of sqlparams.
"""
from __future__ import unicode_literals

import os.path
import site
import sys
import unittest

import sqlparams

if sys.version_info[0] >= 3:
	unichr = chr


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

	def test_03_encode_bytes(self):
		"""
		Test encoding bytes.
		"""
		encoded = "".join(map(unichr, range(0,256))).encode(sqlparams._BYTES_ENCODING)
		expected = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff"
		self.assertEquals(encoded, expected)

	def test_03_decode_bytes(self):
		"""
		Test decoding bytes.
		"""
		decoded = bytes(bytearray(range(0,256))).decode(sqlparams._BYTES_ENCODING)
		expected = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff"
		self.assertEquals(decoded, expected)

	def test_04_format_bytes(self):
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

	def test_04_formatmany_bytes(self):
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
