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

class CallCatchingWrapper(object):
        def __init__(self, wrapped, condition, callback):
                """ Creates a wrapper around <wrapped>.  Calls to callable
                    attributes which match <condition> are replaced by calls
                    to <callback>(name, func, args, kwargs), where <name> is
                    the name of the intercepted callable attribute, <func> the
                    original function, <(kw)args> the (keyword) arguments which
                    were passed to the call. The return value of the callback,
                    is returned to the caller. """
                object.__setattr__(self, '_wrapped', wrapped)
                object.__setattr__(self, '_condition', condition)
                object.__setattr__(self, '_callback', callback)
        def __getattribute__(self, name):
                wrapped = object.__getattribute__(self, '_wrapped')
                condition = object.__getattribute__(self, '_condition')
                a = getattr(wrapped, name)
                if callable(a) and condition(name):
                        cb = object.__getattribute__(self, '_callback')
                        def wrapper(*args, **kwargs):
                                return cb(name, a, args, kwargs)
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
