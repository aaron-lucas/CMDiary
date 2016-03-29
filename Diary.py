import pickle
import os.path
import datetime
from random import randint

from DiaryEntry import DiaryEntry


def update_data(func):
    """
    A decorator which automatically updates the data.pickle file after the diary has been changed.

    :param func:    The function which changes the state of the diary.
    :return:        A function that automatically updates the locally stored diary data.
    """
    def wrapper(self, *args, **kwargs):
        retval = func(self, *args, **kwargs)
        with open('data.pickle', 'wb') as file:
            for entry in self.entries:
                file.write(pickle.dumps(entry.data, pickle.HIGHEST_PROTOCOL))
        return retval

    return wrapper


class Diary(object):
    """
    A Diary class that contains a list of DiaryEntry objects and has methods to modify them.
    This class also handles local storing and fetching of all DiaryEntry data.
    """

    def __init__(self):
        """
        Load any locally stored data into the `entries` variable.
        :return: None
        """
        self.entries = self.load_data()

    def load_data(self):
        """
        Read and de-serialise each stored DiaryEntry object and load them into a list
        :return: A list of loaded DiaryEntry objects.
        """
        entry_data = []
        if not os.path.isfile('data.pickle'):
            open('data.pickle', 'w').close()  # Create file if none exists
        with open('data.pickle', 'rb') as source:
            try:
                while True:
                    entry_data.append(pickle.load(source))
            except EOFError:  # Stop looping through data at end of file
                pass

        return [DiaryEntry(self, **dataset) for dataset in entry_data]  # Create DiaryEntrys from stored data

    @property
    def taken_uids(self):
        """Returns a list of uids that are already in use."""
        return [entry.uid for entry in self.entries]

    @update_data
    def add(self, item_type, subject, description, due_date):
        """
        Add an entry to the diary.

        :param item_type:   A str containing the item type of the entry.
        :param subject:     A subject str.
        :param description: A description str.
        :param due_date:    A datetime.date object specifying the due date of the entry.
        :return:            None
        """
        self.entries.append(DiaryEntry(self, item_type, subject, description, due_date))

    @update_data
    def remove(self, *uids):
        """
        Remove entries from the diary.

        :param uids:    A list of ints which are uids of objects to remove.
        :return:        None
        """
        for entry in self.entries:
            if entry.uid in uids:
                self.entries.remove(entry)

    @update_data
    def edit(self, attr, value, *uids):
        """
        Edit diary entries.

        :param attr:    A str containing the attribute name to edit.
        :param value:   The new value to set.
        :param uids:    A list of ints which are uids of objects to edit
        :return:        None
        """
        for entry in self.entries:
            if entry.uid in uids:
                entry.edit(attr, value)

    @update_data
    def extend(self, days, *uids):
        """
        Extend the due date of diary entries.
        :param days:    An int specifying the number of days to extend by (can be negative).
        :param uids:    A list of ints which are uids of objects to extend.
        :return:        None
        """
        for entry in self.entries:
            if entry.uid in uids:
                if entry.due_date is None:
                    continue
                entry.due_date += datetime.timedelta(days=days)

    @update_data
    def priority(self, priority,  *uids):
        """
        Set the priority of diary entries.
        :param priority:    A bool specifying whether the entries have priority.
        :param uids:        A list of ints which are uids of objects to extend.
        :return:            None
        """
        for entry in self.entries:
            if entry.uid in uids:
                entry.priority = priority

    def generate_initial_uid(self):
        """
        Generate a uid that is not already used.
        This will be changed later on based on the order of display.
        :return:    An int between 100 and 999.
        """
        while True:
            uid = randint(100, 999)
            if uid not in self.taken_uids:
                return uid

    def filter(self, expression):
        raise NotImplementedError
