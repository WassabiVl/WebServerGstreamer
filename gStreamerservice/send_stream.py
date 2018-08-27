import sys

import gi

import requests

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, Gtk

def run_pipeline(script):
    print(script)
    pipeline = Gst.parse_launch(script)

    # Start playing
    pipeline.set_state(Gst.State.PAUSED)
    print('playing')
    pipeline.set_state(Gst.State.PLAYING)
    return pipeline

# Build the pipeline
try:
    print(str(sys.argv))
    url = sys.argv[1] + ":8888/get_port"
    print(url)
    r = requests.get("http://" + url)
    print(r.text)
    Gst.init(None)
    run_pipeline('videotestsrc pattern=' + sys.argv[2] +
                    ' background-color=0x00ff00 foreground-color=0x0000ff ! x264enc bitrate=200 speed-preset=superfast tune=zerolatency ! queue ! rtph264pay config-interval=1 ! queue ! udpsink host="' +
                    sys.argv[1] + '" port=' + r.text)
    run_pipeline('udpsrc port=6000 caps="application/x-rtp, media=video, clock-rate=90000, encoding-name=H264, framerate=60/1, width=1600, height=900" ! rtpjitterbuffer drop-on-latency=false latency=500 ! rtph264depay ! queue ! h264parse ! queue ! avdec_h264 ! queue ! videoconvert ! queue ! autovideosink sync=false')

    Gtk.main()

except Exception as e:
    print(e)