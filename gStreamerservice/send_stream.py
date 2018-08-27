import sys

import gi

import requests

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, Gtk


# Build the pipeline
try:
    print(str(sys.argv))
    url = sys.argv[1] + ":8888/get_port"
    print(url)
    r = requests.get("http://" + url)
    print(r.text)
    Gst.init(None)
    pipeline = Gst.parse_launch('videotestsrc pattern=' + sys.argv[2] +
                                ' background-color=0x00ff00 foreground-color=0x0000ff ! x264enc bitrate=200 speed-preset=superfast tune=zerolatency ! queue ! rtph264pay config-interval=1 ! queue ! udpsink host="' +
                                sys.argv[1] + '" port=' + r.text)

    # Start playing
    pipeline.set_state(Gst.State.PAUSED)
    print('playing')
    pipeline.set_state(Gst.State.PLAYING)

    # Wait until error or EOS
    bus = pipeline.get_bus()
    msg = bus.timed_pop_filtered(
        Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS)
    if msg:
        if msg.type == Gst.MessageType.ERROR:
            err, debug = msg.parse_error()
            print("Error received from element %s: %s" % (
                msg.src.get_name(), err), file=sys.stderr)
            print("Debugging information: %s" % debug, file=sys.stderr)
        elif msg.type == Gst.MessageType.EOS:
            print("End-Of-Stream reached.")
        else:
            print("Unexpected message received.", file=sys.stderr)

    # Free resources
    pipeline.set_state(Gst.State.NULL)

except Exception as e:
    print(e)