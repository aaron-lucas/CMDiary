# CMDiary - a command-line diary application

VERSION = 'v2.0'
AUTHOR = 'Aaron Lucas'
GITHUB_REPO = 'https://github.com/aaron-lucas/CMDiary'


from DiaryEntry import ASSESSMENT, HOMEWORK, NOTE, UID, ITEM_TYPE, SUBJECT, DESCRIPTION, DUE_DATE
from Diary import Diary
from termcolor import cprint, colored
import re
import datetime
from collections import OrderedDict
from ParameterInfo import ParameterInfo

ATTRIBUTE = 'attribute'
VALUE = 'value' # Changes depending on chosen attribute - used in edit()
DAYS = 'days' # days parameter name/reference

def requires_parameters(*params):
	def decorator(func):
		def wrapper(input_data):
			required_data = OrderedDict([(key, False) for key in params])
			return func(input_data, required_data)
		return wrapper
	return decorator

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

@requires_parameters(ITEM_TYPE, SUBJECT, DESCRIPTION, DUE_DATE)
def add(input_data, required_data):
	try:
		required_data[ITEM_TYPE] = input_data.split()[0]
		required_data[SUBJECT] = input_data.split()[1]
	except IndexError:
		pass

	unparsed_data = ' '.join(input_data.split()[2:])

	match = re.search(RE_DUE_DATE, unparsed_data)

	required_data[DUE_DATE] = match.group(1) if match is not None else False
	required_data[DESCRIPTION] = match.string[:match.start()] if match is not None else unparsed_data

	format_existing_data(required_data)
	complete_data(required_data)

	diary.add(**required_data)

@requires_parameters(UID)
def remove(input_data, required_data):
	try:
		required_data[UID] = input_data.split()[0]
	except IndexError:
		pass

	format_existing_data(required_data)
	complete_data(required_data)

	diary.remove(required_data[UID])

@requires_parameters(UID, ATTRIBUTE, VALUE)
def edit(input_data, required_data):
	try:
		required_data[UID] = input_data.split()[0]
		required_data[ATTRIBUTE] = input_data.split()[1]
		required_data[VALUE] = ' '.join(input_data.split()[2:])
	except IndexError:
		pass

	format_existing_data(required_data)
	complete_data(required_data)

	diary.edit(required_data[ATTRIBUTE], required_data[VALUE], required_data[UID])

@requires_parameters(UID, DAYS)
def extend(input_data, required_data):
	try:
		required_data[UID] = input_data.split()[0]
		required_data[DAYS] = input_data.split()[1]
	except IndexError:
		pass

	format_existing_data(required_data)
	complete_data(required_data)

	diary.extend(required_data[DAYS], required_data[UID])

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
		_test_date = str_to_date(string)
	except ValueError:
		return False
	return True


def complete_data(data):
	for key, value in data.items():
		if value:
			continue # Data is already present
		if data.get(ATTRIBUTE, False):
			i_value = PARAMETERS[ATTRIBUTES[data[ATTRIBUTE]]]
		label = key.capitalize().replace('_', ' ') + ': '

		param_info = PARAMETERS[key] if key != VALUE else i_value

		data[key] = get_input(prompt=label,
		                      response_type=param_info.data_type,
		                      condition=param_info.condition,
		                      modifier=param_info.modifier,
		                      err_msg=param_info.err_msg)

def format_existing_data(data):
	for key, value in data.items():
		if not value:
			continue
		if data.get(ATTRIBUTE, False):
			i_value = PARAMETERS[ATTRIBUTES[data[ATTRIBUTE]]]
		param_info = PARAMETERS[key] if key != VALUE else i_value
		try:
			value = param_info.data_type(value)
		except ValueError:
			pass
		else:
			if param_info.condition is None or param_info.condition(value):
				data[key] = param_info.modifier(value) if param_info.modifier is not None else value
				continue
		data[key] = False # Mark data as invalid by resetting value

def prompt():
	inp = input('CMDiary {}> '.format(VERSION))
	split_input = inp.split(maxsplit=1)
	command = split_input[0]
	command = COMMANDS.get(command, None)
	args = split_input[1] if len(split_input) == 2 else ''
	return command, args

diary = Diary()

# Define command parameters and required information.
# Variables with the i_ prefix are ParameterInfo types.
i_uid =         ParameterInfo(UID,
                              int,
                              condition=lambda uid: int(uid) in diary.taken_uids,
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
i_attr =        ParameterInfo(ATTRIBUTE,
                              condition=lambda attr: attr in ATTRIBUTES,
                              modifier=lambda attr: ATTRIBUTES[attr],
                              err_msg="Attribute '{}' does not exist")
i_days =        ParameterInfo(DAYS,
                              int)

# Define regex for matching sections of input
RE_DUE_DATE = re.compile(r' (([0-9]{1,2} ?){1,2}([0-9]{4})?)$')

# Define dicts of possible inputs and abbreviations

PARAMETERS = {UID: i_uid,
              ITEM_TYPE: i_item_type,
              SUBJECT: i_subject,
              DESCRIPTION: i_description,
              DUE_DATE: i_due_date,
              ATTRIBUTE: i_attr,
              DAYS: i_days}

ATTRIBUTES = ({'u': UID, UID: UID,
               'i': ITEM_TYPE, ITEM_TYPE: ITEM_TYPE,
               's': SUBJECT, SUBJECT: SUBJECT,
               'd': DESCRIPTION, DESCRIPTION: DESCRIPTION,
               'due': DUE_DATE, DUE_DATE: DUE_DATE})

ITEM_TYPES = {
	'a': ASSESSMENT, 'assessment': ASSESSMENT,
	'h': HOMEWORK, 'homework': HOMEWORK,
	'n': NOTE, 'note': NOTE
}

COMMANDS = {'add': add, 'a': add,
            'remove': remove, 'r': remove,
            'edit': edit, 'e': edit,
            'extend': extend, 'x': extend,
            'quit': quit, 'q': quit,
            'list': list_items, 'l': list_items()}



# Run the diary
if __name__ == '__main__':
	while True:
		command, args = prompt()
		if command is None:
			cprint('{} is not a valid command'.format(command), 'yellow')
			continue
		command(args)