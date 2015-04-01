_error_list = ['InvalidArgumentError',
              'NonexistentUIDError']

for name in _error_list:
	globals()[name] = type(name, (Exception,), {})
