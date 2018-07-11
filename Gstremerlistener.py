import sys

import gi

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst


#  the receiver
#  gst-launch-1.0 -v udpsrc port=5000 caps="application/x-rtp" ! rtpvp8depay ! vp8dec ! videoconvert ! autovideosink

# the full code gst-launch-1.0 -v udpsrc port=5000  caps="application/x-rtp" ! rtpvp8depay ! vp8dec ! alpha
# method=green ! mixer.sink_0 \ udpsrc port=5001  caps="application/x-rtp" ! rtpvp8depay ! vp8dec ! alpha method=green
#  target-r=0 target-b=0 target-g=0 black-sensitivity=128 white-sensitivity=0 ! mixer.sink_1 \ udpsrc port=5002
# caps="application/x-rtp" ! rtpvp8depay ! vp8dec ! alpha method=custom target-r=0 target-b=0 target-g	=0
# black-sensitivity=128 white-sensitivity=0 ! mixer.sink_2 \ videomixer name=mixer sink_0::zorder=2 sink_1::zorder=1
# sink_2::zorder=2 ! \ videoconvert ! autovideosink
def main():
    #  initiate gstreamer
    GObject.threads_init()
    Gst.init(None)
    pipeline = Gst.Pipeline()

    # create the parts of the pipeline
    #  first source
    udpsrc = Gst.ElementFactory.make('udpsrc', Gst.ELEMENT_FACTORY_KLASS_SRC)
    udpsrc.set_property("port", 5000)
    caps = Gst.Caps("application/x-rtp, width=640, height=480, framerate=20/1")
    udpsrc.set_property("caps", caps)
    alphacolor = Gst.ElementFactory.make("alpha", "alpha")
    alphacolor.set_property("method", "green")
    mixer = Gst.ElementFactory.make("videomixer", "mixer")

    rtpvp8depay = Gst.ElementFactory.make('rtpvp8depay', None)
    vp8dec = Gst.ElementFactory.make('vp8dec', None)
    videoconvert = Gst.ElementFactory.make('videoconvert', "convert")
    videosink = Gst.ElementFactory.make("autovideosink", "video-output")

    # check if the parts can be created
    if not rtpvp8depay or not udpsrc or not vp8dec or not pipeline or not videoconvert:
        print("Not all elements could be created.", file=sys.stderr)
        exit(-1)

    # add them to the pipeline in the proper order
    pipeline.add(udpsrc, rtpvp8depay, vp8dec, videoconvert, videosink)

    # link the elements in order
    udpsrc.link(rtpvp8depay)
    rtpvp8depay.link(vp8dec)
    vp8dec.link(videoconvert)
    videoconvert.link(videosink)
    ret = pipeline.set_state(Gst.State.PLAYING)
    if ret == Gst.StateChangeReturn.FAILURE:
        print("Unable to set the pipeline to the playing state.", file=sys.stderr)
        exit(-1)
    # Wait until error or EOS
    bus = pipeline.get_bus()

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
    pipeline.set_state(Gst.State.NULL)


main()
