# CMDiary - a command-line diary application

VERSION = 'v2.0.2'
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

from DiaryEntry import ASSESSMENT, HOMEWORK, NOTE, UID, ITEM_TYPE, SUBJECT, DESCRIPTION, DUE_DATE
from Diary import Diary
from ParameterInfo import ParameterInfo
from info import get_info

# Define custom parameter names
ATTRIBUTE = 'attribute'
VALUE = 'value'  # Changes depending on chosen attribute - used in edit()
DAYS = 'days'  # days parameter name/reference
NEW_UID = 'new_uid'  # Parameter name requiring nonexistent uid

COLOUR_MAP = {ASSESSMENT: 'red',
              HOMEWORK: 'blue',
              NOTE: 'green'}

NO_DATE = 'N/A'  # String used as placeholder if no date is specified


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


def update(func):
    """
    A decorator that updates the diary table after running the specified function.

    :param func: The function after which to update the diary table.
    :return:     A new function that automatically updates the screen after running.
    """
    def wrapper(*args, **kwargs):
        retval = func(*args, **kwargs)
        display()
        return retval

    return wrapper


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
            if inp or inp == '':  # Empty string signifies no value
                inp = response_type(inp)
        except:
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


@update
@requires_parameters(ITEM_TYPE, SUBJECT, DESCRIPTION, DUE_DATE)
def add(input_data, required_data):
    """
    Take and evaluate input to add a diary entry.

    Signature is add(input_data) after decoration.

    :param input_data:      The raw str data entered after the 'add' command.
    :param required_data:   A dict provided by the requires_parameters decorator. Doesn't need to be specified when
                            called due to the decorator.
    :return:                None
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
    complete_data(required_data)

    diary.add(**required_data)  # Parameter names in required_data match with diary.add function


@update
@requires_parameters(UID)
def remove(input_data, required_data):
    """
    Take and evaluate input to remove an entry from the diary.

    Signature is remove(input_data) after decoration.

    :param input_data:      The raw str data entered after the 'remove' command.
    :param required_data:   A dict provided by the requires_parameters decorator. Doesn't need to be specified when
                            called due to the decorator.
    :return:                None
    """
    try:
        required_data[UID] = input_data.split()[0]  # UID is always first word
    except IndexError:
        pass  # Ignore error if data not specified as it will be entered later

    format_existing_data(required_data)
    complete_data(required_data)

    diary.remove(required_data[UID])


@update
@requires_parameters(UID, ATTRIBUTE, VALUE)
def edit(input_data, required_data):
    """
    Take and evaluate input to edit an entry in the diary.

    Signature is edit(input_data) after decoration.

    :param input_data:      The raw str data entered after the 'edit' command.
    :param required_data:   A dict provided by the requires_parameters decorator. Doesn't need to be specified when
                            called due to the decorator.
    :return:                None
    """
    try:
        required_data[UID] = input_data.split()[0]  # UID is always first word
        required_data[ATTRIBUTE] = input_data.split()[1]  # atribute is always second word
        required_data[VALUE] = ' '.join(input_data.split()[2:])  # Rest of the string is new value
    except IndexError:
        pass  # Ignore error if data not specified as it will be entered later

    format_existing_data(required_data)
    if any([not bool(val) for val in required_data.values()]):  # Check if any data needs to be entered
        complete_data(required_data)
    diary.edit(required_data[ATTRIBUTE], required_data[VALUE], required_data[UID])


@update
@requires_parameters(UID, DAYS)
def extend(input_data, required_data):
    """
    Take and evaluate input to extend the due date of an entry.

    Signature is remove(input_data) after decoration.

    :param input_data:      The raw str data entered after the 'remove' command.
    :param required_data:   A dict provided by the requires_parameters decorator. Doesn't need to be specified when
                            called due to the decorator.
    :return:                None
    """
    try:
        required_data[UID] = input_data.split()[0]  # UID is always first word
        required_data[DAYS] = input_data.split()[1]  # days is always second word
    except IndexError:
        pass  # Ignore error if data not specified as it will be entered later

    format_existing_data(required_data)
    complete_data(required_data)

    diary.extend(required_data[DAYS], required_data[UID])


def display(filter_=None):  # Filter not yet implemented
    """
    Display all diary entries and info as a table on the screen.

    :param filter_: A string to be analysed to view only certain entries. Not yet implemented.
    :return: None.
    """
    os.system('cls' if os.name == 'nt' else 'clear')  # For Windows/Mac/Linux compatibility
    if not len(diary.entries):
        cprint('Diary has no entries.\n', 'yellow')
        return
    headers = ('UID', 'Type', 'Subject', 'Description', 'Due Date', 'Days Left')
    rows = []
    for entry in diary.entries:
        due_date = entry.due_date if entry.due_date is not None else NO_DATE
        days_left = entry.days_left if entry.days_left is not None else NO_DATE
        rows.append([str(entry.uid),
                     entry.item_type,
                     entry.subject,
                     entry.description,
                     date_to_str(due_date),
                     str(days_left)])  # Format some data to str

    rows.sort(key=lambda r: r[-1])  # Sort by days remaining
    rows = [[colored(attr, COLOUR_MAP[row[1]], attrs=get_text_attributes(row)) for attr in row]
            for row in rows]  # Colour-code rows based on item type
    table = tabulate(rows, headers)
    sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=24,
                                                    cols=max((len(table.split('\n')[1])), 80)))  # Resize window
    print(table + '\n')  # Newline after table is more aesthetically pleasing.


def get_text_attributes(row_data):
    """
    Analyse entry data and return list of formatting attributes to add to the row.

    :param row_data: A list of ordered entry data.
    :return: List of attributes.
    """
    attrs = []
    days_left = row_data[-1]
    if days_left != NO_DATE:
        days_left = int(days_left)
        if days_left < 0:
            attrs.append('dark')
        if days_left == 0:
            attrs.append('reverse')
        if days_left == 1:
            attrs.append('underline')
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

    :param string: The date string.
    :return: A datetime.date representation of `string`.
    """
    separator = determine_date_separator(string)
    if not string:
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
    return date.strftime('%d/%m/%Y') if date is not NO_DATE else NO_DATE


