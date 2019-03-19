#! /bin/bash

gst-launch-1.0 -v tcpclientsrc host=192.168.0.10 port=9000 ! gdpdepay ! rtph264depay ! ffdec_h264 ! ffmpegcolorspace ! autovideosink sync=false
