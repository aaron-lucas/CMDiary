from collections import OrderedDict
from termcolor import colored

COMMANDS = OrderedDict([('add',     '(a)dd     <type> - add new entry'),
                        ('remove',  '(r)emove  <uid> - remove an entry'),
                        ('edit',    '(e)dit    <uid> [attr] - edit an entry\'s data'),
                        ('extend',  'e(x)tend  <uid> <days> - change an entry\'s due date by (days) days'),
                        ('list',    '(l)ist    display all diary entries'),
                        ('quit',    '(q)uit    quit CMDiary'),
                        ('help',    "(h)elp    [command : 'types' : 'attrs'] - display command info  ")])

ITEM_TYPES = ['(h)omework', '(a)ssessment', '(n)ote']

ATTRIBUTES = ['(s)ubject', '(d)escription', '(due)date', '(t)ype']

def help(cmd=None):
	if cmd is None:
		print('\nCMDiary Help\n-----------------------')
		print('Item Types: {}'.format(', '.join(ITEM_TYPES)))
		print('Attributes: {}'.format(', '.join(ATTRIBUTES)))
		print()
		for info in COMMANDS.values():
			print(info)
	elif cmd == 'types':
		print('Item Types: {}'.format(', '.join(ITEM_TYPES)))
	elif cmd == 'attrs':
		print('Attributes: {}'.format(', '.join(ATTRIBUTES)))
	else:
		print(' '.join(COMMANDS.get(cmd, colored('No help section for {}'.format(cmd), 'yellow')).split()))
