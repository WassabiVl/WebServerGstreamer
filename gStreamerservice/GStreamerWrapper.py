import socket
import sys

import gi

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst
import _thread

DNS = '8.8.8.8'
port_list = []
stop = False

class GStreamerWrapper:
    def __init__(self):
        Gst.init(None)
        self.GObject = None
        self.pipeline = None
        self.pipeline_string = ""

    def add_source(self, port):
        if self.pipeline_string != "":
            self.pipeline_string += " "

        self.pipeline_string += "udpsrc port=" + str(port) + " caps=\"application/x-rtp, width=640, height=480, framerate=30/1\" buffer-size=100000 ! rtpjitterbuffer ! rtpgstdepay ! jpegdec ! alpha method=green ! mixer.sink_" + str(port)

    def add_dest(self, sink_ip):
        self.pipeline_string += "jpegenc ! rtpgstpay config-interval=1 ! multiudpsink clients="
        client_list = ""

        for key, i in enumerate(sink_ip):
            if client_list != "":
                client_list += ","

            client_list += str(i) + ":6000"

        self.pipeline_string += client_list

    def check_bus(self):
        global stop
        bus = self.pipeline.get_bus()

        while stop == False:
            message = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.STATE_CHANGED | Gst.MessageType.ERROR | Gst.MessageType.EOS)

            if message.type == Gst.MessageType.ERROR:
                err, debug = message.parse_error()
                print("Error received from element %s: %s" % (message.src.get_name(), err), file=sys.stderr)
                print("Debugging information: %s" % debug, file=sys.stderr)
                break
            elif message.type == Gst.MessageType.EOS:
                print("End-Of-Stream reached.")
                break
            elif message.type == Gst.MessageType.STATE_CHANGED:
                if isinstance(message.src, Gst.Pipeline):
                    old_state, new_state, pending_state = message.parse_state_changed()
                    print("Pipeline state changed from %s to %s." % (old_state.value_nick, new_state.value_nick))

                    if (new_state.value_nick == 'playing'):
                        break
            else:
                print("Unexpected message received.", file=sys.stderr)

    def main(self, sink_ip=None):
        Gst.init(None)
        self.GObject = GObject.threads_init()

        if sink_ip:
            for key, i in enumerate(port_list):
                print(key, i)
                #  video elements
                self.add_source(i);

            self.pipeline_string += " videomixer name=mixer ! videoconvert ! "
            self.add_dest(sink_ip)
            print(self.pipeline_string)
            self.pipeline = Gst.parse_launch(self.pipeline_string)
            ret = self.pipeline.set_state(Gst.State.PLAYING)

            if ret == Gst.StateChangeReturn.FAILURE:
                print("Unable to set the pipeline to the playing state.", file=sys.stderr)
                exit(-1)

            self.check_bus()

    def get_ip(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect((DNS, port))
            client = s.getsockname()[0]
        except socket.error:
            client = "Unknown IP"
        finally:
            del s
        return client

    def stop(self):
        global stop
        stop = True;

        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)

        Gst.init(None)
        self.GObject = None
        self.pipeline_string = ""
        self.pipeline = None

    def add_port(self, port):
        port_list.append(port);