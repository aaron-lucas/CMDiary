import datetime

HOMEWORK = 'homework'
ASSESSMENT = 'assessment'
NOTE = 'note'

UID = 'uid'
SUBJECT = 'subject'
DESCRIPTION = 'description'
DUE_DATE = 'due_date'
ITEM_TYPE = 'item_type'

class CheckedVar(object):
	def __init__(self, data_type, options=None, default=None):
		self._store_id = '__CheckedVar_{}'.format(id(self))
		self.data_type = data_type
		self.options = set() if options is None else set(filter(lambda x: isinstance(x, data_type), options))
		self.default = default if self.is_valid_value(default) else None

	def __set__(self, instance, value):
		if self.is_valid_value(value):
			setattr(instance, self._store_id, value)
		else:
			raise ValueError('New value must be of type {}.'.format(self.data_type))

	def __get__(self, instance, owner):
		return getattr(instance, self._store_id, self.default)

	def is_valid_value(self, value):
		if value is None:
			return True
		elif self.options:
			return value in self.options
		return isinstance(value, self.data_type)


class DiaryEntry(object):
	uid = CheckedVar(int)
	subject = CheckedVar(str)
	description = CheckedVar(str)
	due_date = CheckedVar(datetime.date)
	item_type = CheckedVar(str, [HOMEWORK, ASSESSMENT, NOTE])

	def __init__(self, owner, item_type, subject, description, due_date, uid=None):
		self.owner = owner
		self.item_type = item_type
		self.subject = subject
		self.description = description
		self.due_date = due_date
		self.uid = owner.allocate_uid() if uid is None else uid

	def edit(self, attr, value):
		if attr in (UID, SUBJECT, DESCRIPTION, DUE_DATE, ITEM_TYPE):
			setattr(self, attr, value)

	@property
	def data(self):
		return {UID: self.uid,
		        SUBJECT: self.subject,
		        DESCRIPTION: self.description,
		        DUE_DATE: self.due_date,
		        ITEM_TYPE: self.item_type}

	@property
	def days_left(self):
		if self.due_date is None:
			return None
		return (self.due_date - datetime.date.today()).days