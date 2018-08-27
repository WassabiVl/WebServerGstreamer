import time
import json
import tornado
from tornado import ioloop, web, websocket, options, httpserver
from tornado.options import define, options
import socket
from tornado.platform import asyncio
from tornado.httpclient import AsyncHTTPClient

from gStreamerservice import GStreamerWrapper

clients = dict()
Ip_collection = []
port_list = []
define("port", default=8888, help="run on the given port", type=int)
source_port = 5000
wrapper = GStreamerWrapper.GStreamerWrapper()


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class MainHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, error=None):
        wrapper.get_client()
        self.render("template.html", title="My title", items=(wrapper.get_client()), port=port_list, error=error)

    def post(self):
        global source_port
        try:
            socket.inet_aton(self.get_body_argument("message"))
        except socket.error:
            self.get('not an IP')
        wrapper.stop()
        wrapper.add_client(self.get_body_argument("message"), source_port)
        source_port += 1
        # wrapper.start_pipelines()
        self.get()

    def on_finish(self):
        wrapper.start_pipelines()


class PortHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        global source_port
        self.write(str(source_port))
        wrapper.stop()
        wrapper.add_client(self.request.remote_ip, source_port)
        source_port += 1

    def on_finish(self):
        wrapper.run_pipelines()


class deleteIP(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, *args):
        self.write(*args)
        wrapper.del_client(*args)
        self.redirect('/')

    def on_finish(self):
        # wrapper.start_pipelines()
        return MainHandler
        # self.write(self.request.uri)

    #    if self.request.remote_ip not in Ip_collection:


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/del/(.*)", deleteIP),
        (r"/get_port/?", PortHandler)
    ], debug=False)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    print("Starting GST thread...")

    # time.sleep(1)

    print("starting frame grabber thread")
    tornado.ioloop.IOLoop.current().start()
