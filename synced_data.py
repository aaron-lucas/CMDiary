import sqlite3
import datetime
import os


class Date(object):
	"""A custom date that can be set via a datetime.date object or a
	date-formatted string in the format `date_format`.

	Date will also provide the date and string versions of the date,
	regardless of what was assigned to the `date` variable.

	Parameters:
	date_format     The format in which dates will be shown as
	date            The initial value that the object holds
	"""
	def __init__(self, date=None, date_format='%d/%m/%Y'):
		self.date_format = date_format
		if date in ('N/A', ''):
			self._date = None
		elif isinstance(date, str):
			self._date = datetime.datetime.strptime(date, date_format).date()
		else:
			self._date = date

	@property
	def date(self):
		return 'N/A' if self._date is None else self._date

	@date.setter
	def date(self, value):
		if value in (None, 'N/A'):
			print('none')
			self._date = None
		elif isinstance(value, str):
			print('datestr')
			self._date = datetime.datetime.strptime(self.date, self.date_format)
		elif isinstance(value, datetime.date):
			print('date')
			self._date = value

	@property
	def date_str(self):
		if self._date is None:
			return 'N/A'
		return datetime.date.strftime(self._date, self.date_format)


class SyncedDataset(dict):
	"""A custom dictionary that automatically syncs selected attributes
	to a database

	Each SyncedDataset can only hold one type of object in order to ensure
	that everything syncs properly. Only attributes that use the
	descriptors SyncedVar or SyncedDate are synced to the database.

	Parameters:
	database        A string that contains the file path for a database
					existing or not.
	data_type       The class of the objects that will be stored in the
					dictionary. Metaclass of the data type must be
					SyncedDataType.
	id_key          The name of the attribute used to provide a unique
					id for each object so that it can be referenced
	extra		    A dict containing extra (unsynced) data for object
					creation
	*args, **kwargs Initialisation parameters for the dictionary.
	"""
	def __init__(self, database, data_type, id_key, extra=None, *args, **kwargs):
		# Initialise dictionary and its properties
		super().__init__(*args, **kwargs)

		# Load database filepath and check whether it exists
		self.database = database
		db_exists = os.path.isfile(database)  # check before a database is created

		# Initialise attributes
		self.data_type = data_type
		self.conn = sqlite3.connect(database)  # creates a new database if none exists
		self.cursor = self.conn.cursor()
		self.id_key = id_key
		self.extra = {} if not extra else extra

		# Initialise a new database if none exists else load data from
		# existing database
		if db_exists:
			self._load_data()
		else:
			self._init_db()

	def __delitem__(self, key):
		"""Removes an item from the dictionary

		Can be called by SyncedDataset.remove() or del

		:param key: id_key value of item to remove
		:return: None
		"""
		# Remove item from dictionary
		super().__delitem__(key)

		# Remove data from database and commit
		self.cursor.execute('delete from objects where {}=?;'.format(self.id_key), (key,))
		self.conn.commit()

	def _load_data(self):
		"""Loads data from the database into the dictionary

		:return: None
		"""

		# Load the names of the synced attributes and fetch each
		# object's data from the database
		keys = self.data_type.synced_attrs
		values = self.cursor.execute('SELECT {} FROM objects'.format
						(', '.join(self.data_type.synced_attrs))).fetchall()
		# Create a dictionary containing the data for each object,
		# use it to create a new object, and add it to the class'
		# dict
		for obj_data in values:
			data = self.extra  # Add extra data needed to create object
			for key, value in zip(keys, obj_data):  # Pair keys and values
				data[key] = value if value != 'N/A' else None
			obj = self.data_type(**data)  # Unpack data to create new object

			# Retrieve the value held in the attribute given by id_key
			# for the object and add the object to the dict using the
			# value as the key
			self[getattr(obj, self.id_key)] = obj

	def _init_db(self):
		"""Creates the database table and its columns

		:return: None
		"""
		type_map = {int: 'integer', str: 'text', Date: 'text'}
		template = '{} {}'  # used to create SQL columns
		columns = []

		# Form the code to for each column in the format
		# 'var_name data_type' using `template`
		for attr in self.data_type.synced_attrs:
			var_type = self.data_type.__dict__[attr].data_type
			columns.append(template.format(attr, type_map[var_type]))

		# Form SQL code that generates an appropriate table and execute
		self.cursor.execute('create table objects ({});'.format
							(', '.join(columns)))

	def add(self, obj):
		""" Adds an object to the dictionary

		:param obj: The object to add. Must be of type self.data_type.
		:return: None
		"""

		# Ensure that `obj` is of correct type
		if not isinstance(obj, self.data_type):
			raise TypeError('Object must be of type {}.'.format
								(self.data_type))

		# Add object to dictionary using id_key value
		key = getattr(obj, self.id_key)
		self[key] = obj

		# Get all synced attributes and their values
		columns = self.data_type.synced_attrs
		values = [getattr(self[key], attr) for attr in columns]

		# Format the columns and attributes for the SQL command
		columns = ', '.join(map(str, columns))
		values = ', '.join(map(self._format_value, values))

		# Form the SQL command, execute, and commit
		self.cursor.execute('insert into objects ({}) values ({});'.format
							(columns, values))
		self.conn.commit()

	def remove(self, key):
		"""Removes an object from the dictionary

		Provides a function interface for deletion
		:param key: id_key value of item to delete
		:return: None
		"""
		del self[key]

	def edit(self, key, attr, value):
		"""Edits a value of an object in the dictionary

		:param key: id_key value of item to edit
		:param attr: the attribute name to edit (str)
		:param value: new value
		:return: None
		"""

		# Retrieve the object
		obj = self[key]

		# Ensure that the attribute is synced to the database
		if attr in obj.synced_attrs:
			# If the attribute to edit is the id_key, ensure that no
			# other object has that value as their id_key
			if key == self.id_key:
				if value in self.keys():
					raise ValueError('This id key already exists')
				else:
					self[value] = self.pop(key)

			# Update the value in the object itself
			setattr(obj, attr, value)

			# If the new value is a date, get its string representation
			if isinstance(value, datetime.date):
				value = obj.due_date.date_str

			# Update the value in the database
			template = '{}={}'  # Used to form SQL update code
			update = template.format(attr, self._format_value(value))

			# Form SQL command, execute, commit
			self.cursor.execute('update objects set {} where {}={};'.format(update, self.id_key, key))
			self.conn.commit()
		else:
			raise AttributeError('This attribute is not synced or does not exist')

	@staticmethod
	def _format_value(value):
		"""Formats values for use in SQL commands

		:param value: value to be formatted
		:return: str containing formatted value
		"""
		if isinstance(value, Date):
			value = value.date_str

		if value is None:
			return "'N/A'"  # String formatting removes surrounding quotes

		if isinstance(value, str):
			return "'{}'".format(value)  # String formatting removes surrounding quotes
		elif isinstance(value, int):
			return str(value)  # String formatting removes surrounding quotes


