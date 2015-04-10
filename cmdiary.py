from DiaryEntry import ASSESSMENT, HOMEWORK, NOTE, UID, ITEM_TYPE, SUBJECT, DESCRIPTION, DUE_DATE
from Diary import Diary
from termcolor import cprint, colored
import re
import datetime
from collections import OrderedDict
from ParameterInfo import ParameterInfo

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

			message = err_msg.format(inp) if '{}' in err_msg else err_msg
			cprint(message, 'yellow')

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

	print("Raw: ", required_data)
	format_existing_data(required_data)
	print('After format: ', required_data)
	complete_data(required_data)
	print('After processing: ', required_data)

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

		label = key.capitalize().replace('_', ' ') + ': '
		param_info = PARAMETERS[key]

		data[key] = get_input(prompt=label,
		                      response_type=param_info.data_type,
		                      condition=param_info.condition,
		                      modifier=param_info.modifier,
		                      err_msg=param_info.err_msg)


def format_existing_data(data):
	for key, value in data.items():
		if not value:
			continue
		param_info = PARAMETERS[key]
		if param_info.condition is None or param_info.condition(value):
			data[key] = param_info.modifier(value) if param_info.modifier is not None else value
		else:
			data[key] = False # Mark data as invalid by resetting value


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

diary = Diary()

# Define command parameters and required information.
# Variables with the i_ prefix are ParameterInfo types.
i_uid =         ParameterInfo(UID,
                              int,
                              condition=lambda uid: uid in diary.taken_uids,
                              err_msg='Object with UID {} does not exist')

i_item_type =   ParameterInfo(ITEM_TYPE,
                              condition=lambda x: x in ITEM_TYPES.keys(),
                              modifier=lambda x: ITEM_TYPES.get(x, HOMEWORK),
                              err_msg='Item type {} does not exist')

i_subject =     ParameterInfo(SUBJECT)

i_description = ParameterInfo(DESCRIPTION)

i_due_date =    ParameterInfo(DUE_DATE,
                              condition=validate_date,
                              modifier=str_to_date,
                              err_msg='Invalid date. Date format is dd/mm/yyyy. See help page for more info.')

PARAMETERS = {UID: i_uid,
              ITEM_TYPE: i_item_type,
              SUBJECT: i_subject,
              DESCRIPTION: i_description,
              DUE_DATE: i_due_date}

# Testing code for debug purposes
add('homework maths worksheet q1-2 5')
add('h')
print([entry.data for entry in diary.entries])