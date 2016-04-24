import re
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
    """
    An exception class which indicates an exception originating from a Filter object.
    Is only defined for the custom name.
    """
    pass


def filter_function(function):
    """
    A decorator which filters through the entries according to a condition provided by the decorated function.
    The decorated function should have the signature decorated_function(self, obj_value, filter_value) to specify
    the condition between the value given and that of the object but will end up with the signature
    decorated_function(attr, value, negate=False) to determine the attribute and value to compare.

    :param function:        The function to be decorated.
    :return:                A decorated function.
    """
    def wrapper(self, attr, value, negate=False):
        matched = []
        for obj in self.objects:
            try:
                obj_value = getattr(obj, attr)
            except AttributeError:  # If invalid attribute is specified
                return ATTR_MSG
            if obj_value is None and value.lower() != 'none':  # Skip over blank values if not looking for them
                continue
            try:
                if negate:
                    if not function(self, obj_value, value):
                        matched.append(obj)
                else:
                    if function(self, obj_value, value):
                        matched.append(obj)
            except ValueError:  # If type conversion fails
                return VALUE_MSG
            except TypeError:  # If a date is converted to int
                return 'Due date cannot be used with the < or > operator. Use \'days\' instead.'
        return matched
    return wrapper


class Filter:
    """
    A class which can filter through a list of objects by comparing the value of an attribute to a given value.
    The condition format to use is [attribute][operator][value].

    :param objects:         A list of objects to be filtered.
    :param initial:         An initial filter condition string.
    """
    condition_format = re.compile('(.*?)\s*(!?[=<>:])(.*)')

    def __init__(self, objects):
        """Initialise instance variables."""
        self.original = objects  # Allows resetting of conditions
        self.objects = objects
        self.filters = []

    def refine(self, condition):
        """
        Add a condition to refine the list of filtered objects.

        :param condition:   A condition string.
        :return:            None.
        """
        if self.is_valid_condition(condition):
            attr, operator, value = re.match(self.condition_format, condition).groups()  # Regex splits up raw string
            attr = FILTER_ATTRIBUTES.get(attr, 'error')  # Attribute could be given in abbreviated form or not exist
            matched_objects = self.select(attr, operator, value)  # Could be a list of filtered objects or error string
            if type(matched_objects) is list:  # No error occurred
                self.objects = matched_objects
                self.filters.append('{} {} {}'.format(attr, operator, value))
            else:  # Error occurred
                raise FilterException(matched_objects)

    def is_valid_condition(self, condition):
        """
        Checks raw condition string to check whether it is in the valid pattern.

        :param condition:   The raw condition string.
        :return:            A bool specifying whether the condition is valid.
        """
        return bool(re.match(self.condition_format, condition))

    def select(self, attr, operator, value):
        """
        Maps operators to filter functions and selects all objects which match the condition.

        :param attr:        The name of the attribute of the object to compare.
        :param operator:    The operation to perform (either =, <, >, :, possibly with a ! prefixed).
        :param value:       The value to compare to.
        :return:            A list of matched objects or an error string.
        """
        if '!' in operator:
            operator = operator.strip('!')
            negate = True
        else:
            negate = False

        if operator == '=':
            return self.equal_to(attr, value, negate)
        elif operator == '>':
            return self.greater_than(attr, value, negate)
        elif operator == '<':
            return self.less_than(attr, value, negate)
        elif operator == ':':
            return self.contains(attr, value, negate)

    def reset(self):
        """
        Resets the filter and clears all conditions.

        :return:            None.
        """
        self.objects = self.original
        self.filters = []

    @property
    def filter_string(self):
        """
        Formats all active conditions into a string.

        :return:            String of active conditions.
        """
        return '\n'.join(self.filters)

    # The following functions define conditions for the operators however are decorated to actually
    # filter the list of objects
    # Signature after decoration is function(self, attr, value, negate=False).
    # :param attr:          The name of the attribute to compare.
    # :param value:         The given value to compare
    # :param negate:        Determines whether the condition should be negated
    # :return:

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
