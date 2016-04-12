import re
from datetime import date
from DiaryEntry import UID, ITEM_TYPE, SUBJECT, DESCRIPTION, DUE_DATE, PRIORITY, DAYS_LEFT
ATTR_MSG = 'Attribute does not exist'
VALUE_MSG = 'Invalid value'
FILTER_ATTRIBUTES = {
    'uid': UID, 'u': UID,
    'type': ITEM_TYPE, 't': ITEM_TYPE, 'item_type': ITEM_TYPE,
    'subject': SUBJECT, 's': SUBJECT,
    'description': DESCRIPTION, 'd': DESCRIPTION,
    'duedate': DUE_DATE, 'due': DUE_DATE,
    'priority': PRIORITY, 'p': PRIORITY,
    'daysleft': DAYS_LEFT, 'days': DAYS_LEFT
}


class FilterException(Exception):
    pass


def filter_function(function):
    def wrapper(self, attr, value):
        matched = []
        for obj in self.objects:
            try:
                obj_value = getattr(obj, attr)
            except AttributeError:
                return ATTR_MSG
            if obj_value is None:
                continue
            try:
                if function(self, obj_value, value):
                    matched.append(obj)
            except ValueError:
                return VALUE_MSG
            except TypeError:
                return 'Due date cannot be used with the < or > operator. Use \'days\' instead.'
        return matched
    return wrapper


class Filter:
    condition_format = re.compile('(.*?)([=<>:])(.*)')

    def __init__(self, objects, initial=None):
        self.original = objects
        self.objects = objects
        self.filters = []
        if initial is not None:
            self.refine(initial)

    def refine(self, condition):
        if self.is_valid_condition(condition):
            attr, operator, value = re.match(self.condition_format, condition).groups()
            attr = FILTER_ATTRIBUTES.get(attr, 'error')
            matched_objects = self.select(attr, operator, value)
            if type(matched_objects) is list:
                self.objects = matched_objects
                self.filters.append('{} {} {}'.format(attr, operator, value))
            else:
                raise FilterException(matched_objects)

    def is_valid_condition(self, condition):
        return bool(re.match(self.condition_format, condition))

    def select(self, attr, operator, value):
        if operator == '=':
            return self.equal_to(attr, value)
        if operator == '>':
            return self.greater_than(attr, value)
        if operator == '<':
            return self.less_than(attr, value)
        if operator == ':':
            return self.contains(attr, value)

    def reset(self):
        self.objects = self.original
        self.filters = []

    @filter_function
    def equal_to(self, obj_val, filter_val):
        return str(obj_val).lower() == str(filter_val).lower()

    @filter_function
    def less_than(self, obj_val, filter_val):
        return int(obj_val) < int(filter_val)

    @filter_function
    def greater_than(self, obj_val, filter_val):
        return int(obj_val) > int(filter_val)

    @filter_function
    def contains(self, obj_val, filter_val):
        return str(filter_val).lower() in str(obj_val).lower()

    @property
    def filter_string(self):
        return '\n'.join(self.filters)


# Format    [attr][operator][value]

# Operators:
# -----------
# =     Equal to
# >     Greater than
# <     Less than
# :     Includes
