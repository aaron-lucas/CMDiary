# CMDiary - a command-line diary application

VERSION = 'v2.3'
AUTHOR = 'Aaron Lucas'
GITHUB_REPO = 'https://github.com/aaron-lucas/CMDiary'

import datetime
import re
import os
import sys
from collections import OrderedDict

from termcolor import cprint, colored
from tabulate import tabulate

if os.name == 'nt':  # Colorama only required on Windows machines
    from colorama import init, deinit

from DiaryEntry import ASSESSMENT, HOMEWORK, NOTE, UID, ITEM_TYPE, SUBJECT, DESCRIPTION, DUE_DATE, PRIORITY
from Diary import Diary
from ParameterInfo import ParameterInfo
from info import get_info
from Filter import Filter, FilterException

# Define custom parameter names
ATTRIBUTE = 'attribute'
VALUE = 'value'  # Changes depending on chosen attribute - used in edit()
DAYS = 'days'  # days parameter name/reference

COLOUR_MAP = {ASSESSMENT: 'red',
              HOMEWORK: 'blue',
              NOTE: 'green'}

NO_DATE = 'N/A'  # String used as placeholder if no date is specified
CANCEL_CHARACTER = '\\'
PROMPT = 'CMDiary {}'.format(VERSION)


def requires_parameters(*params):
    """
    A decorator that specifies what data must be entered for the function to run correctly.

    Creates an empty dict of required data which is passed to the function which must have a signature of
    func(input_data, required_data), where this dict is passed to the required_data parameter.

    :param params: An automatically packed list of data names for which values are required from the user.
                   Must have an entry in the PARAMETERS dict using these names for which the value is a
                   ParameterInfo object.
    :return:       A function with an empty dict of data which the function is required to fill.
    """

    def decorator(func):
        def wrapper(input_data):
            required_data = OrderedDict([(key, False) for key in params])  # OrderedDict to keep order of data prompts
            return func(input_data, required_data)

        return wrapper

    return decorator


def get_input(prompt, response_type=str, condition=None, modifier=None, err_msg='Invalid Argument'):
    """
    Prompt the user for input.

    :param prompt:          The text displayed to the user.
    :param response_type:   The data type expected as a response. The str value is converted to this data type.
    :param condition:       A function which evaluates the input and returns True/False depending on if the input
                            passes the condition.
    :param modifier:        A function that changes the input after testing the condition. Returns the modified value.
    :param err_msg:         An error message or template that can be formatted with the input if the function fails.
    :return:                A value of any type based on modifier and response_type.
    """
    while True:
        inp = input(prompt)
        try:
            if inp == CANCEL_CHARACTER:
                return CANCEL_CHARACTER
            if inp or inp == '':  # Empty string signifies no value
                inp = response_type(inp)
        except ValueError:
            print_error_message(err_msg, inp)
        else:
            if condition is None or condition(inp):  # Bypass condition check if condition is None
                return inp if modifier is None else modifier(inp)  # Bypass value modification if modifier is None
            print_error_message(err_msg, inp)


def print_error_message(msg_template, inp):
    """
    Print a (possibly) formatted error message to the user.

    :param msg_template:    A str template with a maximum of 1 format regions.
    :param inp:             The value the user entered.
    :return:
    """
    message = msg_template.format(inp)  # If no format regions ('{}') the message is unaltered
    cprint(message, 'yellow')


@requires_parameters(ITEM_TYPE, SUBJECT, DESCRIPTION, DUE_DATE)
def add(input_data, required_data):
    """
    Take and evaluate input to add a diary entry.

    Signature is add(input_data) after decoration.

    :param input_data:      The raw str data entered after the 'add' command.
    :param required_data:   A dict provided by the requires_parameters decorator. Doesn't need to be specified when
                            called due to the decorator.
    :return:                None.
    """
    try:
        required_data[ITEM_TYPE] = input_data.split()[0]  # item_type is always first word
        required_data[SUBJECT] = input_data.split()[1]  # subject is always second word
    except IndexError:
        pass  # Ignore error if data not specified as it will be entered later

    unparsed_data = ' '.join(input_data.split()[2:])  # Strip first two words from input_data

    match = re.search(RE_DUE_DATE, unparsed_data)

    required_data[DUE_DATE] = match.group(1) if match is not None else False  # Check for due date with regex
    # Remaining data is description
    required_data[DESCRIPTION] = match.string[:match.start()] if match is not None else unparsed_data

    format_existing_data(required_data)
    cancel = complete_data(required_data) == CANCEL_CHARACTER
    if cancel:
        return
    diary.add(**required_data)  # Parameter names in required_data match with diary.add function


