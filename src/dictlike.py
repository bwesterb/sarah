import weakref
import json

import six


class Self(object):

    def __init__(self, wrapped):
        object.__setattr__(self, '_wrapped', weakref.ref(wrapped))

    def __getattribute__(self, name):
        object.__getattribute__(object.__getattribute__(
            self, '_wrapped')(), name)

    def __setattr__(self, name, value):
        object.__setattr__(object.__getattribute__(
            self, '_wrapped')(), name, value)

    def __delattr__(self, name):
        object.__delattr__(object.__getattribute__(
            self, '_wrapped')(), name)


class DictLike(object):
    """ Base class for a dictionary based object.
        Think about wrappers around JSON data. """

    def __init__(self, data):
        object.__setattr__(self, 'self', Self(self))
        self.self._data = data

    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError

    def __setattr__(self, name, value):
        self._data[name] = value

    def __delattr__(self, name):
        del self._data[name]

    def to_dict(self):
        return self._data

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__,
                           json.dumps(self._data).encode('utf-8'))


class AliasingMixin(object):
    aliases = {}

    @classmethod
    def normalize_dict(cls, data):
        _data = {}
        aliases = cls.aliases
        for k, v in six.iteritems(data):
            if k in aliases:
                k = aliases[k]
            _data[k] = v
        return _data

    def __getattr__(self, name):
        if name in type(self).aliases:
            name = type(self).aliases[name]
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError

    def __setattr__(self, name, value):
        if name in type(self).aliases:
            name = type(self).aliases[name]
        self._data[name] = value

    def __delattr__(self, name):
        if name in type(self).aliases:
            name = type(self).aliases[name]
        del self._data[name]

    def _generate_reverse_aliases(self):
        ass = type(self).aliases
        rass = {}
        for k, v in six.iteritems(ass):
            rass[v] = k
        type(self).reverse_aliases = rass

    def to_unaliased_dict(self):
        if not hasattr(type(self), 'reverse_aliases'):
            self._generate_reverse_aliases()
        lut = type(self).reverse_aliases
        d = {}
        for k, v in six.iteritems(self._data):
            if k in lut:
                k = lut[k]
            d[k] = v
        return d

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, json.dumps(
            self.to_unaliased_dict()).encode('utf-8'))


class AliasingDictLike(AliasingMixin, DictLike):
    """ A DictLike where keys have aliases provided by __class__.aliases
    """

    def __init__(self, data):
        super(AliasingDictLike, self).__init__(
            self.normalize_dict(data))
# vim: et:sta:bs=2:sw=4:
