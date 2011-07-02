from __future__ import with_statement

from mirte.core import Module
from sarah.event import Event

import weakref
import threading

# python 2.6 support
if hasattr(weakref, 'WeakSet'):
        WeakSet = weakref.WeakSet
else:
        import weakrefset
        WeakSet = weakrefset.WeakSet

class RefStore(Module):
        def __init__(self, *args, **kwargs):
                super(RefStore, self).__init__(*args, **kwargs)
                self.namespaces = WeakSet()
        def create_namespace(self):
                ret = NameSpace()
                self.namespaces.add(ret)
                return ret

class NameSpace(object):
        def __init__(self):
                self.obj_to_key = weakref.WeakKeyDictionary()
                self.key_to_obj = weakref.WeakValueDictionary()
                self.lock = threading.Lock()
                self.n = 0

        def key_of(self, obj):
                with self.lock:
                        try:
                                return self.obj_to_key[obj]
                        except KeyError:
                                self.n += 1
                                self.obj_to_key[obj] = self.n
                                self.key_to_obj[self.n] = obj
                                return self.n

        def by_key(self, key):
                return self.key_to_obj[key]