@requires_parameters(UID)
def remove(input_data, required_data):
    """
    Take and evaluate input to remove an entry from the diary.

    Signature is remove(input_data) after decoration.

    :param input_data:      The raw str data entered after the 'remove' command.
    :param required_data:   A dict provided by the requires_parameters decorator. Doesn't need to be specified when
                            called due to the decorator.
    :return:                None.
    """
    try:
        required_data[UID] = input_data.split()[0]  # UID is always first word
    except IndexError:
        pass  # Ignore error if data not specified as it will be entered later

    format_existing_data(required_data)
    cancel = complete_data(required_data) == CANCEL_CHARACTER
    if cancel:
        return
    diary.remove(required_data[UID])


@requires_parameters(UID, ATTRIBUTE, VALUE)
def edit(input_data, required_data):
    """
    Take and evaluate input to edit an entry in the diary.

    Signature is edit(input_data) after decoration.

    :param input_data:      The raw str data entered after the 'edit' command.
    :param required_data:   A dict provided by the requires_parameters decorator. Doesn't need to be specified when
                            called due to the decorator.
    :return:                None.
    """
    try:
        required_data[UID] = input_data.split()[0]  # UID is always first word
        required_data[ATTRIBUTE] = input_data.split()[1]  # atribute is always second word
        required_data[VALUE] = ' '.join(input_data.split()[2:])  # Rest of the string is new value
    except IndexError:
        pass  # Ignore error if data not specified as it will be entered later

    format_existing_data(required_data)
    if any([not bool(val) for val in required_data.values()]):  # Check if any data needs to be entered
        cancel = complete_data(required_data) == CANCEL_CHARACTER
        if cancel:
            return
    diary.edit(required_data[ATTRIBUTE], required_data[VALUE], required_data[UID])


@requires_parameters(UID, DAYS)
def extend(input_data, required_data):
    """
    Take and evaluate input to extend the due date of an entry.

    Signature is remove(input_data) after decoration.

    :param input_data:      The raw str data entered after the 'remove' command.
    :param required_data:   A dict provided by the requires_parameters decorator. Doesn't need to be specified when
                            called due to the decorator.
    :return:                None.
    """
    try:
        required_data[UID] = input_data.split()[0]  # UID is always first word
        required_data[DAYS] = input_data.split()[1]  # days is always second word
    except IndexError:
        pass  # Ignore error if data not specified as it will be entered later

    format_existing_data(required_data)
    cancel = complete_data(required_data) == CANCEL_CHARACTER
    if cancel:
        return
    diary.extend(required_data[DAYS], required_data[UID])


@requires_parameters(UID, PRIORITY)
def priority(input_data, required_data):
    """
    Take and evaluate input to change the priority of an entry.

    Signature is priority(input_data) after decoration.

    :param input_data:      The raw str data entered after the 'remove' command.
    :param required_data:   A dict provided by the requires_parameters decorator. Doesn't need to be specified when
                            called due to the decorator.
    :return:                None.
    """
    try:
        required_data[UID] = input_data.split()[0]
        required_data[PRIORITY] = input_data.split()[1]
    except IndexError:
        pass  # Ignore error if data not specified as it will be entered later

    format_existing_data(required_data)
    cancel = complete_data(required_data) == CANCEL_CHARACTER
    if cancel:
        return
    diary.priority(required_data[PRIORITY], required_data[UID])


