#!/bin/bash

cd /tmp/stream
raspistill --nopreview -w 640 -h 480 -q 10 -o /tmp/stream/pic.jpg -tl 0 -t 0  &
LD_LIBRARY_PATH=/usr/local/lib mjpg_streamer -i "input_file.so -f /tmp/stream -n pic.jpg" -o "output_http.so -p 9000 -w /usr/local/www"
