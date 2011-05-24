import select
import socket

class KeyboardInterruptableEvent(object):
        """ Acts like threading.Event, but a call to .wait will interrupt on
            a keyboard interrupt """
        def __init__(self):
                self.flag = False
                self.sp = socket.socketpair()
        def wait(self, timeout=None):
                select.select((self.sp[1],), (), (), timeout)
        def set(self):
                self.sp[0].send('Good morning!')
        def isSet(self):
                rs, ws, xs = select.select((self.sp[1],), (), (), 0)
                return not self.sp[1] in rs
        def clear(self):
                while True:
                        read = self.sp[0].recv(4096)
                        if read != 4096:
                                break

