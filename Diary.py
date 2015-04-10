import pickle
from DiaryEntry import DiaryEntry
import os.path
from random import randint
import datetime

def update_data(func):
		def wrapper(self, *args, **kwargs):
			retval = func(self, *args, **kwargs)
			with open('data.pickle', 'wb') as file:
				for entry in self.entries:
					file.write(pickle.dumps(entry.data, pickle.HIGHEST_PROTOCOL))
			return retval
		return wrapper

class Diary(object):
	def __init__(self):
		self.entries = self.load_data()

	def load_data(self):
		entry_data = []
		if not os.path.isfile('data.pickle'):
			open('data.pickle', 'w').close() # Create file if none exists
		with open('data.pickle', 'rb') as source:
			try:
				while True:
					entry_data.append(pickle.load(source))
			except EOFError: # Stop looping through data at end of file
				pass

		return [DiaryEntry(self, **dataset) for dataset in entry_data] # Create DiaryEntrys from stored data

	@property
	def taken_uids(self):
		return [entry.uid for entry in self.entries]

	@update_data
	def add(self, item_type, subject, description, due_date):
		self.entries.append(DiaryEntry(self, item_type, subject, description, due_date))

	@update_data
	def remove(self, *uids):
		for entry in self.entries:
			if entry.uid in uids:
				self.entries.remove(entry)

	@update_data
	def edit(self, attr, value, *uids):
		for entry in self.entries:
			if entry.uid in uids:
				entry.edit(attr, value)

	@update_data
	def extend(self, days, *uids):
		for entry in self.entries:
			if entry.uid in uids:
				if entry.due_date is None:
					continue
				entry.due_date += datetime.timedelta(days=days)

	def allocate_uid(self):
		while True:
			uid = randint(100, 999)
			if uid not in self.taken_uids:
				return uid

	def filter(self, expression):
		raise NotImplementedError