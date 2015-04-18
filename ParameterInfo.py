class ParameterInfo(object):
    """
    A class containing all required data for analysing and modifying parameters/arguments specified with commands.

    :param name:        The str name of the parameter.
    :param data_type:   The data type required for the parameter.
    :param condition:   A function that returns True/False depending if a value passes certain criteria.
    :param modifier:    A function that returns a modified value after passing `condition`.
    :param err_msg:     A str specifying an error message should anything fail.
    """

    def __init__(self, name, data_type=str, condition=None, modifier=None, err_msg=None):
        """Initialise instance variables."""
        self.name = name
        self.data_type = data_type
        self.condition = condition
        self.modifier = modifier
        self.err_msg = err_msg