def filter_entries(filter_str=''):
    """
    Enter and handle filter mode.

    Prompts for filter conditions to filter the list of entries and commands to handle entries in bulk.

    :param filter_str:      An optional initial filter condition string.
    :return:                None.
    """
    if not filter_str:  # No initial filter condition given
        filter_str = None
    f = Filter(diary.entries, filter_str)
    display_filters(f)
    while True:
        cmd = get_input('{} (filter mode)> '.format(PROMPT),
                        condition=lambda x: x != '',  # Do not accept blank string
                        err_msg='')  # No error message if blank string is entered
        if f.is_valid_condition(cmd):
            try:
                f.refine(cmd)
                display_filters(f)
            except FilterException as fe:
                cprint(fe.args[0], 'yellow')
            continue

        elif cmd in ['reset', 'r']:
            f.reset()
            display_filters(f)
            continue

        elif cmd in ['l', 'list']:
            display_filters(f)
            continue

        elif cmd not in ['quit', 'q']:  # Otherwise a diary command has been entered
            cmd, f_args = process_input(cmd)  # Separate command and arguments
            if cmd not in [remove, edit, priority, extend]:  # These are the only commands available in filter mode
                continue

            for obj in f.objects:
                new_args = '{} {}'.format(obj.uid, f_args)  # Insert UID of each entry one at a time
                cmd(new_args)
        break  # User wants to exit filter mode or command has been run successfully


def display_filters(filter_obj):
    """
    Prints all active filters in filter mode.

    :param filter_obj:      A Filter object which holds the active filters.
    :return:                None.
    """
    display(filter_obj.objects,
            extra='Filters:\n' + colored('{}'.format(filter_obj.filter_string if filter_obj.filters else 'No Filters'),
                                         'yellow'))


def display(items='', extra=None):
    """
    Display all diary entries and info as a table on the screen.

    :param items:           List which sets items to be displayed. Defaults to all entries.
    :param extra:           Extra text to be displayed after the table.
    :return:                None.
    """
    filter_mode = type(items) is list  # Items is a list when run in filter mode
    os.system('cls' if os.name == 'nt' else 'clear')  # For Windows/Mac/Linux compatibility
    if not filter_mode and not len(diary.entries):  # Displaying all diary entries and diary is empty
        cprint('Diary has no entries.\n', 'yellow')
        return
    items = items if filter_mode else diary.entries

    if not len(items):  # Using filter function
        cprint('No entries match these criteria\n', 'yellow')
        print(extra + '\n')
        return

    headers = ('UID', 'Type', 'Subject', 'Description', 'Due Date', 'Days Left')
    rows = []
    entries = sorted(items, key=entry_sort_info)

    for new_uid, entry in enumerate(entries):
        if not filter_mode:
            entry.uid = new_uid + 1  # Leave UIDs unchanged in filter mode
        due_date = entry.due_date if entry.due_date is not None else NO_DATE
        days_left = entry.days_left if entry.days_left is not None else NO_DATE
        rows.append(['{:0>3}'.format(entry.uid),
                     entry.item_type,
                     entry.subject,
                     entry.description,
                     date_to_str(due_date),
                     days_left,
                     entry.priority])  # Format some data to str

    rows = [[colored(str(attr), COLOUR_MAP[row[1]],
                     attrs=get_text_attributes(row)) for attr in row[:-1]]  # Do not display priority status
            for row in rows]  # Colour-code rows based on item type

    table = tabulate(rows, headers)
    sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=24,
                                                    cols=max((len(table.split('\n')[1])), 80)))  # Resize window
    print(table + '\n')  # Newline after table is more aesthetically pleasing.
    if extra is not None:
        print(extra + '\n')


def entry_sort_info(entry):
    """
    Provides the data of an entry in order as to prioritise sorting of data fields.
    Required to sort by days remaining then item type then subject then description.

    :param entry:           A DiaryEntry to be processed.
    :return:                A tuple containing the data of the entry in a sortable order.
    """
    days_left = entry.days_left if entry.days_left is not None else float('infinity')
    return days_left, entry.item_type, entry.subject, entry.description


def get_text_attributes(row_data):
    """
    Analyse entry data and return list of formatting attributes to add to the row.

    :param row_data:        A list of ordered entry data.
    :return:                List of attributes.
    """
    attrs = []
    days_left = row_data[-2]
    priority = row_data[-1]
    if days_left != NO_DATE:
        days_left = int(days_left)
        if days_left < 0:
            attrs.append('dark')
        if days_left == 0:
            attrs.append('reverse')
        if days_left == 1:
            attrs.append('underline')

    if priority:
        attrs.append('bold')

    return attrs


