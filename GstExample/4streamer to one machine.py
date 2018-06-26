#!/usr/bin/python
import sys
import gi
import socket

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst, Gtk

GObject.threads_init()
Gst.init(None)

DNS = '8.8.8.8'
source_port = 6000
sink_port = 5000


class Main:
    def __init__(self):
        def onPad(obj, pad, target):
            """

            :param obj: GstDecodeBin
            :param target: GstX264Enc
            :type pad: GstDecodePad
            """
            print("Received new pad '%s' from '%s':" % (pad.get_name(), obj.get_name()))
            if pad.is_linked():
                print("We are already linked. Ignoring.")
                return True
            ret = pad.link(target.get_static_pad("sink"))
            return True

        self.pipeline = Gst.Pipeline("mypipeline")

        for key, i in enumerate(range(3)):
            #  video elements
            self.src = Gst.ElementFactory.make("videotestsrc", "source" + i.__str__())
            self.src.set_property("pattern", i)
            self.decodebin = Gst.ElementFactory.make("decodebin")
            self.encoder = Gst.ElementFactory.make("x264enc")
            self.rtp_payload = Gst.ElementFactory.make("rtph264pay")
            self.rtpbin = Gst.ElementFactory.make('rtpbin', 'rtpbin' + i.__str__())
            self.udpsink = Gst.ElementFactory.make("udpsink")
            self.udpsink.set_property("host", "127.0.0.1")
            self.udpsink.set_property("port", 5011)
            self.udpsrc = Gst.ElementFactory.make("udpsrc")
            self.udpsrc.set_property("port", 5013)
            print(self.get_ip(5043))
            caps = Gst.Caps("application/x-rtp, width=640, height=480, framerate=20/1")
            self.udpsrc.set_property("caps", caps)

            if not self.pipeline or not self.src or not self.decodebin or not self.encoder or not self.rtp_payload \
                    or not self.rtpbin or not self.udpsink or not self.udpsrc:
                print("One of the elements wasn't create... Exiting\n")
                exit(-1)
            self.pipeline.add(self.src, self.decodebin, self.encoder, self.rtp_payload, self.rtpbin, self.udpsink,
                              self.udpsrc)

            # video linking
            self.src.link(self.decodebin)
            self.decodebin.connect("pad-added", onPad, self.encoder)
            self.encoder.link(self.rtp_payload)
            self.rtp_payload.link_pads('src', self.rtpbin, 'send_rtp_sink_0')
            self.rtpbin.link_pads('send_rtp_src_0', self.udpsink, 'sink')
            self.udpsrc.link_pads('src', self.rtpbin, 'recv_rtcp_sink_0')

        ret = self.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            print("Unable to set the pipeline to the playing state.", file=sys.stderr)
            exit(-1)

        bus = self.pipeline.get_bus()

        # Parse message
        while True:
            message = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE,
                                             Gst.MessageType.STATE_CHANGED | Gst.MessageType.ERROR | Gst.MessageType.EOS)
            if message.type == Gst.MessageType.ERROR:
                err, debug = message.parse_error()
                print("Error received from element %s: %s" % (
                    message.src.get_name(), err), file=sys.stderr)
                print("Debugging information: %s" % debug, file=sys.stderr)
                break
            elif message.type == Gst.MessageType.EOS:
                print("End-Of-Stream reached.")
                break
            elif message.type == Gst.MessageType.STATE_CHANGED:
                if isinstance(message.src, Gst.Pipeline):
                    old_state, new_state, pending_state = message.parse_state_changed()
                    print("Pipeline state changed from %s to %s." %
                          (old_state.value_nick, new_state.value_nick))
            else:
                print("Unexpected message received.", file=sys.stderr)
        # Free resources
        self.pipeline.set_state(Gst.State.NULL)

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


start = Main()
Gtk.main()
