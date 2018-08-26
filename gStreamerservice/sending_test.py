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
    pipeline = Gst.parse_launch('videotestsrc pattern=pinwheel background-color=0x00ff00 foreground-color=0x0000ff ! x264enc bitrate=200 speed-preset=superfast tune=zerolatency ! queue ! rtph264pay config-interval=1 ! queue ! udpsink host="127.0.0.1" port=7005')
  #  pipeline = Gst.parse_launch('videotestsrc pattern=pinwheel background-color=0x00ff00 foreground-color=0x0000ff ! x264enc bitrate=1000 speed-preset=superfast tune=zerolatency ! queue ! rtph264pay config-interval=1 ! queue ! udpsink host=141.54.50.64 port=5001');

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