class SyncedDataType(type):
	"""A metaclass that is used to mark a data type that can be used
	by SyncedDataset.

	The SyncedDataType metaclass adds to the class and/or class
	instances certain attributes that must be present when using
	SyncedDataset such as the list of synced attributes and their values.
	"""
	def __new__(mcs, *args, **kwargs):
		def fget(self):
			vals = {attr: getattr(self, attr) for attr in self.synced_attrs}
			for key, val in vals.items():
				if isinstance(val, Date):
					vals[key] = val.date_str
			return vals

		new = super().__new__(mcs, *args, **kwargs)

		# Create a class variable that holds the names of all
		# variables that conform to the SyncedVar or SyncedDate
		# descriptor
		new.synced_attrs = [attr for attr in new.__dict__ if
							isinstance(new.__dict__[attr], (SyncedVar, SyncedDate))]

		# Add a property to the class that returns a dict containing
		# the synced attributes and their values
		new.synced_data = property(fget)  # Property simulates instance variable

		return new


class SyncedVar(object):
	"""A descriptor that provides the necessary functionality for
	synced attributes.

	SyncedVars are statically typed in order to operate with sqlite,
	whose columns require a static type.

	Parameters:
	data_type      The data type of the object the descriptor holds.
	options        A list of values that the descriptor is limited to.
	default        The initial value that the descriptor holds.
	"""
	def __init__(self, data_type, options=None, default=None):
		self._store_id = '__SyncedVar_{}'.format(id(self))
		self.data_type = data_type
		self.options = (set() if options is None else
						set(filter(lambda x: isinstance(x, data_type), options)))
		self.default = default if self.is_legal_value(default) else None

	def __get__(self, instance, owner):
		return getattr(instance, self._store_id, self.default)

	def __set__(self, instance, value):
		if self.is_legal_value(value):
			setattr(instance, self._store_id, value)
		else:
			raise TypeError('New value must be of type {}'.format(self.data_type))

	def is_legal_value(self, value):
		"""Checks if the descriptor can hold a value.

		:param value: any object
		:return: True/False depending on certain criteria
		"""
		if self.options:
			return any([value in self.options, value is None])
		return any([isinstance(value, self.data_type), value is None])


class SyncedDate(object):
	"""A descriptor that provides the necessary functionality for
	synced dates.

	A SyncedDate can be assigned a datetime.date object or string that
	conforms to the format provided, and will return a Date object
	which contains both the string and datetime.date representation.

	Parameters:
	str_format      A date formatting string which decides how a date is displayed
	default         The initial value that the descriptor holds.
	"""
	def __init__(self, str_format='%d/%m/%Y', default=None):
		self._store_id = '__SyncedDate_{}'.format(id(self))
		self.str_format = str_format
		self.default = Date(date_format=str_format) if default is None else Date(default, str_format)
		self.data_type = Date

	def __get__(self, instance, owner):
		return getattr(instance, self._store_id)

	def __set__(self, instance, value):
		value = Date(value, self.str_format)
		setattr(instance, self._store_id, value)

pass
