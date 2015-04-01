from synced_data import SyncedDataType, SyncedDataset, SyncedVar, SyncedDate, Date
from random import randint
from tabulate import tabulate
from termcolor import colored, cprint
import os, sys, datetime
# define constants
HOMEWORK = 'HOMEWORK'
ASSESSMENT = 'ASSESSMENT'
NOTE = 'NOTE'

SUBJECT = 'subject'
DESCRIPTION = 'description'
DUE_DATE = 'due_date'
UID = 'uid'
ITEM_TYPE = 'item_type'

COLOR_MAP = {ASSESSMENT: 'red', HOMEWORK: 'blue', NOTE: 'green'}

def refresh(func):
	def wrapper(self, *args, **kwargs):
		retval = func(self, *args, **kwargs)
		self.display()
		return retval
	return wrapper

class Diary(object):
	def __init__(self):
		self.objects = SyncedDataset(database='data.db', data_type=DiaryObject, id_key='uid', extra={'owner': self})

	@refresh
	def add(self, item_type, subject, description, due_date=None):
		self.objects.add(DiaryObject(self, item_type, subject, description, due_date))

	@refresh
	def remove(self, uid):
		self.objects.remove(uid)

	@refresh
	def edit(self, uid, attribute, value):
		self.objects.edit(uid, attribute, value)

	@refresh
	def extend(self, uid, days):
		obj = self.object_with_uid(uid)
		new_date = obj.due_date.date + datetime.timedelta(days=int(days))
		self.objects.edit(uid, 'due_date', new_date)

	def object_with_uid(self, uid):
		return self.objects[uid]

	def display(self):
		if not len(self.objects):
			cprint('Diary contains no entries', 'yellow')
			return
		attrs = ['uid', 'item_type', 'subject', 'description', 'due_date', 'days_left']
		labels = ['UID', 'Type', 'Subject', 'Description', 'Due Date', 'Days Left']
		objects = self.objects.values()
		objects = sorted(objects, key=lambda o: (o.due_date.date_str, o.subject))
		data = []
		for obj in objects:
			obj_data = []
			text_attrs = self.select_attributes(obj)
			for attr in attrs:
				item = getattr(obj, attr)
				if isinstance(item, Date):
					item = item.date_str
				item = colored(str(item), color=COLOR_MAP[obj.item_type], attrs=text_attrs)
				obj_data.append(item)
			data.append(obj_data)
		table = tabulate(data, headers=labels)
		sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=24, cols=max((len(table.split('\n')[1])), 80)))
		os.system('clear')
		print(table)

	@staticmethod
	def select_attributes(obj):
		attrs = []
		if obj.days_left != 'N/A':
			if obj.days_left == 1:
				attrs.append('underline')
			elif obj.days_left == 0:
				attrs.append('reverse')
			elif obj.days_left < 0:
				attrs.append('dark')

		return attrs

	@property
	def taken_uids(self):
		return list(self.objects.keys())


class DiaryObject(object, metaclass=SyncedDataType):
	uid = SyncedVar(data_type=int)
	item_type = SyncedVar(options=[HOMEWORK, ASSESSMENT, NOTE], data_type=str)
	subject = SyncedVar(data_type=str)
	description = SyncedVar(data_type=str)
	due_date = SyncedDate()

	def __init__(self, owner, item_type, subject, description, due_date=None, uid=None):
		self.owner = owner
		self.item_type = item_type
		self.subject = subject
		self.description = description
		self.due_date = due_date
		self.uid = self.allocate_uid() if uid is None else uid

		for attr in self.synced_attrs:
				self.synced_data[attr] = getattr(self, attr)

	def edit(self, attribute, value):
		if attribute in (SUBJECT, DESCRIPTION, DUE_DATE, UID, ITEM_TYPE):
			setattr(self, attribute, value)

	def allocate_uid(self):
		while True:
			uid = randint(100, 999)
			if uid not in self.owner.taken_uids:
				return uid

	@property
	def days_left(self):
		if self.due_date.date in (None, 'N/A'):
			return 'N/A'
		return (self.due_date.date - datetime.date.today()).days
