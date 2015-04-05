from DiaryEntry import ASSESSMENT, HOMEWORK, NOTE, UID, ITEM_TYPE, SUBJECT, DESCRIPTION, DUE_DATE
from Diary import Diary
ABBREVIATIONS = {'a': (add, ASSESSMENT),
                'd': DESCRIPTION,
                'due': DUE_DATE,
                'e': edit,
                'f': filter,
                'h': (help, HOMEWORK),
                'l': list,
                'n': NOTE,
                'q': quit,
                'r': remove,
                's': SUBJECT,
                't': ITEM_TYPE,
                'u': UID,
                'x': extend}

diary = Diary()

def get_input():
	pass

def format_input(input_string):
	pass

def add(item_type, subject, description, due_date):
	pass

def remove(*uids):
	pass

def edit(attr, value, *uids):
	pass

def extend(days, *uids):
	diary.extend(days, *uids)

def list():
	pass