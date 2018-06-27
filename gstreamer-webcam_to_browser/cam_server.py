import threading
import time
import signal
import gi
import tornado
from tornado import web, websocket, httpserver, ioloop, options
from tornado.options import options

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, Gtk

cam_sockets = []
key_sockets = []
clients = dict()
Ip_collection = []

frame_grabber = None

DEAD_ZONE = 10
FORWARD_SPEED = 75.0
TURN_SPEED = 50.0
FORWARD = 1
BACKWARD = -1
LEFT = 0
RIGHT = 1


def send_all(msg):
    for ws in cam_sockets:
        ws.write_message(msg, True)


class CamWSHandler(tornado.websocket.WebSocketHandler):
    def data_received(self, chunk):
        pass

    def open(self):
        global cam_sockets
        cam_sockets.append(self)
        print('new camera connection')

    def on_message(self, message):
        print(message)

    def on_close(self):
        global cam_sockets
        cam_sockets.remove(self)
        print('camera connection closed')

    def check_origin(self, origin):
        return True


class KeyWSHandler(tornado.websocket.WebSocketHandler):
    def data_received(self, chunk):
        pass

    def open(self):
        global key_sockets
        key_sockets.append(self)
        print('new command connection')

    def on_message(self, message):
        pass
        # print(message)

    def on_close(self):
        global key_sockets
        key_sockets.remove(self)
        print('command connection closed')

    def check_origin(self, origin):
        return True


class HTTPServer(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")


class MainPipeline:
    def __init__(self):
        self.pipeline = None
        self.videosrc = None
        self.videoparse = None
        self.videosink = None
        self.current_buffer = None

    def pull_frame(self, sink):
        # second param appears to be the sink itself
        sample = self.videosink.emit("pull-sample")
        if sample is not None:
            self.current_buffer = sample.get_buffer()
            current_data = self.current_buffer.extract_dup(0, self.current_buffer.get_size())
            send_all(current_data)
        return False

    def gst_thread(self):
        print("Initializing GST Elements")
        Gst.init(None)

        self.pipeline = Gst.Pipeline.new("framegrabber")

        # instantiate the camera source
        self.videosrc = Gst.ElementFactory.make("videotestsrc", "vid-src")
        self.videosrc.set_property("pattern", 0)

        # instantiate the jpeg parser to ensure whole frames
        self.videoparse = Gst.ElementFactory.make("videoparse", "vid-parse")

        # instantiate the appsink - allows access to raw frame data
        self.videosink = Gst.ElementFactory.make("appsink", "vid-sink")
        self.videosink.set_property("max-buffers", 3)
        self.videosink.set_property("drop", True)
        self.videosink.set_property("emit-signals", True)
        self.videosink.set_property("sync", False)
        self.videosink.connect("new-sample", self.pull_frame)
        # add all the new elements to the pipeline
        print("Adding Elements to Pipeline")
        self.pipeline.add(self.videosrc)
        self.pipeline.add(self.videoparse)
        self.pipeline.add(self.videosink)

        # link the elements in order, adding a filter to ensure correct size and framerate
        print("Linking GST Elements")
        self.videosrc.link_filtered(self.videoparse,
                                    Gst.caps_from_string('image/jpeg,width=640,height=480,framerate=30/1'))
        self.videoparse.link(self.videosink)

        # start the video
        print("Setting Pipeline State")
        self.pipeline.set_state(Gst.State.PAUSED)
        self.pipeline.set_state(Gst.State.PLAYING)


def start_server(cam_app, key_app):
    cam_server = tornado.httpserver.HTTPServer(cam_app)
    key_server = tornado.httpserver.HTTPServer(key_app)
    cam_app.listen(8888)
    key_app.listen(8889)
    tornado.ioloop.IOLoop.current().start()


def signal_handler(signum, frame):
    print("Interrupt caught")
    tornado.ioloop.IOLoop.instance().stop()
    server_thread.stop()


def make_app():
    return tornado.web.Application([
        (r"/", HTTPServer),
        (r"/ws", CamWSHandler),
        # (r"/", updserver2),
    ], debug=True)


def make_app1():
    return tornado.web.Application([
        (r'/ws', KeyWSHandler)
    ], debug=True)


if __name__ == "__main__":

    cam_app = make_app()
    key_app = make_app1()

    print("Starting GST thread...")

    pipeline = MainPipeline()
    gst_thread = threading.Thread(target=pipeline.gst_thread)
    gst_thread.start()

    time.sleep(1)

    print("starting frame grabber thread")

    print("Starting server thread")
    cam_server = tornado.httpserver.HTTPServer(cam_app)
    key_server = tornado.httpserver.HTTPServer(key_app)
    cam_server.listen(8888)
    key_server.listen(8889)
    tornado.ioloop.IOLoop.current().start()
    # server_thread = threading.Thread(target=start_server, args=[cam_app, key_app])
    # server_thread.start()

    # or you can use a custom handler,
    # in which case recv will fail with EINTR
    print("registering sigint")
    signal.signal(signal.SIGINT, signal_handler)

    try:
        print("gst_thread_join")
        gst_thread.join()
        print("Pausing so that thread doesn't exit")
        while 1:
            time.sleep(1)
    except:
        print("exiting")
        exit(0)
