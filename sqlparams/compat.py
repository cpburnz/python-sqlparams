# encoding: utf-8
"""
This module provides compatibility between Python 2 and 3. Hardly
anything is used by this project to constitute including `six`_.

.. _`six`: http://pythonhosted.org/six
"""

import sys

if sys.version_info[0] < 3:
	# Python 2.
	unicode = unicode

	def iteritems(mapping):
		return mapping.iteritems()

else:
	# Python 3.
	unicode = str

	def iteritems(mapping):
		return mapping.items()
