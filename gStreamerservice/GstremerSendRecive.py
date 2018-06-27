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
                print(i,key)
                #  video elements
                src = Gst.ElementFactory.make("udpsrc", "source" + key.__str__())
                src.set_property("port", 8880)
                caps = Gst.Caps("application/x-rtp, width=640, height=480, framerate=30/1")
                src.set_property("caps", caps)
                decodebin = Gst.ElementFactory.make("decodebin")
                encoder = Gst.ElementFactory.make("vp8enc")
                dencoder = Gst.ElementFactory.make("vp8dec")
                videoconvert = Gst.ElementFactory.make("videoconvert")
                rtp_payload = Gst.ElementFactory.make("rtpvp8depay")
                rtp_payload1 = Gst.ElementFactory.make("rtpvp8pay", 'rtpvp8pay'+ key.__str__())
                rtpbin = Gst.ElementFactory.make('rtpbin', 'rtpbin' + key.__str__())
                udpsink = Gst.ElementFactory.make("udpsink", 'sink' + key.__str__())
                udpsink.set_property("host", i)
                udpsink.set_property("port", 6000)
                udpsrc = Gst.ElementFactory.make("udpsrc")
                udpsrc.set_property("port", 5013)
                caps = Gst.Caps("application/x-rtp, width=640, height=480, framerate=30/1")
                udpsrc.set_property("caps", caps)
                sink = Gst.ElementFactory.make('autovideosink')

                if not self.pipeline or not src or not rtp_payload or not dencoder or not videoconvert \
                        or not decodebin or not encoder or not rtp_payload1 or not rtpbin or not udpsink or not sink:
                    print("One of the elements wasn't create... Exiting\n")
                    exit(-1)
                self.pipeline.add(src, rtp_payload, dencoder, videoconvert, decodebin, encoder, rtp_payload1, rtpbin,
                                  udpsink)
                # self.pipeline.add(src, rtp_payload, dencoder, videoconvert, decodebin, encoder, rtp_payload1, rtpbin,
                #                   sink)

                # video linking
                src.link(rtp_payload)
                rtp_payload.link(dencoder)
                dencoder.link(videoconvert)
                videoconvert.link(decodebin)
                decodebin.connect("pad-added", onPad, encoder)
                encoder.link(rtp_payload1)
                rtp_payload1.link_pads('src', rtpbin, 'send_rtp_sink_0')
                rtpbin.link_pads('send_rtp_src_0', udpsink, 'sink')
                # rtpbin.link_pads('send_rtp_src_0', sink, 'sink')

            ret = self.pipeline.set_state(Gst.State.PLAYING)
            if ret == Gst.StateChangeReturn.FAILURE:
                print("Unable to set the pipeline to the playing state.", file=sys.stderr)
                exit(-1)

            bus = self.pipeline.get_bus()

            # Parse message
            while True:
                message = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.STATE_CHANGED |
                                                 Gst.MessageType.ERROR | Gst.MessageType.EOS)
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
