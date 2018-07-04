import time
import tornado
from tornado import ioloop, web, websocket, options
from gStreamerservice import GstremerSendRecive
import threading

clients = dict()
Ip_collection = []
gstreamer = GstremerSendRecive


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        # self.write(repr(self.request))
        if self.request.remote_ip not in Ip_collection:
            Ip_collection.append(self.request.remote_ip)

        self.render("index.html")

    def on_finish(self):
        gstreamerSendReceive = GstremerSendRecive.GstSendReceive(Ip_collection)
        pipeline = gstreamerSendReceive.main()
        gst_thread = threading.Thread(target=pipeline)
        return gst_thread.start()


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def data_received(self, chunk):
        pass

    def open(self, *args):
        self.id = self.get_argument("Id")
        self.stream.set_nodelay(True)
        clients[self.id] = {"id": self.id, "object": self}

    def on_message(self, message):
        """
        when we receive some message we want some message handler..
        for this example i will just print message to console
        """
        print("Client %s received a message : %s" % (self.id, message))

    def on_close(self):
        if self.id in clients:
            del clients[self.id]


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/", websocket),
        # (r"/", updserver2),
    ], debug=True)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Starting GST thread...")

    time.sleep(1)

    print("starting frame grabber thread")
    tornado.ioloop.IOLoop.current().start()
