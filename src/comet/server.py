from mirte.core import Module
from sarah.event import Event
from sarah.io import IntSocketFile
from sarah.socketServer import TCPSocketServer

import cStringIO
import threading
import urlparse
import os.path
import logging
import socket
import base64
import urllib
import json
import time
import os

from cStringIO import StringIO
from BaseHTTPServer import BaseHTTPRequestHandler

class CometRHWrapper(object):
	""" Exposes SocketServer handler semantics for our
	    BaseHTTPRequestHandler based CometRH """
	def __init__(self, request, addr, server, l):
		self.request = IntSocketFile(request)
		self.addr = addr
		self.server = server
		self.l = l
	def handle(self):
		self.h = CometRH(self.request, self.addr,
					self.server, self.l)
	def interrupt(self):
		self.request.interrupt()
	def cleanup(self):
		pass

class CometRH(BaseHTTPRequestHandler):
	def __init__(self, request, addr, server, l):
		self.l = l
		self.server = server
		BaseHTTPRequestHandler.__init__(self, request, addr, server)
	def log_message(self, format, *args, **kwargs):
		self.l.info(format, *args, **kwargs)
	def log_error(self, format, *args, **kwargs):
		self.l.error(format, *args, **kwargs)
	def log_request(self, code=None, size=None):
		self.l.info("Request: %s %s" % (code, size))
	def do_GET(self):
		v = urllib.unquote(urlparse.urlparse(self.path).query)
		self._dispatch_request(v)
	def do_POST(self):
		if not 'Content-Length' in self.headers:
			self._respond_simple(400, "No Content-Length")
		self._dispatch_request(self.rfile.read(
			int(self.headers['Content-Length'])))
	def _dispatch_request(self, v):
		if v == '':
			d = None
		else:
			try:
				d = json.loads(v)
			except ValueError:
				self._respond_simple(400, 'Malformed JSON')
				return
		self.server.dispatch_message(d, self)
	def _respond_simple(self, code, message):
		self.send_response(code)
		self.end_headers()
		self.wfile.write(message)
		self.real_finish()	
	def real_finish(self):
		BaseHTTPRequestHandler.finish(self)
	def finish(self):
		# We don't want our parent to close our wfile and rfile.
		pass

class BaseCometSession(object):
	def __init__(self, server, token):
		self.l = logging.getLogger('%s.%s' % (server.l.name, token)) 
		self.server = server
		self.lock = threading.Lock()
		self.rh = None
		self.token = token
		self.timeout = None
		self.messages = []
	def send_message(self, data):
		self.l.debug("> %s" % data)
		with self.lock:
			self.messages.append(data)
			if not self.rh is None:
				self.__flush()
	def _set_timeout(self, timeout):
		if not timeout == self.timeout:
			if not self.timeout is None:
				self.server.remove_timeout(self.timeout, self)
			self.server.add_timeout(timeout, self)
			self.timeout = timeout
	def _handle_message(self, rh, data, direct_return):
		self.l.debug("< %s" % data)
		with self.lock:
			if not self.rh is None:
				self.__flush()
			else:
				self._set_timeout(int(time.time() +
						self.server.timeout))
			self.rh = rh
			if direct_return:
				self.__flush()
		if len(data) > 1:
			self.handle_message(data)
	def handle_message(self, data):
		pass
	def on_timeout(self, timeout):
		with self.lock:
			if timeout != self.timeout:
				return
			if self.rh is None:
				self.server.remove_session(self.token)
			else:
				self.__flush()
	def flush(self):
		with self.lock:
			if not self.rh is None:
				self.__flush()
	def __flush(self):
		""" Flushes messages through current HttpRequest and closes it.
		    It assumes a current requesthandler and requires a lock
		    on self.lock """
		rh = self.rh
		messages = list(self.messages)
		self.messages = []
		self.server.threadPool.execute(self.__inner_flush, rh, messages)
		self.rh = None
		self._set_timeout(int(time.time() + self.server.timeout))
	def __inner_flush(self, rh, messages):
		try:
			rh.send_response(200)
			rh.end_headers()
			json.dump([self.token] + messages, rh.wfile)
			rh.real_finish()
		except socket.error:
			self.l.exception("Exception while flushing")

class CometServer(TCPSocketServer):
	def __init__(self, settings, logger, session_class):
		self.sessions = {}
		self.lock = threading.Lock()
		self.timeout_lut = dict()
		self.session_class = session_class
		super(CometServer, self).__init__(settings, logger)
	def send_message(self, d):
		with self.lock:
			for s in self.sessions.itervalues():
				s.send_message(d)
	def create_token(self):
		while True:
			_try = base64.b64encode(os.urandom(6))
			with self.lock:
				if not _try in self.sessions:
					self.sessions[_try] = None
					return _try
	def dispatch_message(self, d, rh):
		direct_return = False
		if d is None:
			direct_return = True
			d = {}
		if not isinstance(d, dict):
			rh._respond_simple(400, 'Message isn\'t dict')
			return
		if not 's' in d:
			d['s'] = self.create_token()
		with self.lock:
			if not d['s'] in self.sessions or \
					self.sessions[d['s']] is None:
				self.sessions[d['s']] = \
					self.session_class(self, d['s'])
		self.sessions[d['s']]._handle_message(rh, d, direct_return)

	def create_handler(self, con, addr, logger):
		return CometRHWrapper(con, addr, self, logger)
	def remove_timeout(self, timeout, session):
		with self.lock:
			if timeout in self.timeout_lut:
				self.timeout_lut[timeout].remove(session)
	def add_timeout(self, timeout, session):
		with self.lock:
			if not timeout in self.timeout_lut:
				self.timeout_lut[timeout] = set()
			self.timeout_lut[timeout].add(session)
	def remove_session(self, token):
		with self.lock:
			self.l.info("Session %s timed out" % token)
			del self.sessions[token]
	def run(self):
		super(CometServer, self).run()
		while True:
			with self.lock:
				ds = self.timeout_lut.items()
			tmp = sorted([x[0] for x in ds if x[1]])
			timeout = tmp[0] - time.time() if tmp else self.timeout
			if timeout > 0:
				time.sleep(timeout)
			with self.lock:
				ds = self.timeout_lut.items()
			ds.sort(cmp=lambda x,y: cmp(x[0], y[0]))
			now = time.time()
			for t, ss in ds:
				if t >= now:
					break
				del self.timeout_lut[t]
				for s in ss:
					s.on_timeout(t)
			if not self.running:
				break

