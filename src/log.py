import os
import logging
import threading
import logging.handlers

from mirte.core import Module
from sarah.io import IntSocketFile
from sarah.runtime import ExceptionCatchingWrapper
from sarah.socketServer import UnixSocketServer

class LogServer(UnixSocketServer):
        class SocketHandler(logging.handlers.SocketHandler):
                def __init__(self, socket):
                        self.__socket = socket
                        logging.handlers.SocketHandler.__init__(self, None,
                                        None)
                def makeSocket(self):
                        return self.__socket

        class Handler(object):
                def __init__(self, server, _socket, l):
                        self.l = l
                        self.server = server
                        self.f = ExceptionCatchingWrapper(
                                        IntSocketFile(_socket),
                                        self._on_exception)
                        self.handler = LogServer.SocketHandler(self.f)
                        self.socket = _socket
                        self.running = True

                def _on_exception(self, attr, exc):
                        if attr == 'send':
                                self.interrupt()
                                return 0
                        raise exc

                def interrupt(self):
                        self.f.interrupt()
                        self.running = False

                def handle(self):
                        logging.getLogger('').addHandler(self.handler)
                        while self.server.running and self.running:
                                rs, ws, xs = self.server.selectPool.select(
                                                (), (), (self.socket,))
                                if self.socket in xs:
                                        break

                def cleanup(self):
                        logging.getLogger('').removeHandler(self.handler)
                        self.socket.close()

        def create_handler(self, con, addr, logger):
                return LogServer.Handler(self, con, logger)
