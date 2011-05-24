import select
import socket

class CappedReadFile(object):
        def __init__(self, f, cap, autoclose=False):
                self.f = f
                self.autoclose = autoclose
                self.left = cap
        def close(self):
                self.left = 0
                self.f.close()
        def read(self, n):
                if n <= self.left:
                        self.left -= n
                        if self.left == 0 and self.autoclose:
                                self.f.close()
                        return self.f.read(n)
                if self.left == 0:
                        return ''
                ret = self.f.read(self.left)
                self.left = 0
                if self.left == 0 and self.autoclose:
                        self.f.close()
                return ret

class BufferedFile(object):
        """ Wraps around a normal fileobject, buffering IO writes,
                @f      the file to wrap
                @n      the buffer size """
        def __init__(self, f, n=4096):
                self.f = f
                self.n = n
                # Maybe a cStringIO would be faster.  However <n> is still
                # pretty small in comparison.
                self.buf = ''
        
        def read(self, n=None):
                if n is None:
                        return self.f.read()
                return self.f.read(n)
        
        def write(self, s):
                if len(s) + len(self.buf) >= self.n:
                        self.f.write(self.buf + s)
                        self.buf = ''
                else:
                        self.buf += s
        
        def flush(self):
                self.f.write(self.buf)
                self.buf = ''
        
        def close(self):
                self.f.close()

class IntSocketFile(object):
        """ IntSocketFile(s) ~ s.makefile(), but has a nice
            interrupt function """
        # Yeah, the annoying branches are a bit dense in this code.
        def __init__(self, sock):
                self.socket = sock
                sock.setblocking(0)
                self._sleep_socket_pair = socket.socketpair()
                self.running = True
                self.read_buffer = ''
                self.closed = False
        def write(self, v):
                to_write = v
                while self.running and len(to_write) > 0:
                        rlist, wlist, xlist = select.select(
                                        [self._sleep_socket_pair[1]],
                                        [self.socket],
                                        [self.socket])
                        if (self._sleep_socket_pair[1] in rlist and
                            not self.running):
                                break
                        if self.socket in xlist:
                                raise IOError
                        if not self.socket in wlist:
                                continue
                        written = self.socket.send(to_write)
                        if written <= 0:
                                raise IOError
                        to_write = to_write[written:]
        def read(self, n):
                to_read = n
                ret = ''
                if len(self.read_buffer) > 0:
                        if len(self.read_buffer) >= n:
                                ret = self.read_buffer[:n]
                                self.read_buffer = self.read_buffer[n:]
                                return ret
                        ret = self.read_buffer
                        self.read_buffer = ''
                        to_read -= len(ret)
                while self.running and to_read > 0:
                        rlist, wlist, xlist = select.select(
                                        [self._sleep_socket_pair[1],
                                         self.socket], [],
                                        [self.socket])
                        if (self._sleep_socket_pair[1] in rlist and
                            not self.running):
                                break
                        if self.socket in xlist:
                                raise IOError
                        if not self.socket in rlist:
                                continue
                        tmp = self.socket.recv(min(2048, to_read))
                        if len(tmp) == 0:
                                raise IOError
                        ret += tmp
                        to_read -= len(tmp)
                return ret
        def readline(self, size=0):
                ret = ''
                to_read = size if size > 0 else None
                if to_read is None:
                        bit = self.read_buffer
                        self.read_buffer = ''
                else:
                        bit = self.read_buffer[:to_read]
                        self.read_buffer = self.read_buffer[to_read:]
                while self.running:
                        if not to_read is None:
                                to_read -= len(bit)
                        if not "\n" in bit:
                                ret += bit
                                if not to_read is None and to_read <= 0:
                                        return ret
                        else:
                                bit, rem = bit.split("\n", 1)
                                ret += bit + "\n"
                                self.read_buffer += rem
                                return ret
                        rlist, wlist, xlist = select.select(
                                        [self._sleep_socket_pair[1],
                                         self.socket], [],
                                        [self.socket])
                        if (self._sleep_socket_pair[1] in rlist and
                            not self.running):
                                break
                        if self.socket in xlist:
                                raise IOError
                        if not self.socket in rlist:
                                continue
                        buffer_size = min(1024, 1024 if to_read is None
                                                else to_read)
                        bit = self.socket.recv(buffer_size)
                        if len(bit) == 0:
                                raise IOError
                return ''
        def readsome(self, amount=2048):
                if len(self.read_buffer) != 0:
                        ret = self.read_buffer
                        self.read_buffer = ''
                        return self.read_bufffer
                rlist, wlist, xlist = select.select(
                                [self._sleep_socket_pair[1],
                                 self.socket], [],
                                [self.socket])
                if (self._sleep_socket_pair[1] in rlist and
                    not self.running):
                        return
                if self.socket in xlist:
                        raise IOError
                if not self.socket in rlist:
                        return
                return self.socket.recv(amount)

        def recv(self, amount=2048):
                return self.readsome(amount)
        def send(self, data):
                self.write(data)
                return len(data)
        def close(self):
                self.socket.close()
                self.closed = True
        def interrupt(self):
                self.running = False
                self._sleep_socket_pair[0].send('Good morning!')
        def flush(self):
                pass
        def makefile(self, mode=None, bufsize=None):
                return self

class SocketPairWrappedFile(object):
        """ Wraps around a file like object with a socket pair.  This gives
            any file() like object a fileno().  The current implementation
            is quite limited.  This object needs a worker thread.  Call run
            in a separate thread.  """
        def __init__(self, f):
                self.f = f
                self.sp = socket.socketpair()
        def fileno(self):
                return self.sp[1].fileno()
        def run(self):
                while True:
                        tmp = self.f.read(2048)
                        if tmp == '':
                                break
                        to_send = len(tmp)
                        while to_send > 0:
                                sent = self.sp[0].send(tmp)
                                tmp = tmp[sent:]
                                to_send -= sent
                self.sp[0].close()
        def close(self):
                self.sp[0].close()
                self.sp[1].close()


def pump(fin, fout):
        """ Reads data from <fin> and writes it to <fout> until EOF is
            reached. """
        while True:
                tmp = fin.read(4096)
                if not tmp:
                        break
                fout.write(tmp)
