from collections import OrderedDict
from termcolor import cprint

COMMANDS = OrderedDict([('add',     '(a)dd     [type] [subject] [description] [due date] - add new entry'),
                        ('remove',  '(r)emove  [uid] - remove an entry'),
                        ('edit',    '(e)dit    [uid] [attr] [value] - edit an entry\'s data'),
                        ('extend',  'e(x)tend  [uid] [days] - change an entry\'s due date by (days) days'),
                        ('list',    '(l)ist    list all diary entries'),
                        ('quit',    '(q)uit    quit CMDiary'),
                        ('help',    "(h)elp    [command : 'types' : 'attrs' : 'date'] - display command info  ")])
ITEM_TYPES = ['(h)omework', '(a)ssessment', '(n)ote']
item_types_help = 'Item Types: {}'.format(', '.join(ITEM_TYPES))
ATTRIBUTES = ['(s)ubject', '(d)escription', '(due)date', '(t)ype']
attributes_help = 'Attributes: {}'.format(', '.join(ATTRIBUTES))
DATE_FORMATTING = '* Dates can be represented by using 1 to 3 numbers, separated by a space ( ), dash (-), or slash' \
                  ' (/) but not a mixture of the three.\n' \
                  '* The numbers represent the day, month and year in that order. If any are omitted, the' \
                  ' corresponding value from todays date is assumed.\n' \
                  '* E.g. entering 12/3 as a date will form the 12th of March in the current year.\n' \
                  '* Similarly, entering just 4 will form the 4th of the current month and year.\n' \
                  '* If a year is specified, it must be in full, 4-digit format or it will not be recognised.'
date_formatting_help = 'Date formatting:\n{}'.format(DATE_FORMATTING)

def get_info(item=None):
    if item is None:
        print('\nCMDiary Help\n-----------------------')
        print(item_types_help)
        print(attributes_help)
        print()
        for info in COMMANDS.values():
            print(info)
        print()
        print(date_formatting_help)
    elif item in ('t', 'types'):
        print(item_types_help)
    elif item in ('attrs', 'attributes', 'attr'):
        print(attributes_help)
    elif item in ('date', 'due', 'duedate', 'format', 'formatting', 'd'):
        print(date_formatting_help)
    elif item in COMMANDS.keys():
        print(COMMANDS[item])
    else:
        cprint("No help section for '{}'. Type 'help' for all CMDiary help info.".format(item), 'yellow')
    print()

