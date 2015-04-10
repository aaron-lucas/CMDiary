from DiaryEntry import ASSESSMENT, HOMEWORK, NOTE, UID, ITEM_TYPE, SUBJECT, DESCRIPTION, DUE_DATE
from Diary import Diary
from termcolor import cprint, colored
import re
import datetime
from collections import OrderedDict

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
	required_data = OrderedDict([(ITEM_TYPE, False),
	                             (SUBJECT, False),
	                             (DESCRIPTION, False),
	                             (DUE_DATE, False)])

	required_data[ITEM_TYPE] = list(input_data.split())[:1]
	required_data[SUBJECT] = list(input_data.split())[1:2]

	unparsed_data = ' '.join(input_data.split()[2:])
	re_due_date = re.compile(r' (([0-9]{1,2} ?){1,2}([0-9]{4})?)$')
	match = re.search(re_due_date, unparsed_data)

	required_data[DUE_DATE] = match.group(1) if match is not None else False
	required_data[DESCRIPTION] = match.string[:match.start()] if match is not None else False

	complete_data(required_data)
	print(required_data)
	format_data(required_data)
	#diary.add(item_type, subject, description, due_date)

def remove(input_data):
	pass

def edit(input_data):
	pass

def extend(input_data):
	pass

def list_items():
	pass

def str_to_date(string, separator='/'):
	if not string:
		return None
	components = string.split(separator)
	today = datetime.date.today()

	day = int(components[0]) if len(components) >= 1 else today.day
	month = int(components[1]) if len(components) >= 2 else today.month
	year = int(components[2]) if len(components) >= 3 else today.year

	return datetime.date(year, month, day)

def date_to_str():
	pass

def complete_data(data):
	for key, value in data.items():
		if value:
			continue
		label = key.replace('_', ' ') + ': '
		data[key] = input(label)
def format_data(data):
	for key, value in data.items:
		if key in (SUBJECT, DESCRIPTION):
			if value in (False, None):
				value = None
			else:
				value = str(value)
		elif key == ITEM_TYPE:
			value = ITEM_TYPES.get(value, None)
		elif key == DUE_DATE:
			value = str_to_date(value, separator=' ')

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

ITEM_TYPES = {
	'a': ASSESSMENT, 'assessment': ASSESSMENT,
	'h': HOMEWORK, 'homework': HOMEWORK,
	'n': NOTE, 'note': NOTE
}

add('homework maths worksheet q1-2 5')
add('')