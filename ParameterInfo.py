class ParameterInfo(object):
    def __init__(self, name, data_type=str, condition=None, modifier=None, err_msg=None):
        self.name = name
        self.data_type = data_type
        self.condition = condition
        self.modifier = modifier
        self.err_msg = err_msg
