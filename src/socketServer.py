import os
import socket
import os.path
import logging
import threading

from mirte.core import Module

class SocketServer(Module):
        def __init__(self, *args, **kwargs):
                super(SocketServer, self).__init__(*args, **kwargs)
                self.lock = threading.Lock()
                self.running = False
                self.handlers = set()
                self.n_conn = 0
        def create_listening_socket(self):
                raise NotImplementedError
        def create_handler(self, con, addr, logger):
                raise NotImplementedError
        def run(self):
                with self.lock:
                        assert not self.running
                        self.running = True
                        self.socket = self.create_listening_socket()
                        self.selectPool.register(self._on_socket_activity,
                                        [self.socket])
        def _on_socket_activity(self, rs, ws, xs):
                with self.lock:
                        con, addr = self.socket.accept()
                        self.n_conn += 1
                        self.threadPool.execute_named(self._handle_connection,
                                        '%s _handle_connection %s' % (
                                                self.l.name, self.n_conn),
                                                con, addr, self.n_conn)
                return True
        def _handle_connection(self, con, addr, n_conn):
                l = logging.LoggerAdapter(self.l, {'sid': n_conn})
                l.info("Accepted connection from %s" % repr(addr))
                handler = self.create_handler(con, addr, l)
                with self.lock:
                        if not self.running:
                                return
                        self.handlers.add(handler)
                try:
                        handler.handle()
                except Exception:
                        self.l.exception("Uncaught exception")
                finally:
                        with self.lock:
                                self.handlers.remove(handler)
                        handler.cleanup()
        def stop(self):
                with self.lock:
                        assert self.running
                        self.running = False
                        handlers = list(self.handlers)
                for handler in handlers:
                        handler.interrupt()
                self.selectPool.deregister([self.socket])
                self.socket.close()

class UnixSocketServer(SocketServer):
        def create_listening_socket(self):
                if os.path.exists(self.socketPath):
                        os.unlink(self.socketPath)
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.bind(self.socketPath)
                s.listen(self.backlog)
                return s

class TCPSocketServer(SocketServer):
        def create_listening_socket(self):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.host, self.port))
                s.listen(self.backlog)
                return s
