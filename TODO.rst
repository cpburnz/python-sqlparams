
Silence manifest exclude warnings::

	hey, here is some output from running pip install sqlparams. i'm not sure if these warnings are expected on your end, but thought i'd make you aware if they're not:

	$ sudo pip install sqlparams
	Downloading/unpacking sqlparams
		Running setup.py egg_info for package sqlparams

		  no previously-included directories found matching 'doc/build'
		  warning: no previously-included files matching '*~' found anywhere in distribution
		  warning: no previously-included files matching '*.pyc' found anywhere in distribution
	Installing collected packages: sqlparams
		Running setup.py install for sqlparams

		  no previously-included directories found matching 'doc/build'
		  warning: no previously-included files matching '*~' found anywhere in distribution
		  warning: no previously-included files matching '*.pyc' found anywhere in distribution
	Successfully install
