from diary_objects import Diary, HOMEWORK, ASSESSMENT, NOTE, SUBJECT, DESCRIPTION, DUE_DATE, UID, ITEM_TYPE
from termcolor import cprint
import help
import datetime
from input_errors import *

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

def add_item(item_type):
	subject = get_input('Subject: ')
	description = get_input('Description: ')
	due_date = format_date(get_input('Due Date: ', modifier=lambda x: x if x else None))
	diary.add(item_type, subject, description, due_date)

def edit_item(uid, attr=None):
	def format_value(val):
		try:
			if attr == 'uid':
				if is_valid_uid(int(val)):
					return int(val)
				cprint('UID {} already exists'.format(val), 'yellow')
				return None
			elif attr == 'type':
				return TYPES[val]
			elif attr == 'due_date':
				return format_date(val)
			elif attr is None:
				return None
			return str(val)
		except (KeyError, ValueError) as e:
			print(e)
			return None
	attr = get_input('Attribute: ', modifier=lambda x:ATTRS.get(x, None)) if attr is None else ATTRS.get(attr, None)
	value = get_input('New value: ', modifier=format_value)
	if attr is not None and value is not None:
		print(uid, attr, repr(value))
		diary.edit(uid, attr, value)
	else:
		cprint('Invalid input', 'yellow')

def is_valid_uid(uid):
	return not uid in diary.taken_uids

def format_date(date_str):
	print(repr(date_str))
	if not date_str:
		return ''
	args = date_str.split()
	today = datetime.date.today()
	d = int(args[0]) if len(args) >= 1 else today.day
	m = int(args[1]) if len(args) >= 2 else today.month
	y = int(args[2]) if len(args) >= 3 else today.year
	return datetime.date(y, m, d)

def format_args(cmd, args):
	try:
		expected_args = help.required_args.get(cmd, 0)
	except KeyError:
		pass

	try:
		if cmd == 'add':
			args[0] = TYPES[args[0]]
		elif cmd == 'help' and args:
			args[0] = COMMAND_ABBREVS.get(args[0], args[0])
	except (KeyError, IndexError):
		raise InvalidArgumentError

	try:
		if cmd in ('remove', 'edit', 'extend'):
			args[0] = int(args[0])
			if args[0] not in diary.taken_uids:
				raise NonexistentUIDError
	except (IndexError, ValueError):
		raise InvalidArgumentError
	return args[:expected_args]

def prompt():
	print()
	inp = input('CMDiary v2.0> ').split()
	if not inp:
		return (None, None)
	cmd, args = inp[0], inp[1:]
	cmd = COMMAND_ABBREVS.get(cmd, cmd)
	return cmd, args

diary = Diary()
COMMANDS = {"add": add_item,
            "remove": diary.remove,
            "edit": edit_item,
			"quit": quit,
			"list": diary.display,
			'extend': diary.extend,
			'help': help.help}

TYPES = {'homework': HOMEWORK, 'h': HOMEWORK,
         'assessment': ASSESSMENT, 'a': ASSESSMENT,
         'note': NOTE, 'n': NOTE}

ATTRS = {'uid': UID, 'u': UID,
         'subject': SUBJECT, 's': SUBJECT,
         'description': DESCRIPTION, 'd': DESCRIPTION,
         'due': DUE_DATE, 'duedate': DUE_DATE,
         'type': ITEM_TYPE, 't': ITEM_TYPE}

COMMAND_ABBREVS = {'a': 'add',
                   'r': 'remove',
                   'e': 'edit',
                   'q': 'quit',
                   'l': 'list',
                   'x': 'extend',
                   'h': 'help'}

diary.display()
while True:
	cmd, args = prompt()
	if cmd is None:
		continue
	try:
		args = format_args(cmd, args)
	except InvalidArgumentError:
		cprint('Invalid arguments', 'yellow')
		print('Usage: ', end='')
		help.help(cmd)
	except NonexistentUIDError:
		cprint('Item with UID {} does not exist'.format(args[0]), 'yellow')
	else:
		COMMANDS.get(cmd, lambda *args: cprint("'{}' is not a valid command".format(cmd), 'yellow'))(*args)
