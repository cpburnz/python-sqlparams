"""
This package tests the general implementation of sqlparams.
"""

import unittest

import sqlparams


class Test(unittest.TestCase):
	"""
	The :class:`Test` class tests the general implementation of
	the :class:`~sqlparams.SQLParams` class.
	"""

	def test_1_decode_bytes(self):
		"""
		Test decoding bytes.
		"""
		decoded = bytes(bytearray(range(0, 256))).decode(sqlparams._BYTES_ENCODING)
		expected = (
			"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12"
			"\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f"
			" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcde"
			"fghijklmnopqrstuvwxyz{|}~"
			"\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90"
			"\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2"
			"\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4"
			"\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6"
			"\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8"
			"\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea"
			"\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc"
			"\xfd\xfe\xff"
		)
		self.assertEqual(decoded, expected)

	def test_1_encode_bytes(self):
		"""
		Test encoding bytes.
		"""
		encoded = "".join(map(chr, range(0,256))).encode(sqlparams._BYTES_ENCODING)
		expected = (
			b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12"
			b"\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f"
			b" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcd"
			b"efghijklmnopqrstuvwxyz{|}~"
			b"\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f"
			b"\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0"
			b"\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1"
			b"\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2"
			b"\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3"
			b"\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4"
			b"\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5"
			b"\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff"
		)
		self.assertEqual(encoded, expected)

	def test_2_format_bytes(self):
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
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_2_format_bytes_many(self):
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
		self.assertEqual(sql, dest_sql)
		self.assertEqual(many_params, dest_params)

	def test_3_qmark_end(self):
		"""
		Test that a query can end with a qmark.
		"""
		# Create instance.
		query = sqlparams.SQLParams('qmark', 'qmark')

		# Source SQL and params.
		src_sql = "SELECT ?"
		name = "Bilbo"
		src_params = [name]

		# Desired SQL and params.
		dest_sql = "SELECT ?"
		dest_params = [name]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_4_postgresql_named(self):
		"""
		Test converting from::

			... WHERE id = :id::int

		to::

			... WHERE id = ?::int
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'qmark')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :id::integer;
		"""
		id = '2941'
		src_params = {'id': id}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = ?::integer;
		"""
		dest_params = [id]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_4_postgresql_numeric(self):
		"""
		Test converting from::

			... WHERE id = :1::int

		to::

			... WHERE id = ?::int
		"""
		# Create instance.
		query = sqlparams.SQLParams('numeric', 'qmark')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE id = :1::integer;
		"""
		id = '2941'
		src_params = [id]

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE id = ?::integer;
		"""
		dest_params = [id]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_4_postgresql_timestamp(self):
		"""
		Test a PostgreSQL query containing an inline timestamp.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'qmark')

		# Source SQL and params.
		src_sql = """
			SELECT *
			FROM users
			WHERE time = '12:00:00'
		"""
		src_params = {}

		# Desired SQL and params.
		dest_sql = """
			SELECT *
			FROM users
			WHERE time = '12:00:00'
		"""
		dest_params = []

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_strip_comments_mixed(self) -> None:
		"""
		Test a potentially strange scenario with mixed comments.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'qmark', strip_comments=True)

		# Source SQL and params.
		src_sql = """
			/*
			-- Parameters:
			--   :start_date
			--   :end_date */
			SELECT * FROM users WHERE updated_at BETWEEN :start_date AND :end_date
		"""
		src_params = {'start_date': "2021-10-21", 'end_date': "2022-08-10"}

		# Desired SQL and params.
		dest_sql = """
			SELECT * FROM users WHERE updated_at BETWEEN ? AND ?
		"""
		dest_params = [src_params['start_date'], src_params['end_date']]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_strip_comments_multi(self) -> None:
		"""
		Test a query stripping multiline comments.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'qmark', strip_comments=True)

		# Source SQL and params.
		src_sql = """
			/*
			Parameters:
			  :start_date
			  :end_date
			*/
			SELECT * FROM users WHERE updated_at BETWEEN :start_date AND :end_date
		"""
		src_params = {'start_date': "2021-10-21", 'end_date': "2022-08-10"}

		# Desired SQL and params.
		dest_sql = """
			SELECT * FROM users WHERE updated_at BETWEEN ? AND ?
		"""
		dest_params = [src_params['start_date'], src_params['end_date']]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_strip_comments_multi_greedy(self) -> None:
		"""
		Test to make sure multiline comments are not greedy.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'qmark', strip_comments=True)

		# Source SQL and params.
		src_sql = """
			/*
			Parameters:
			  :start_date
			  :end_date
			*/
			*/
			SELECT * FROM users WHERE updated_at BETWEEN :start_date AND :end_date
		"""
		src_params = {'start_date': "2021-10-21", 'end_date': "2022-08-10"}

		# Desired SQL and params.
		dest_sql = """
			*/
			SELECT * FROM users WHERE updated_at BETWEEN ? AND ?
		"""
		dest_params = [src_params['start_date'], src_params['end_date']]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_strip_comments_multi_last(self) -> None:
		"""
		Test to make sure a multiline comment at the end of the string is
		handled properly.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'qmark', strip_comments=True)

		# Source SQL and params.
		src_sql = """
			SELECT * FROM users
			/* Last line. */
		""".rstrip()
		src_params = {}

		# Desired SQL and params.
		dest_sql = """
			SELECT * FROM users
		""".rstrip() + "\n"
		dest_params = []

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_strip_comments_multi_trailing(self) -> None:
		"""
		Test to make sure multiline comments do not consume trailing comments.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'qmark', strip_comments=True)

		# Source SQL and params.
		src_sql = """
			SELECT * FROM users /* Trailing comment. */
		"""
		src_params = {}

		# Desired SQL and params.
		dest_sql = """
			SELECT * FROM users /* Trailing comment. */
		"""
		dest_params = []

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_strip_comments_single(self) -> None:
		"""
		Test a query stripping single line comments.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'qmark', strip_comments=True)

		# Source SQL and params.
		src_sql = """
			-- Parameters:
			--   :start_date
			--   :end_date
			SELECT * FROM users WHERE updated_at BETWEEN :start_date AND :end_date
		"""
		src_params = {'start_date': "2021-10-21", 'end_date': "2022-08-10"}

		# Desired SQL and params.
		dest_sql = """
			SELECT * FROM users WHERE updated_at BETWEEN ? AND ?
		"""
		dest_params = [src_params['start_date'], src_params['end_date']]

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_strip_comments_single_last(self) -> None:
		"""
		Test to make sure single line comment at the end of the string is handled
		properly.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'qmark', strip_comments=True)

		# Source SQL and params.
		src_sql = """
			SELECT * FROM users
			-- Last line.
		""".rstrip()
		src_params = {}

		# Desired SQL and params.
		dest_sql = """
			SELECT * FROM users
		""".rstrip() + "\n"
		dest_params = []

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)

	def test_5_strip_comments_single_trailing(self) -> None:
		"""
		Test to make sure single line comments do not consume trailing comments.
		"""
		# Create instance.
		query = sqlparams.SQLParams('named', 'qmark', strip_comments=True)

		# Source SQL and params.
		src_sql = """
			SELECT * FROM users -- Trailing comment.
		"""
		src_params = {}

		# Desired SQL and params.
		dest_sql = """
			SELECT * FROM users -- Trailing comment.
		"""
		dest_params = []

		# Format SQL with params.
		sql, params = query.format(src_sql, src_params)

		# Make sure desired SQL and parameters are created.
		self.assertEqual(sql, dest_sql)
		self.assertEqual(params, dest_params)
