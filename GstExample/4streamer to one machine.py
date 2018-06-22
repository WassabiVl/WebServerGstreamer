#!/usr/bin/python
import gi

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst, Gtk

GObject.threads_init()
Gst.init(None)


class Main:
    def __init__(self):
        def onPad(obj, pad, target):
            sinkpad = target.get_compatible_pad(pad, pad.get_caps())
            if sinkpad:
                pad.link(sinkpad)
            print("pad added")
            print(obj)
            return True

        self.pipeline = Gst.Pipeline("mypipeline")

        # video 1
        self.src1 = Gst.ElementFactory.make("videotestsrc", "source")
        self.src1.set_property("pattern", 0)
        self.decodebin1 = Gst.ElementFactory.make("decodebin", 'none')
        self.encoder1 = Gst.ElementFactory.make("x264enc")
        self.rtp_payload1 = Gst.ElementFactory.make("rtph264pay")
        self.rtpbin1 = Gst.ElementFactory.make('rtpbin', 'rtpbin')
        self.udpsink11 = Gst.ElementFactory.make("udpsink")
        self.udpsink11.set_property("host", "192.168.1.104")
        self.udpsink11.set_property("port", 5011)
        self.udpsink12 = Gst.ElementFactory.make("udpsink")
        self.udpsink12.set_property("host", "192.168.1.104")
        self.udpsink12.set_property("port", 5012)
        self.udpsrc1 = Gst.ElementFactory.make("udpsrc")
        self.udpsrc1.set_property("port", 5013)
        if not self.pipeline or not self.src1 or not self.decodebin1 or not self.encoder1 or not self.rtp_payload1 \
                or not self.rtpbin1 or not self.udpsink11 or not self.udpsink12 or not self.udpsrc1:
            print("One of the elements wasn't create... Exiting\n")
            exit(-1)
        self.pipeline.add(self.src1, self.decodebin1, self.encoder1, self.rtp_payload1, self.rtpbin1, self.udpsink11,
                          self.udpsink12, self.udpsrc1)


        # video 1 linking
        self.src1.link(self.decodebin1)
        self.decodebin1.connect("pad-added", onPad, self.encoder1)
        self.encoder1.link(self.rtp_payload1)
        self.rtp_payload1.link_pads('src', self.rtpbin1, 'send_rtp_sink_0')
        self.rtpbin1.link_pads('send_rtp_src_0', self.udpsink11, 'sink')
        self.rtpbin1.link_pads('send_rtcp_src_0', self.udpsink12, 'sink')
        self.udpsrc1.link_pads('src', self.rtpbin1, 'recv_rtcp_sink_0')

        # video 2
        self.src2 = Gst.ElementFactory.make("videotestsrc", "source")
        self.src2.set_property("pattern", 1)
        self.decodebin2 = Gst.ElementFactory.make("decodebin")
        self.encoder2 = Gst.ElementFactory.make("x264enc")
        self.rtp_payload2 = Gst.ElementFactory.make("rtph264pay")
        self.rtpbin2 = Gst.ElementFactory.make("rtpbin")
        self.udpsink21 = Gst.ElementFactory.make("udpsink")
        self.udpsink21.set_property("host", "192.168.1.104")
        self.udpsink21.set_property("port", 5021)
        self.udpsink22 = Gst.ElementFactory.make("udpsink")
        self.udpsink22.set_property("host", "192.168.1.104")
        self.udpsink22.set_property("port", 5022)
        self.udpsrc2 = Gst.ElementFactory.make("udpsrc")
        self.udpsrc2.set_property("port", 5023)
        self.pipeline.add(self.src2, self.decodebin2, self.encoder2, self.rtp_payload2, self.rtpbin2,
                          self.udpsink21, self.udpsink22, self.udpsrc2)

        # video 2 linking
        self.src2.link(self.decodebin2)
        self.decodebin2.connect("pad-added", onPad, self.encoder2)
        self.encoder2.link(self.rtp_payload2)
        self.rtp_payload2.link_pads('src', self.rtpbin2, 'send_rtp_sink_0')
        self.rtpbin2.link_pads('send_rtp_src_0', self.udpsink21, 'sink')
        self.rtpbin2.link_pads('send_rtcp_src_0', self.udpsink22, 'sink')
        self.udpsrc2.link_pads('src', self.rtpbin2, 'recv_rtcp_sink_0')

        # video 3
        self.src3 = Gst.ElementFactory.make("videotestsrc", "source")
        self.src3.set_property("pattern", 2)
        self.decodebin3 = Gst.ElementFactory.make("decodebin")
        self.encoder3 = Gst.ElementFactory.make("x264enc")
        self.rtp_payload3 = Gst.ElementFactory.make("rtph264pay")
        self.rtpbin3 = Gst.ElementFactory.make("Gstrtpbin")
        self.udpsink31 = Gst.ElementFactory.make("udpsink")
        self.udpsink31.set_property("host", "192.168.1.104")
        self.udpsink31.set_property("port", 5031)
        self.udpsink32 = Gst.ElementFactory.make("udpsink")
        self.udpsink32.set_property("host", "192.168.1.104")
        self.udpsink32.set_property("port", 5032)
        self.udpsrc3 = Gst.ElementFactory.make("udpsrc")
        self.udpsrc3.set_property("port", 5033)
        self.pipeline.add(self.src3, self.decodebin3, self.encoder3, self.rtp_payload3, self.rtpbin3, self.udpsink31, self.udpsink32, self.udpsrc3)

        # video 3 linking
        self.src3.link(self.decodebin3)
        self.decodebin3.connect("pad-added", onPad, self.encoder3)
        self.encoder3.link(self.rtp_payload3)
        self.rtp_payload3.link_pads('src', self.rtpbin3, 'send_rtp_sink_0')
        self.rtpbin3.link_pads('send_rtp_src_0', self.udpsink31, 'sink')
        self.rtpbin3.link_pads('send_rtcp_src_0', self.udpsink32, 'sink')
        self.udpsrc3.link_pads('src', self.rtpbin3, 'recv_rtcp_sink_0')

        # video 4
        self.src4 = Gst.ElementFactory.make("filesrc", "filesrc4")
        self.src4.set_property("location", "x104.avi")
        self.decodebin4 = Gst.ElementFactory.make("decodebin")
        self.encoder4 = Gst.ElementFactory.make("x264enc")
        self.rtp_payload4 = Gst.ElementFactory.make("rtph264pay")
        self.rtpbin4 = Gst.ElementFactory.make("Gstrtpbin")
        self.udpsink41 = Gst.ElementFactory.make("udpsink")
        self.udpsink41.set_property("host", "192.168.1.104")
        self.udpsink41.set_property("port", 5041)
        self.udpsink42 = Gst.ElementFactory.make("udpsink")
        self.udpsink42.set_property("host", "192.168.1.104")
        self.udpsink42.set_property("port", 5042)
        self.udpsrc4 = Gst.ElementFactory.make("udpsrc")
        self.udpsrc4.set_property("port", 5043)
        self.pipeline.add(self.src4, self.decodebin4, self.encoder4, self.rtp_payload4, self.rtpbin4, self.udpsink41,
                          self.udpsink42, self.udpsrc4)

        # video 4 linking
        self.src4.link(self.decodebin4)
        self.decodebin4.connect("pad-added", onPad, self.encoder4)
        self.encoder4.link(self.rtp_payload4)
        self.rtp_payload4.link_pads('src', self.rtpbin4, 'send_rtp_sink_0')
        self.rtpbin4.link_pads('send_rtp_src_0', self.udpsink41, 'sink')
        self.rtpbin4.link_pads('send_rtcp_src_0', self.udpsink42, 'sink')
        self.udpsrc4.link_pads('src', self.rtpbin4, 'recv_rtcp_sink_0')

        self.pipeline.set_state(Gst.State.PLAYING)


start = Main()
Gtk.main()
