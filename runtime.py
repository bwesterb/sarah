import functools

class ExceptionCatchingWrapper(object):
	def __init__(self, wrapped, callback):
		""" Creates a wrapper around <wrapped>.  If any call to a
		    callable attribute throws an exception, callback will be
		    called with the name of the callable attribute as first
		    argument and the exception as second. The return value
		    of the callback will be the return value of the callable
		    attribute. """
		object.__setattr__(self, '_wrapped', wrapped)
		object.__setattr__(self, '_callback', callback)
	def __getattribute__(self, name):
		wrapped = object.__getattribute__(self, '_wrapped')
		a = getattr(wrapped, name)
		if callable(a):
			cb = object.__getattribute__(self, '_callback')
			def wrapper(*args, **kwargs):
				try:
					return a(*args, **kwargs)
				except Exception as e:
					return cb(name, e)
			return wrapper
		return a
	def __setattr__(self, name, value):
		wrapped = object.__getattribute__(self, '_wrapped')
		setattr(wrapped, name, value)
	def __delattr__(self, name):
		wrapped = object.__getattribute__(self, '_wrapped')
		delattr(wrapped, name)

def _get_by_path(bits, _globals):
	c = None
	for i, bit in enumerate(bits):
		try:
			c = globals()[bit] if c is None else getattr(c, bit)
		except (AttributeError, KeyError):
			c = __import__('.'.join(bits[:i+1]), _globals,
				fromlist=[bits[i+1]] if i+1 < len(bits) else [])
	return c

def get_by_path(path, _globals=None):
	""" Returns an object by <path>, importing modules if necessary """
	if _globals is None: _globals = list()
	return _get_by_path(path.split('.'), _globals)
