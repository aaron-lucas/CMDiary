from collections import OrderedDict
from termcolor import cprint, colored


def cmd(string):
    return colored(string, 'magenta')


def arg(string):
    return colored(string, 'red')


def title(string):
    return colored(string, attrs=['bold'])


def important(string):
    return colored(string, 'yellow')


# A dict of commands and their respective help strings
COMMANDS = OrderedDict([('add',      cmd('(a)dd') + arg('       [type] [subject] [description] [due date]') +
                         ' - add new entry'),
                        ('remove',   cmd('(r)emove') + arg('    [uid]') + ' - remove an entry'),
                        ('edit',     cmd('(e)dit') + arg('      [uid] [attr] [value]') + ' - edit an entry\'s data'),
                        ('extend',   cmd('e(x)tend') + arg('    [uid] [days]') +
                         ' - change an entry\'s due date by (days) days'),
                        ('list',     cmd('(l)ist') + '      list all diary entries'),
                        ('priority', cmd('(p)riority') + arg('  [uid] [0:1]') +
                         ' - Gives or takes priority of an entry. An entry with\n' +
                         '            priority will appear in bold.'),
                        ('filter',   cmd('(f)ilter') + arg('    [condition]') +
                         ' - enter filter mode to select multiple entries at once'),
                        ('quit',     cmd('(q)uit') + '      quit CMDiary'),
                        ('help',     cmd('(h)elp') + arg("      [command : 'types' : 'attrs' : 'date']") +
                         ' - display command info'),
                        ('cancel',   'Use ' + cmd('\\') + ' to ' + arg('cancel') +
                         ' a prompt and return to the main screen')])

# A list of available item types
ITEM_TYPES = ['(h)omework', '(a)ssessment', '(n)ote']

# A list of available attributes
ATTRIBUTES = ['(s)ubject', '(d)escription', '(due)date', '(t)ype', '(p)riority']

# A string containing help for date formatting
DATE_FORMATTING = '* Dates can be represented by using 1 to 3 numbers, separated by a space ( ), dash (-), or slash' \
                  ' (/) but not a mixture of the three.\n' \
                  '* The numbers represent the day, month and year in that order. If any are omitted, the' \
                  ' corresponding value from today\'s date is assumed.\n' \
                  '* E.g. entering 12/3 as a date will form the 12th of March in the current year.\n' \
                  '* Similarly, entering just 4 will form the 4th of the current month and year.\n' \
                  '* If a year is specified, it must be in full, 4-digit format or it will not be recognised.'

FILTER_HELP = '* In filter mode, you can specify conditions to select multiple entries.\n' + \
              '* Conditions are entered in the form ' + arg('[attribute][operator][value]') + '.\n' + \
              '* Conditions can be entered at the prompt until a selection has been made.\n' + \
              '* The ' + cmd('remove') + ', ' + cmd('edit') + ', ' + cmd('extend') + ' and ' + cmd('priority') + \
              ' commands can then be used, without the need to specify uids.\n' + \
              important('Attributes') + ': (u)id, (s)ubject, (d)escription, (due)date, (days)left.\n' + \
              important('Operators') + ':\n    =    Equal to\n    >    Greater than\n    <    Less than\n' \
                                       '    :    Contains\n' + \
              important('Extra Commands:') + '\n ' + cmd('(q)uit') + '  Quit filter mode\n ' + \
              cmd('(l)ist') + '  List entries currently selected by filter\n ' + cmd('(c)lear') + ' Clear all filters'

# Create help strings using the above three lists/strings
item_types_help = important('Item Types: ') + '{}'.format(', '.join(ITEM_TYPES))
attributes_help = important('Attributes: ') + '{}'.format(', '.join(ATTRIBUTES))
date_formatting_help = important('Date formatting:\n') + DATE_FORMATTING


def get_info(item=None):
    """
    Lookup and print help strings.

    :param item:    A str to find a help section for.
    :return:        None
    """
    if item is None:  # Print all help
        print('\n' + title('CMDiary Help\n-----------------------'))
        print(item_types_help)
        print(attributes_help)
        print()
        for info in COMMANDS.values():
            print(info)
        print()
        print('There are additional help sections on the following topics:\n* ' +
              important('Date Formatting ') + '(' +
              cmd('help date') + ')\n* ' +
              important('Use of the filter function ') + '(' +
              cmd('help filter') + ')')
    elif item in ('t', 'types'):
        print(item_types_help)
    elif item in ('attrs', 'attributes', 'attr'):
        print(attributes_help)
    elif item in ('date', 'due', 'duedate', 'format', 'formatting', 'd'):
        print(date_formatting_help)
    elif item in COMMANDS.keys():  # Command-specific help
        print(COMMANDS[item])
    else:
        cprint("No help section for '{}'. Type 'help' for all CMDiary help info.".format(item), 'yellow')
    if item == 'filter':
        print('\n' + FILTER_HELP)
    print()
