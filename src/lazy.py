# Based on lazy_import from Ryan Kelly's esky.

import sys

import six


def lazy(func):
    """ Decorator, which can be used for lazy imports

            @lazy
            def yaml():
                import yaml
                return yaml """
    try:
        frame = sys._getframe(1)
    except Exception:
        _locals = None
    else:
        _locals = frame.f_locals
    func_name = func.func_name if six.PY2 else func.__name__
    return LazyStub(func_name, func, _locals)


class LazyStub(object):

    def __init__(self, name, loader, _locals=None):
        self.__loaded = None
        self.__loader = loader
        self.__locals = _locals
        self.__name = name

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            if self.__loaded is None:
                self.__load()
            return getattr(self.__loaded, attr)

    def __nonzero__(self):
        if self.__loaded is None:
            self.__load()
        return bool(self.__loaded)
    __bool__ = __nonzero__

    def __load(self):
        assert self.__loaded is None
        self.__loaded = self.__loader()
        if self.__locals is not None:
            try:
                if self.__locals[self.__name] is self:
                    self.__locals[self.__name] = self.__loaded
            except KeyError:
                pass

# vim: et:sta:bs=2:sw=4:
