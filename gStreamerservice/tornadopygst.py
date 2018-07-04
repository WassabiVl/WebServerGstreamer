import time
import json
import tornado
from tornado import ioloop, web, websocket, options, httpserver
from tornado.options import define, options
from tornado.platform import asyncio
from tornado.httpclient import AsyncHTTPClient

import GstremerSendRecive
import threading

clients = dict()
Ip_collection = []
define("port", default=8888, help="run on the given port", type=int)
source_port = 5000
gstreamerSendReceive = GstremerSendRecive.GstSendReceive()

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        gstreamerSendReceive.stop()
        self.write('<html><body><form action="/myform" method="POST">'
                   '<input type="text" name="message">'
                   '<input type="submit" value="Submit">'
                   '</form></body></html>')
        #if self.request.remote_ip not in Ip_collection:
        Ip_collection.append(self.request.remote_ip)

        #     gstreamerSendReceive = GstremerSendRecive.GstSendReceive(Ip_collection)
        #     pipeline = gstreamerSendReceive.main()
        #     gst_thread = threading.Thread(target=pipeline)
        #     gst_thread.start()

    def on_finish(self):
        t = gstreamerSendReceive.main(Ip_collection)
        a = t.__next__()
        while True:
            if a != t.__next__():
                t.__next__()
            break


class PortHandler(tornado.web.RequestHandler):
    def get(self):
        gstreamerSendReceive.stop()
        global source_port
        gstreamerSendReceive.add_port(source_port)
        result = source_port
        source_port += 1
        self.write(str(result))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/get_port/?", PortHandler)
        # (r"/", websocket),
        # (r"/", updserver2),
    ])


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    print("Starting GST thread...")

    # time.sleep(1)

    print("starting frame grabber thread")
    tornado.ioloop.IOLoop.current().start()