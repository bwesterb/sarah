import json
import httplib
import threading

from mirte.core import Module

class CometClient(Module):
	def __init__(self, settings, l):
		super(CometClient, self).__init__(settings, l)
		self.cond_in = threading.Condition()
		self.cond_out = threading.Condition()
		self.running = False
		self.token = None
		self.queue_in = []
		self.queue_out = []
		self.nPending = 0
	def handle_message(self, m):
		raise NotImplemented
	def send_message(self, d):
		with self.cond_out:
			self.queue_out.insert(0, d)
			self.cond_out.notify()
	def run_dispatcher(self):
		while self.running:
			with self.cond_in:
				while self.queue_in:
					self.handle_message(self.queue_in.pop())
				self.cond_in.wait()
	def run_requester(self):
		while self.running:
			data = None
			with self.cond_out:
				if ((not self.queue_out or self.token is None)
						and self.nPending > 0):
					self.cond_out.wait()
					continue
				self.nPending += 1
				if self.queue_out:
					data = self.queue_out.pop()
			self._do_request(data)
			with self.cond_out:
				self.nPending -= 1
	def run(self):
		assert not self.running
		self.running = True
		self._do_request()
		self.threadPool.execute(self.run_dispatcher)
		self.threadPool.execute(self.run_requester)
		self.run_requester()
	def _do_request(self, data=None):
		conn = httplib.HTTPConnection(self.host, self.port)
		if data is None and not self.token is None:
			data = {}
		if not self.token is None:
			data['s'] = self.token
		method = 'GET' if data is None else 'POST'
		if not data is None:
			data = json.dumps(data)
		conn.request(method, self.path, data)
		resp = conn.getresponse()
		d = json.load(resp)
		with self.cond_out:
			old, self.token = self.token, d[0]
			if old is None:
				self.cond_out.notify()
		if len(d) == 1:
			return
		with self.cond_in:
			for m in d[1:]:
				self.queue_in.append(m)
			self.cond_in.notify()
	def stop(self):
		self.running = False
		with self.cond_in:
			self.cond_in.notifyAll()
		with self.cond_out:
			self.cond_out.notifyAll()
