from DiaryEntry import ASSESSMENT, HOMEWORK, NOTE, UID, ITEM_TYPE, SUBJECT, DESCRIPTION, DUE_DATE
from Diary import Diary
from termcolor import cprint, colored
import re
import datetime
from collections import OrderedDict

diary = Diary()

def get_input(prompt, response_type=str, condition=None, modifier=None, err_msg='Invalid Argument'):
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

			if '{}' in err_msg:
				err_msg = err_msg.format(inp)
			cprint(err_msg, 'yellow')

def format_input(input_string):
	pass

def add(input_data):
	required_data = OrderedDict([(ITEM_TYPE, False),
	                             (SUBJECT, False),
	                             (DESCRIPTION, False),
	                             (DUE_DATE, False)])
	try:
		required_data[ITEM_TYPE] = list(input_data.split())[0]
		required_data[SUBJECT] = list(input_data.split())[1]
	except IndexError:
		pass

	unparsed_data = ' '.join(input_data.split()[2:])
	re_due_date = re.compile(r' (([0-9]{1,2} ?){1,2}([0-9]{4})?)$')
	match = re.search(re_due_date, unparsed_data)

	required_data[DUE_DATE] = match.group(1) if match is not None else False
	required_data[DESCRIPTION] = match.string[:match.start()] if match is not None else False

	complete_data(required_data)
	format_data(required_data)
	diary.add(**required_data)

def remove(input_data):
	pass

def edit(input_data):
	pass

def extend(input_data):
	pass

def list_items():
	pass

def determine_date_separator(string):
	if not string:
		return None

	for separator in (' ', '/', '-'):
		if separator in string:
			return separator

def str_to_date(string):
	separator = determine_date_separator(string)
	if not string:
		return None
	components = string.split(separator) if separator is not None else [string]
	today = datetime.date.today()

	day = int(components[0]) if len(components) >= 1 else today.day
	month = int(components[1]) if len(components) >= 2 else today.month
	year = int(components[2]) if len(components) >= 3 else today.year

	return datetime.date(year, month, day)

def date_to_str():
	pass

def validate_date(string):
	try:
		test_date = str_to_date(string)
	except ValueError:
		return False

	return True


def complete_data(data):
	for key, value in data.items():
		if value:
			continue

		if key == UID:
			data[key] = get_input('UID: ',
			                      int,
			                      condition=lambda uid: uid in diary.taken_uids,
			                      err_msg='Object with UID {} does not exist')
		elif key == ITEM_TYPE:
			data[key] = get_input('Item type: ',
			                      condition=lambda x: x in ITEM_TYPES.keys(),
			                      modifier=lambda x: ITEM_TYPES.get(x, HOMEWORK))
		elif key in (SUBJECT, DESCRIPTION):
			data[key] = get_input(key.capitalize()+': ')
		elif key == DUE_DATE:
			data[key] = get_input('Due date: ',
			                      condition=validate_date,
			                      modifier=str_to_date)

def format_data(data):
	for key, value in data.items():
		if key in (SUBJECT, DESCRIPTION):
			if value in (False, None):
				data[key] = None
			else:
				data[key] = str(value)
		elif key == ITEM_TYPE:
			data[key] = ITEM_TYPES.get(value, None)
		elif key == DUE_DATE:
			data[key] = str_to_date(value)

"""ABBREVIATIONS = {'a': (add, ASSESSMENT),
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
                'x': extend}"""

ITEM_TYPES = {
	'a': ASSESSMENT, 'assessment': ASSESSMENT,
	'h': HOMEWORK, 'homework': HOMEWORK,
	'n': NOTE, 'note': NOTE
}

add('homework maths worksheet q1-2 5')
add('')