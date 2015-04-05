from DiaryEntry import ASSESSMENT, HOMEWORK, NOTE, UID, ITEM_TYPE, SUBJECT, DESCRIPTION, DUE_DATE
from Diary import Diary
from termcolor import cprint, colored
import re

diary = Diary()

def get_input(prompt, response_type=str, condition=None, modifier=None):
	while True:
		inp = input(prompt)
		try:
			if inp:
				inp = response_type(inp)
		except:
			cprint('Input must be of type {}'.format(response_type.__name__), 'yellow')
		else:
			if condition is None or condition(inp):
				return inp if modifier is None else modifier(inp)
			cprint('Input must pass specified condition', 'yellow')

def format_input(input_string):
	pass

def add(input_data):
	re_command = re.compile('^([a-zA-Z]*?) ')
	re_item_type = re.compile('([ahn]|assessment|homework|note)')
	re_subject = re.compile(r' (.*?)[\;]')
	re_description = re.compile('r[\;](.*?)[\;]')
	re_due_date = re.compile(r'[\;](([0-9]{1,2}){1,2}([0-9]{4})?)$')


def remove(input_data):
	pass

def edit(input_data):
	pass

def extend(input_data):
	pass

def list():
	pass

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