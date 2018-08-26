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
clients = {}


class GStreamerWrapper:
    def __init__(self):
        Gst.init(None)
        self.GObject = None
        self.pipeline_list = []

    def add_source(self, port, pipeline_string):
        if pipeline_string != "":
            pipeline_string += " "

        pipeline_string += "udpsrc port=" + str(
            port) + ' caps=\"application/x-rtp,media=video,clock-rate=90000,encoding-name=H264,width=640,height=480,framerate=60/1\" ! rtpjitterbuffer drop-on-latency=false latency=500 ! rtph264depay ! queue ! h264parse ! queue ! avdec_h264 ! queue ! alpha method=green ! videoconvert ! mixer.sink_' + str(
            port)

        return pipeline_string

    def check_bus(self):
        global stop

        while stop == False:
            for pipeline in self.pipeline_list:
                pipeline.set_state(Gst.State.NULL)
                bus = pipeline.get_bus()
                message = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE,
                                                 Gst.MessageType.STATE_CHANGED | Gst.MessageType.ERROR | Gst.MessageType.EOS)

                if message.type == Gst.MessageType.ERROR:
                    err, debug = message.parse_error()
                    print("Error received from element %s: %s" % (message.src.get_name(), err), file=sys.stderr)
                    print("Debugging information: %s" % debug, file=sys.stderr)
                    self.stop()
                    break
                elif message.type == Gst.MessageType.EOS:
                    print("End-Of-Stream reached.")
                    break
                elif message.type == Gst.MessageType.STATE_CHANGED:
                    if isinstance(message.src, Gst.Pipeline):
                        old_state, new_state, pending_state = message.parse_state_changed()
                        print("Pipeline state changed from %s to %s." % (old_state.value_nick, new_state.value_nick))

                        if new_state.value_nick == "playing":
                            break
                else:
                    print("Unexpected message received.", file=sys.stderr)

    def add_client(self, ip, port):
        try:
            global clients
            clients[ip] = port;
        except Exception as e:
            print(e)

    def get_client(self):
        return clients.items()

    def del_client(self,ip):
        del clients[ip]

    def stop(self):
        try:
            global stop
            stop = True

            for pipeline in self.pipeline_list:
                pipeline.set_state(Gst.State.NULL)

            Gst.init(None)
            self.GObject = None
            self.pipeline_list.clear();
        except Exception as e:
            print(e)

    def start_pipelines(self):
        try:
            # only start if there are more than 1 clients
            global clients

            if len(clients.items()) > 1:
                Gst.init(None)
                self.GObject = GObject.threads_init()

                for ip_dest, port_dest in clients.items():
                    print(ip_dest, port_dest)
                    pipeline_string = "";

                    for ip_source, port_source in clients.items():
                        if (ip_dest != ip_source):
                            pipeline_string = self.add_source(port_source, pipeline_string)

                    pipeline_string += " videomixer name=mixer background=white ! queue ! videoconvert ! x264enc bitrate=1000 speed-preset=superfast tune=zerolatency " +\
                                       "! queue ! rtph264pay config-interval=1 ! queue ! udpsink host=" + ip_dest + " port=6000"
                    print(pipeline_string + "\n")
                    pipeline = Gst.parse_launch(pipeline_string)
                    self.pipeline_list.append(pipeline)
                    ret = pipeline.set_state(Gst.State.PLAYING)

                    if ret == Gst.StateChangeReturn.FAILURE:
                        print("Unable to set the pipeline to playing state.", file=sys.stderr)
                        self.stop();
                        exit(-1)

                self.check_bus()
        except Exception as e:
            print(e)

    def start_pipelines(self):
        Gst.init(None)
        self.GObject = GObject.threads_init()

        for ip_dest, port_dest in clients.items():
            print(ip_dest, port_dest)
            pipeline_string = ""

            for ip_source, port_source in clients.items():
                if (ip_dest != ip_source):
                    self.add_source(ip_source, pipeline_string)

            pipeline_string += " videomixer name=mixer background=white ! queue ! videoconvert ! x264enc bitrate=1000 speed-preset=superfast tune=zerolatency " + \
                               "! queue ! rtph264pay config-interval=1 ! queue ! udpsink host=" + ip_dest + " port=6000"
            print(pipeline_string + "\n")
            pipeline = Gst.parse_launch(pipeline_string)
            ret = pipeline.set_state(Gst.State.PLAYING)

            if ret == Gst.StateChangeReturn.FAILURE:
                print("Unable to set the pipeline to playing state.", file=sys.stderr)
                self.stop()
                exit(-1)

        self.check_bus()
