import socket
import sys

import gi

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst
import _thread

DNS = '8.8.8.8'
source_port = 6000
sink_port = 5000
port_list = []
stop = False

class GstSendReceive:
    def __init__(self):
        Gst.init(None)
        self.GObject = None
        self.pipeline = None

    def add_source(self, first_element, port):
        src = Gst.ElementFactory.make("udpsrc", "source" + port.__str__())
        src.set_property("port", port)
        caps = Gst.Caps("application/x-rtp, width=640, height=480, framerate=30/1")
        src.set_property("caps", caps)
        src.set_property("buffer-size", 100000)
        jitter = Gst.ElementFactory.make('rtpjitterbuffer')
        rtp_depay = Gst.ElementFactory.make("rtpgstdepay")
        alpha = Gst.ElementFactory.make('alpha', 'alpha' + port.__str__())
        alpha.set_property('method', 'green')
        decoder = Gst.ElementFactory.make("jpegdec")

        if not src or not rtp_depay or not decoder or not jitter or not alpha:
            print("%s: %s elements wasn't create... Exiting\n")
            exit(-1)

        self.pipeline.add(src, jitter, rtp_depay, decoder, alpha)

        if first_element is not None:
            first_element.link(src)

        src.link(jitter)
        jitter.link(rtp_depay)
        rtp_depay.link(decoder)
        decoder.link(alpha)
        return alpha

    def add_dest(self, sink_ip):
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

        for key, i in enumerate(sink_ip):
            decodebin = Gst.ElementFactory.make("decodebin")
            rtp_payload1 = Gst.ElementFactory.make("rtpgstpay", 'rtpgstpay' + key.__str__())
            rtp_payload1.set_property('config-interval', 1)
            rtpbin = Gst.ElementFactory.make('rtpbin', 'rtpbin' + key.__str__())
            udpsink = Gst.ElementFactory.make("udpsink", 'sink' + key.__str__())
            udpsink.set_property("host", i)
            udpsink.set_property("port", 600)
            sink = Gst.ElementFactory.make('autovideosink')
            encoder = Gst.ElementFactory.make("jpegenc")

            if not rtp_payload1 or not rtpbin or not udpsink or not sink or not decodebin or not encoder:
                print("%s: %s elements wasn't create... Exiting\n")
                exit(-1)
            self.pipeline.add(rtp_payload1, rtpbin, udpsink, decodebin, encoder)
            # self.pipeline.add(src, rtp_payload, dencoder, videoconvert, decodebin, encoder, rtp_payload1, rtpbin,
            #                   sink)

            # video linking
            #videoconvert.link(decodebin)
            decodebin.connect("pad-added", onPad, encoder)
            encoder.link(rtp_payload1)
            rtp_payload1.link_pads('src', rtpbin, 'send_rtp_sink_0')
            rtpbin.link_pads('send_rtp_src_0', udpsink, 'sink')
            # rtpbin.link_pads('send_rtp_src_0', sink, 'sink')

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
            self.pipeline = Gst.Pipeline("mypipeline")
            last_element = None;

            for key, i in enumerate(port_list):
                print(key, i)
                #  video elements
                last_element = self.add_source(last_element, i);

            mixer = Gst.ElementFactory.make("videomixer", "mixer")
            videoconvert = Gst.ElementFactory.make("videoconvert")
            test_sink = Gst.ElementFactory.make("autovideosink")

            if not self.pipeline or not mixer or not videoconvert:
                print('Pipeline or mixer or mixer not created')
                exit(-1)

           # self.pipeline.add(mixer, videoconvert)
            self.pipeline.add(mixer, videoconvert, test_sink)
            last_element.link(mixer)
            mixer.link(videoconvert)
            videoconvert.link(test_sink)

            #self.add_dest(sink_ip)

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
        self.pipeline = None

    def add_port(self, port):
        port_list.append(port);