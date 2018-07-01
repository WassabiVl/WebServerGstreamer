import gi

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst, Gtk

'''
Gst-launch -e videomixer name=mix \
sink_0::xpos=0 sink_0::ypos=0 sink_0::alpha=0 \
sink_1::xpos=100 sink_1::ypos=50 \
! xvimagesink \
videotestsrc \
! video/x-raw-yuv,width=600,height=200 \
! mix.sink_0 \
videotestsrc pattern=0 \
! video/x-raw-yuv,width=100,height=100 \
! mix.sink_1 
'''


class Main:
    def __init__(self):
        Gst.init(None)
        self.pipeline = Gst.Pipeline("mypipeline")

        # self.videotestsrc = Gst.ElementFactory.make("videotestsrc", "videoin")

        source = Gst.ElementFactory.make("videotestsrc", "video-source-bg")
        source1 = Gst.ElementFactory.make("videotestsrc", "video-source1")
        source1.set_property("pattern", 0)
        source2 = Gst.ElementFactory.make("videotestsrc", "video-source2")
        source2.set_property("pattern", 4)

        sink = Gst.ElementFactory.make("xvimagesink", "video-output")
        caps_bg = Gst.Caps("video/x-raw, width=600, height=200")
        filter = Gst.ElementFactory.make("capsfilter", "filter-bg")
        filter.set_property("caps", caps_bg)
        # filter_src_pad = filter.get_pad("src")

        caps1 = Gst.Caps("video/x-raw, width=100, height=100")
        filter1 = Gst.ElementFactory.make("capsfilter", "filter1")
        filter1.set_property("caps", caps1)
        # filter1_src_pad = filter1.get_pad("src")

        caps2 = Gst.Caps("video/x-raw, width=100, height=100")
        filter2 = Gst.ElementFactory.make("capsfilter", "filter2")
        filter2.set_property("caps", caps2)
        # filter2_src_pad = filter2.get_pad("src")

        mixer = Gst.ElementFactory.make("videomixer", "mixer")
        # mixer.set_property("background",3)
        if not mixer:
            print("mixer wasn't create... Exiting\n")
            exit(-1)
        # self.bin = Gst.Bin("my-bin")
        pad0 = Gst.Element.get_static_pad(source, "src")
        if not pad0:
            print("pad0 wasn't create... Exiting\n")
            exit(-1)
        pad0_template = mixer.get_pad_template("sink_%u")
        if not pad0_template:
            print("pad0_template wasn't create... Exiting\n")
            exit(-1)
        mixer_pad0 = Gst.Element.request_pad(mixer, pad0_template)
        if not mixer_pad0:
            print("pad0_template wasn't create... Exiting\n")
            exit(-1)
        if not Gst.Element.link_pads(mixer, pad0, mixer_pad0):
            print("elements couldn't be linked... Exiting\n")
            exit(-1)
        # pad0 = Gst.Element.get_pad("sink_0")
        pad1 = mixer.get_static_pad("sink_1")
        pad2 = mixer.get_static_pad("sink_2")

        # sink_0
        pad0.set_property("xpos", 0)
        pad0.set_property("ypos", 0)
        pad0.set_property("alpha", 0)

        # sink_1
        pad1.set_property("xpos", 0)
        pad1.set_property("ypos", 0)

        # sink_2
        pad2.set_property("xpos", 200)
        pad2.set_property("ypos", 0)

        # get src pad of stream1, attach it to sink_%d of videomixer
        # we add all elements into the pipeline
        self.pipeline.add(source, filter, mixer, sink)
        self.pipeline.add(source1, filter1)
        self.pipeline.add(source2, filter2)

        # we link the elements together
        source.link(filter)
        filter.link(source1)
        source1.link(filter1)
        filter1.link(source2)
        source2.link(filter2)
        # link pad manually
        # filter_src_pad.link(pad0)
        filter.link_pads(filter, mixer, pad0)
        filter.link_pads(filter1, mixer, pad1)
        filter.link_pads(filter2, mixer, pad2)

        # filter1_src_pad.link(pad1)
        # filter2_src_pad.link(pad2)

        # mixer.link(sink)
        mixer.link(sink)
        # Gst.element_link_many(mixer,sink)

        self.pipeline.set_state(Gst.State.PLAYIN)


start = Main()
Gtk.main()
