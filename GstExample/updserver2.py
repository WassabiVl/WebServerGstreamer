import logging
import time
import tornado
from tornado import ioloop, gen
import socket
from tornado.ioloop import IOLoop


# From Kyle Grahel - http://kyle.graehl.org/
# The __enter__ and __exit__ are added by me.. probably not the best way to use
# these though..


class UDPStream(object):
    def __init__(self, socket, in_ioloop=None):
        self.socket = socket
        self._state = None
        self._read_callback = None
        self.ioloop = in_ioloop or IOLoop.instance()
        self._read_timeout = None

    def _add_io_state(self, state):
        if self._state is None:
            self._state = tornado.ioloop.IOLoop.ERROR | state
            self.ioloop.add_handler(
                self.socket.fileno(), self._handle_events, self._state)
        elif not self._state & state:
            self._state = self._state | state
            self.ioloop.update_handler(self.socket.fileno(), self._state)

    def send(self, msg):
        return self.socket.send(msg)

    def recv(self, sz):
        return self.socket.recv(sz)

    def close(self):
        self.ioloop.remove_handler(self.socket.fileno())
        self.socket.close()
        self.socket = None

    def read_chunk(self, callback=None, timeout=4):
        self._read_callback = callback
        self._read_timeout = self.ioloop.add_timeout(time.time() + timeout,
                                                     self.check_read_callback)
        self._add_io_state(self.ioloop.READ)
        yield gen.Task(s.read_chunk)

    def check_read_callback(self):
        if self._read_callback:
            # XXX close socket?
            self._read_callback(None, error='timeout')

    def _handle_read(self):
        if self._read_timeout:
            self.ioloop.remove_timeout(self._read_timeout)
        if self._read_callback:
            try:
                data = self.socket.recv(4096)
            except:
                # conn refused??
                data = None
            self._read_callback(data)
            self._read_callback = None

    def _handle_events(self, fd, events):
        if events & self.ioloop.READ:
            self._handle_read()
        if events & self.ioloop.ERROR:
            logging.error('%s event error' % self)


if __name__ == "__main__":
    udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpsock.setblocking(False)
    udpsock.connect(('tracker.openbittorrent.com', 80))
    s = UDPStream(udpsock)
    s.send('some data')
    # data = yield gen.Task( s.read_chunk )