def validate_date(string):
    """
    A condition to check whether a date string can be converted to a valid date.

    :param string: The date str.
    :return: True/False depending on whether the date string is valid.
    """
    try:
        _ = str_to_date(string)  # If fails, then invalid date
    except ValueError:
        return False
    return True


def complete_data(data):
    """
    Prompt user to enter previously unentered or invalid data.

    :param data: A dict of required data names and their current values.
    :return: None
    """
    for key, value in data.items():
        if value:
            continue  # Data is already present
        if ATTRIBUTE in data.keys():  # User wishes to edit an entry
            i_value = match_value_parameter(data)
        label = key.capitalize().replace('_', ' ') + ': '  # Change data name to readable label

        param_info = PARAMETERS[key] if key != VALUE else i_value  # Get info about required data
        data[key] = get_input(prompt=label,
                              response_type=param_info.data_type,
                              condition=param_info.condition,
                              modifier=param_info.modifier,
                              err_msg=param_info.err_msg)


def format_existing_data(data):
    """
    Convert data to required format for processing.

    :param data: A dict of data names and values.
    :return: None
    """
    for key, value in data.items():
        if not value:
            continue  # No value to be formatted
        if ATTRIBUTE in data.keys():  # User wishes to edit an entry
            i_value = match_value_parameter(data)
        param_info = PARAMETERS[key] if key != VALUE else i_value  # Get info about required data

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
    :param data: A dict containing names and values of data
    :return:
    """
    if data.get(ATTRIBUTE, False):  # Check to see if the attribute field has a value
        if data[ATTRIBUTE] == UID:
            i_value = i_new_uid  # The attribute argument is only used in `edit` so a new uid should be specified
        else:
            i_value = PARAMETERS[ATTRIBUTES[data[ATTRIBUTE]]]  # Match parameter to data value
        return i_value


def prompt():
    """
    Prompt the user for a command to run and any arguments they wish to supply.

    :return: The strings of the command and arguments. Command is None if not supplied.
    """
    inp = input('CMDiary {}> '.format(VERSION))
    if not inp:
        return None, ''
    split_input = inp.split(maxsplit=1)  # Separate command from arguments
    command_str = split_input[0]
    try:
        command_str = COMMANDS[command_str]
    except KeyError:
        cprint("'{}' is not a valid command".format(command_str), 'yellow')
        return None, ''
    arg_string = split_input[1] if len(split_input) == 2 else ''  # Check is arguments were supplied
    return command_str, arg_string


def quit_cmdiary():
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

i_new_uid = ParameterInfo(NEW_UID,
                          int,
                          condition=lambda uid: (uid not in diary.taken_uids) and (uid in range(1, 1000)),
                          err_msg='Object with UID {} already exists or invalid uid (must be between 1 and 999)')

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
                       int)

# Define regex for matching sections of input
RE_DUE_DATE = re.compile(r' (([0-9]{1,2} ?){1,2}([0-9]{4})?)$')

# Dict of parameter names and info objects
PARAMETERS = {UID: i_uid,
              NEW_UID: i_new_uid,
              ITEM_TYPE: i_item_type,
              SUBJECT: i_subject,
              DESCRIPTION: i_description,
              DUE_DATE: i_due_date,
              ATTRIBUTE: i_attr,
              DAYS: i_days}

# Dict mapping strings and abbreviations to possible attributes
ATTRIBUTES = ({'u': UID, UID: UID,
               't': ITEM_TYPE, 'type': ITEM_TYPE, ITEM_TYPE: ITEM_TYPE,
               's': SUBJECT, SUBJECT: SUBJECT,
               'd': DESCRIPTION, DESCRIPTION: DESCRIPTION,
               'due': DUE_DATE, 'duedate': DUE_DATE, DUE_DATE: DUE_DATE})

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
            'help': get_info, 'h': get_info}

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
    except KeyboardInterrupt:
        quit_cmdiary()  # Exit without crash info
