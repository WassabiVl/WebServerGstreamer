#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# GStreamer SDK Tutorials in Python
#
#     basic-tutorial-1
#
"""
basic-tutorial-1: Hello world!
http://docs.gstreamer.com/display/GstSDK/Basic+tutorial+2%3A+GStreamer+concepts
"""

import sys

import gi

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, Gtk

Gst.init(None)
pipeline = Gst.Pipeline.new("test-pipeline")

# Build the pipeline
try:
    pipeline = Gst.parse_launch('udpsrc port=5002 caps="application/x-rtp,media=video,clock-rate=90000,encoding-name=H264,width=640,height=480,framerate=60/1" ! rtpjitterbuffer drop-on-latency=false latency=500 ! rtph264depay ! queue ! h264parse ! queue ! avdec_h264 ! queue ! alpha method=green ! videoconvert ! autovideosink')
except Exception as e:
    print(e)

# video = Gst.ElementFactory.make('videotestsrc','videotestsrc')
# video.set_property('is-live', True)
# video.set_property('pattern', 0)
# code = Gst.ElementFactory.make('x264enc')
# mpeg = Gst.ElementFactory.make('mpegtsmux')
# sink = Gst.ElementFactory.make('hlssink')
# sink.set_property('playlist-root','127.0.0.1:8000')
# pipeline.add(video, code, mpeg, sink)
# video.link(code)
# code.link(mpeg)
# mpeg.link(sink)

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
