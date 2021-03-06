from mirte.core import Module

from six.moves import range
import six

import select
import socket
import threading


class SelectPool(Module):
    """ Pools select (2) calls in one call and adds convencience
        functionality """

    def __init__(self, *args, **kwargs):
        super(SelectPool, self).__init__(*args, **kwargs)
        self.running = True
        self.lock = threading.Lock()
        self.sp = socket.socketpair()
        self.lut = (dict(), dict(), dict())
        self.rlut = dict()
        self.events = set()

    def select(self, rs=None, ws=None, xs=None):
        event = threading.Event()
        ret = [None]
        ss = [[] if _s is None else _s for _s in (rs, ws, xs)]

        def callback(rs, ws, xs):
            ret[0] = (rs, ws, xs)
            event.set()
            return False
        with self.lock:
            self.events.add(event)
            for i in range(3):
                for s in ss[i]:
                    self.__register(s, i, callback)
            self._interrupt()
        event.wait()
        with self.lock:
            self.events.remove(event)
            for i in range(3):
                for s in ss[i]:
                    self.__deregister(s, i)
        return ((), (), ()) if ret[0] is None else ret[0]

    def register(self, callback, rs=None, ws=None, xs=None):
        def outer_callback(rs, ws, xs):
            try:
                ret = callback(rs, ws, xs)
            except Exception:
                self.l.exception("Uncaught exception")
            if not ret:
                return
            for i in range(3):
                for s in ss[i]:
                    self.__register(s, i, inner_callback)
            self.interrupt()

        def inner_callback(rs, ws, xs):
            for i in range(3):
                for s in ss[i]:
                    self.__deregister(s, i)
            self.threadPool.execute_named(
                outer_callback,
                'selectPool outer_callback',
                rs,
                ws,
                xs
            )
        ss = [[] if _s is None else _s for _s in (rs, ws, xs)]
        with self.lock:
            for i in range(3):
                for s in ss[i]:
                    self.__register(s, i, inner_callback)
            self._interrupt()

    def deregister_callback(self, callback):
        with self.lock:
            if callback not in self.clut:
                raise KeyError
            for s, i in self.clut[callback]:
                self.__deregister(s, i)
            del(self.clut[callback])

    def deregister(self, rs=None, ws=None, xs=None):
        ss = [[] if _s is None else _s for _s in (rs, ws, xs)]
        with self.lock:
            for i in range(3):
                for s in ss[i]:
                    self.__deregister(s, i)

    def __register(self, s, idx, callback):
        if s in self.lut[idx]:
            raise KeyError
        self.lut[idx][s] = callback
        if callback not in self.rlut:
            self.rlut[callback] = set()
        self.rlut[callback].add((s, idx))

    def __deregister(self, s, idx):
        if s not in self.lut[idx]:
            raise KeyError
        self.rlut[self.lut[idx][s]].remove((s, idx))
        del(self.lut[idx][s])

    def run(self):
        self.lock.acquire()
        while self.running:
            self.run__inner_loop()
        self.lock.release()

    def run__inner_loop(self):
        ri = list(six.iterkeys(self.lut[0]))
        wi = list(six.iterkeys(self.lut[1]))
        xi = list(six.iterkeys(self.lut[2]))
        self.lock.release()
        ret = None
        try:
            ret = select.select(ri + [self.sp[1]], wi, xi)
        except select.error as e:
            if e[0] == 9:
                self.l.warn('Bad file descriptor')
            else:
                raise
        self.lock.acquire()
        if ret is None:
            return
        todo = dict()
        for i in range(3):
            for f in ret[i]:
                if i == 0 and f == self.sp[1]:
                    self.sp[1].recv(4096)
                    continue
                if f not in self.lut[i]:
                    # f has been deregistered in between
                    continue
                cb = self.lut[i][f]
                if cb not in todo:
                    todo[cb] = (list(), list(), list())
                todo[cb][i].append(f)
        for cb, lists in six.iteritems(todo):
            try:
                cb(*lists)
            except Exception:
                self.l.exception("Uncaught exception")

    def stop(self):
        with self.lock:
            self.running = False
            self._interrupt()
            for event in self.events:
                event.set()

    def interrupt(self):
        with self.lock:
            self._interrupt()

    def _interrupt(self):
        self.sp[0].send('Poke')
# vim: et:sta:bs=2:sw=4:
