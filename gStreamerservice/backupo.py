import socket
import sys

import gi

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst

DNS = '8.8.8.8'
source_port = 6000
sink_port = 5000


class GstSendReceive:
    def __init__(self, sink_ip=None):
        self.GObject = GObject.threads_init()
        self.sink_ip = [] if sink_ip is None else sink_ip
        self.pipeline = None

    def main(self):
        Gst.init(None)

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
            pad.link(target.get_static_pad("sink"))
            return True

        self.pipeline = Gst.Pipeline("mypipeline")
        if self.sink_ip:
            for key, i in enumerate(self.sink_ip):
                #  video elements
                src = Gst.ElementFactory.make("udpsrc", "source" + key.__str__())
                src.set_property("port", 8880)
                # caps = Gst.Caps("application/x-rtp")
                # src.set_property("caps", caps)
                rtp_payload = Gst.ElementFactory.make("rtph264pay")
                rtpbin = Gst.ElementFactory.make('rtpbin', 'rtpbin' + key.__str__())
                decoder = Gst.ElementFactory.make('vp8dec')
                videoConvert = Gst.ElementFactory.make('videoconvert')
                decodebin = Gst.ElementFactory.make("decodebin")
                encoder = Gst.ElementFactory.make("vp8dec")
                udpsink = Gst.ElementFactory.make("udpsink", "sink" + key.__str__())
                udpsink.set_property("host", i)
                udpsink.set_property("port", 6000)
                udpsrc = Gst.ElementFactory.make("udpsrc")
                udpsrc.set_property("port", 6001)
                # print(self.get_ip(8880))
                caps = Gst.Caps("application/x-rtp, width=640, height=480, framerate=20/1")
                udpsrc.set_property("caps", caps)

                if not self.pipeline or not src or not videoConvert or not rtpbin or not udpsink or not udpsrc:
                    print("One of the elements wasn't create... Exiting\n")
                    exit(-1)
                self.pipeline.add(src, decodebin, encoder, rtp_payload, rtpbin, udpsink, udpsrc)

                # video linking
                # video linking
                src.link(decodebin)
                decodebin.connect("pad-added", onPad, encoder)
                encoder.link(rtp_payload)
                rtp_payload.link_pads('src', rtpbin, 'send_rtp_sink_0')
                rtpbin.link_pads('send_rtp_src_0', udpsink, 'sink')
                udpsrc.link_pads('src', rtpbin, 'recv_rtcp_sink_0')

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