def determine_date_separator(string):
    """Analyse a date string and determine the character separating the components."""
    if not string:
        return None

    for separator in (' ', '/', '-'):
        if separator in string:
            return separator


def str_to_date(string):
    """
    Convert a string representation of a date to the datetime.date form and supplement missing values with
    corresponding values from today's date.

    :param string:          The date string.
    :return:                A datetime.date representation of `string`.
    """
    separator = determine_date_separator(string)
    if not string or string is NO_DATE:
        return None

    # No separator means only one value, and converting to datetime.date requires a list
    components = string.split(separator) if separator is not None else [string]
    today = datetime.date.today()

    # Substitute empty values with corresponding values from today's date
    day = int(components[0]) if len(components) >= 1 else today.day
    month = int(components[1]) if len(components) >= 2 else today.month
    year = int(components[2]) if len(components) >= 3 else today.year

    return datetime.date(year, month, day)


def date_to_str(date):
    """Convert a date to a string with a pre-determined format."""
    return date.strftime('%d/%m/%Y') if date not in (NO_DATE, None) else NO_DATE


def validate_date(string):
    """
    A condition to check whether a date string can be converted to a valid date.

    :param string:          The date str.
    :return:                True/False depending on whether the date string is valid.
    """
    try:
        _ = str_to_date(string)  # If fails, then invalid date
    except ValueError:
        return False
    return True


def complete_data(data):
    """
    Prompt user to enter previously unentered or invalid data.

    :param data:            A dict of required data names and their current values.
    :return:                None.
    """
    for key, value in data.items():
        if value or (key == PRIORITY and value is 0):
            continue  # Data is already present

        if key == ATTRIBUTE or data.get(ATTRIBUTE, False):  # Attribute has or is about to be specified
            i_value = match_value_parameter(data)
        label = key.capitalize().replace('_', ' ') + ': '  # Change data name to readable label

        param_info = PARAMETERS[key] if key != VALUE else i_value  # ATTRIBUTE comes before VALUE
        inp = get_input(prompt=label,
                        response_type=param_info.data_type,
                        condition=param_info.condition,
                        modifier=param_info.modifier,
                        err_msg=param_info.err_msg)

        if inp == CANCEL_CHARACTER:
            return CANCEL_CHARACTER

        data[key] = inp


def format_existing_data(data):
    """
    Convert data to required format for processing.

    :param data:            A dict of data names and values.
    :return:                None.
    """
    for key, value in data.items():
        if not value:
            continue  # No value to be formatted
        if key == ATTRIBUTE and value:  # `edit` function is running
            i_value = match_value_parameter(data)
            if i_value is None:  # Invalid attribute name passed
                data[ATTRIBUTE] = False
                break  # Continuing loop with no attribute causes crash as no parameter info exists for the new value
        param_info = PARAMETERS.get(key, None) if key != VALUE else i_value  # ATTRIBUTE comes before VALUE
        # Format value
        try:
            value = param_info.data_type(value)
        except ValueError:
            pass
        else:
            if param_info.condition is None or param_info.condition(value):
                data[key] = param_info.modifier(value) if param_info.modifier is not None else value
                continue
        data[key] = False  # Mark data as invalid by resetting value


def match_value_parameter(data):
    """
    Match attribute name from raw text to its ParameterInfo object

    :param data:            A dict containing names and values of data
    :return:
    """
    if data.get(ATTRIBUTE, False):  # Check to see if the attribute field has a value
        return PARAMETERS.get(ATTRIBUTES.get(data[ATTRIBUTE], None), None)  # Match parameter to data value


def prompt():
    """
    Prompt the user for a command to run and any arguments they wish to supply.

    :return:                The strings of the command and arguments. Command is None if not supplied.
    """
    inp = input(PROMPT + '> ')
    if not inp:
        return None, ''
    return process_input(inp)


def process_input(inp):
    """
    Split the raw command string into a command and its arguments.

    :param inp:             A string containing the users command.
    :return:                A tuple containing the name of the command and a string of arguments.
    """
    split_input = inp.split(maxsplit=1)  # Separate command from arguments
    command_str = split_input[0]
    try:
        command_str = COMMANDS[command_str]
    except KeyError:
        cprint("'{}' is not a valid command".format(command_str), 'yellow')
        return None, ''
    arg_string = split_input[1] if len(split_input) == 2 else ''  # Check is arguments were supplied
    return command_str, arg_string


