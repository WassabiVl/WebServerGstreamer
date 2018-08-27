import sys

import gi

import requests

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, Gtk

def run_pipeline(script):
    pipeline = Gst.parse_launch(script)

    # Start playing
    pipeline.set_state(Gst.State.PAUSED)
    print('playing')
    pipeline.set_state(Gst.State.PLAYING)

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
    run_pipeline('udpsrc port=6000 caps="application/x-rtp, payload=96,clock-rate=90000, framerate=60/1" ! rtpjitterbuffer drop-on-latency=false latency=500 ! rtpmp4vdepay ! avdec_mpeg4 ! queue ! videoconvert ! queue ! xvimagesink sync=false')

except Exception as e:
    print(e)