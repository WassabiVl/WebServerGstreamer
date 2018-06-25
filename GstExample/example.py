import gi

gi.require_version("Gst", "1.0")
gi.require_version("Gtk", "3.0")
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GObject, Gtk


class Main:
    def __init__(self):
        GObject.threads_init()
        Gst.init(None)
        self.pipeline = Gst.Pipeline("mypipeline")

        self.audiotestsrc = Gst.ElementFactory.make("audiotestsrc", "audio")
        self.pipeline.add(self.audiotestsrc)

        self.sink = Gst.ElementFactory.make("autovideosink", "sink")
        self.pipeline.add(self.sink)

        self.audiotestsrc.link(self.sink)

        self.pipeline.set_state(Gst.State.PLAYING)
        pipeline = 'udpsrc port=5000  ! rtpvp8depay ! vp8dec ! alpha method=green ! mixer.sink_0 udpsrc port=5001 ' \
                   'caps="application/x-rtp" ! rtpvp8depay ! vp8dec ! alpha method=green target-r=0 ' \
                   'target-b=0 target-g=0 black-sensitivity=128 white-sensitivity=0 ! mixer.sink_1 udpsrc port=5002 ' \
                   'caps="application/x-rtp" ! rtpvp8depay ! vp8dec ! alpha method=custom target-r=0 target-b=0 ' \
                   'target-g	=0 black-sensitivity=128 white-sensitivity=0 ! mixer.sink_2 videomixer ' \
                   'name=mixer sink_0::zorder=2 sink_1::zorder=1 sink_2::zorder=2 ! videoconvert ! autovideosink'
        self.pipeline = Gst.parse_launch(pipeline)
        print(self.pipeline.get_by_name("mixer"))


start = Main()
Gtk.main()