def quit_cmdiary(*ignore):
    """Clean up and quit diary."""
    if os.name == 'nt':  # Colorama only required on Windows machines
        deinit()  # Colorama deinit function
    quit()

# Initialise diary object
diary = Diary()

# Define command parameters and required information.
# Variables with the i_ prefix are ParameterInfo types.
i_uid = ParameterInfo(UID,
                      int,
                      condition=lambda uid: int(uid) in diary.taken_uids,
                      err_msg='Object with UID {} does not exist')

i_item_type = ParameterInfo(ITEM_TYPE,
                            condition=lambda x: x in ITEM_TYPES.keys(),
                            modifier=lambda x: ITEM_TYPES.get(x, HOMEWORK),
                            err_msg="Item type '{}' does not exist. Available item types are "
                                    "assessment, homework and note.")

i_subject = ParameterInfo(SUBJECT)

i_description = ParameterInfo(DESCRIPTION)

i_due_date = ParameterInfo(DUE_DATE,
                           condition=validate_date,
                           modifier=str_to_date,
                           err_msg="Invalid date. Date format is dd/mm/yyyy. See help page or type 'help date' "
                                   "for more info.")
i_attr = ParameterInfo(ATTRIBUTE,
                       condition=lambda attr: attr in ATTRIBUTES,
                       modifier=lambda attr: ATTRIBUTES[attr],
                       err_msg="Attribute '{}' does not exist. Available attributes are type, subject, "
                               "description and duedate.")
i_days = ParameterInfo(DAYS,
                       int,
                       err_msg="'{}' is an invalid number. Please enter a number of days to extend by.")

i_priority = ParameterInfo(PRIORITY,
                           int,
                           condition=lambda x: x in (0, 1),
                           err_msg="'{}' is invalid, please enter 0 or 1.")

# Define regex for matching sections of input
RE_DUE_DATE = re.compile(r' (([0-9]{1,2} ?){1,2}([0-9]{4})?)$')

# Dict of parameter names and info objects
PARAMETERS = {UID: i_uid,
              ITEM_TYPE: i_item_type,
              SUBJECT: i_subject,
              DESCRIPTION: i_description,
              DUE_DATE: i_due_date,
              ATTRIBUTE: i_attr,
              DAYS: i_days,
              PRIORITY: i_priority}

# Dict mapping strings and abbreviations to possible attributes
ATTRIBUTES = {'t': ITEM_TYPE, 'type': ITEM_TYPE, ITEM_TYPE: ITEM_TYPE,
              's': SUBJECT, SUBJECT: SUBJECT,
              'd': DESCRIPTION, DESCRIPTION: DESCRIPTION,
              'due': DUE_DATE, 'duedate': DUE_DATE, DUE_DATE: DUE_DATE,
              'p': PRIORITY, 'priority': PRIORITY}

# Dict mapping strings and abbreviations to item types
ITEM_TYPES = {
    'a': ASSESSMENT, 'assessment': ASSESSMENT,
    'h': HOMEWORK, 'homework': HOMEWORK,
    'n': NOTE, 'note': NOTE
}

# Dict mapping strings and abbreviations to command functions
COMMANDS = {'add': add, 'a': add,
            'remove': remove, 'r': remove,
            'edit': edit, 'e': edit,
            'extend': extend, 'x': extend,
            'quit': quit_cmdiary, 'q': quit_cmdiary,
            'list': display, 'l': display,
            'help': get_info, 'h': get_info,
            'priority': priority, 'p': priority,
            'filter': filter_entries, 'f': filter_entries}

# Run the diary
if __name__ == '__main__':
    if os.name == 'nt':  # Colorama only required on Windows machines
        init()  # Colorama init function -- allows coloured text on Windows machines
    display()
    try:
        while True:
            command, args = prompt()
            if command is None:
                continue
            if command is get_info:
                args = args if args else None  # get_info has slightly different parameter requirements
            command(args)
            if command is not get_info:
                display()
    except KeyboardInterrupt:
        quit_cmdiary()  # Exit without crash info
