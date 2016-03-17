import datetime

HOMEWORK = 'homework'
ASSESSMENT = 'assessment'
NOTE = 'note'

UID = 'uid'
SUBJECT = 'subject'
DESCRIPTION = 'description'
DUE_DATE = 'due_date'
ITEM_TYPE = 'item_type'
PRIORITY = 'priority'


class CheckedVar(object):
    """
    A descriptor that requires its value be one of the following:
    1. Any value of a pre-determined type.
    2. A selection of a list of pre-defined values.
    3. None.

    :param data_type:   A class which is the type of the stored value.
    :param options:     A set of options that the value can be. Each option must be of the same type.
    :param default:     The initial, default value.
    """

    def __init__(self, data_type, options=None, default=None):
        """Initialise instance variables."""
        self._store_id = '__CheckedVar_{}'.format(id(self))  # A unique reference name
        self.data_type = data_type
        self.options = set() if options is None else set(filter(lambda x: isinstance(x, data_type), options))
        self.default = default if self.is_valid_value(default) else None

    def __set__(self, instance, value):
        """Set a new value to the descriptor after checking whether it is valid."""
        if self.is_valid_value(value):
            setattr(instance, self._store_id, value)
        else:
            raise ValueError('New value must be of type {}.'.format(self.data_type))

    def __get__(self, instance, owner):
        """Retrieve and return the value stored by the descriptor."""
        return getattr(instance, self._store_id, self.default)

    def is_valid_value(self, value):
        """
        Check if the supplied value meets the criteria of the descriptor.

        :param value:   The value to test.
        :return:        True if value passes test, False otherwise.
        """
        if value is None:
            return True
        elif self.options:
            return value in self.options
        return isinstance(value, self.data_type)


class DiaryEntry(object):
    """
    A class containing all the data for a typical diary entry. Each of these variables (except for `days_left`
    which is a property) are CheckedVars to ensure type safety when manipulating the values.

    :param owner:       The Diary object which the entry belongs to.
    :param item_type:   The type of the diary entry (either homework, assessment or note).
    :param subject:     The subject str.
    :param description: The description str.
    :param due_date:    A datetime.date object representing the entry's due date.
    :param uid:         An int specifying a UID. Typically only used when loading data from file.
    """

    uid = CheckedVar(int)
    subject = CheckedVar(str)
    description = CheckedVar(str)
    due_date = CheckedVar(datetime.date)
    item_type = CheckedVar(str, [HOMEWORK, ASSESSMENT, NOTE])
    priority = CheckedVar(bool, default=False)

    def __init__(self, owner, item_type, subject, description, due_date, uid=None, priority=False):
        """Initialise instance variables."""
        self.owner = owner
        self.item_type = item_type
        self.subject = subject
        self.description = description
        self.due_date = due_date
        self.uid = owner.generate_initial_uid() if uid is None else uid
        self.priority = priority


    def edit(self, attr, value):
        """
        Edit the data in the entry.

        :param attr:    The str name of the attribute to edit.
        :param value:   The new value.
        :return:        None
        """
        if attr in (UID, SUBJECT, DESCRIPTION, DUE_DATE, ITEM_TYPE, PRIORITY):  # Available attributes
            setattr(self, attr, value)

    @property
    def data(self):
        """Returns a dict of the data required to re-create an identical DiaryEntry object."""
        return {UID: self.uid,
                SUBJECT: self.subject,
                DESCRIPTION: self.description,
                DUE_DATE: self.due_date,
                ITEM_TYPE: self.item_type,
                PRIORITY: self.priority}

    @property
    def days_left(self):
        """Calculates the days remaining until the task is due."""
        if self.due_date is None:
            return None
        return (self.due_date - datetime.date.today()).days