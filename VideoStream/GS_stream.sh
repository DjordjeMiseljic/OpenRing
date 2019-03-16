#! /bin/bash
# required from client to run gst which complicates things, not good solution for android client

raspivid -t 0 -hf -w 640 -h 320 -fps 25 -b 2000000 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=192.168.0.16 port=9000

# raspvid	command line tool for capturing vido with the RPi camera
# -n 			no preview
# -hf 		horizontal flip
# -t 			duration of capture, 0 = infinite
# -b 			bitrate 2000000 2Mb/s
# -o - 		output is gven to subsequent ppe
# -w 			width of video being captured
# -h 			hight of video being captured
# -fps		fps of video being captured

# gst-launch-1.0 command line tool to build and run GStreamer pipelines
# tcpserversink last plugin in the pipeline acts as TCP server with explicit IP and port number
