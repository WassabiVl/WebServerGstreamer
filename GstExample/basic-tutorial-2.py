#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# GStreamer SDK Tutorials in Python
#
#     basic-tutorial-2
#
"""
basic-tutorial-2: GStreamer concepts
http://docs.gstreamer.com/display/GstSDK/Basic+tutorial+2%3A+GStreamer+concepts
"""

import gi
import sys

gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)

# Create the elements
source = Gst.ElementFactory.make("videotestsrc", "source")
# sink2 = Gst.ElementFactory.make("autovideosink", "sink")
sink = Gst.ElementFactory.make("udpsink", "sink")
sink.set_property("host", '127.0.0.1')
sink.set_property("port", 5000)

# Create the empty pipeline
pipeline = Gst.Pipeline()

if not source or not sink or not pipeline:
    print("Not all elements could be created.", file=sys.stderr)
    exit(-1)

# Build the pipeline
pipeline.add(source)
pipeline.add(sink)
# pipeline.add(sink2)
if not Gst.Element.link(source, sink):
    print("Elements could not be linked.", file=sys.stderr)
    exit(-1)
if not Gst.Element.link(sink, sink2):
    print("Elements could not be linked.", file=sys.stderr)
    exit(-1)

# Modify the source's properties
source.set_property("pattern", 0)

# Start playing
ret = pipeline.set_state(Gst.State.PLAYING)
if ret == Gst.StateChangeReturn.FAILURE:
    print("Unable to set the pipeline to the playing state.", file=sys.stderr)
    exit(-1)

# Wait until error or EOS
bus = pipeline.get_bus()
msg = bus.timed_pop_filtered(
    Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS)

# Parse message
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
