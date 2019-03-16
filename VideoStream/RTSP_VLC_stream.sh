#! /bin/bash
# delay 2.5s, @800x400 frequent freezes
# client URL: rstp://192.160.0.16:9000/
raspivid -t 0 -hf -w 640 -h 320 -fps 25 -o - | cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:9000/}' :demux=h264
# raspvid	command line tool for capturing vido with the RPi camera
# -n 			no preview
# -hf 		horizontal flip
# -t 			duration of capture, 0 = infinite
# -o - 		output is gven to subsequent ppe
# -w 			width of video being captured
# -h 			hight of video being captured
# -fps		fps of video being captured

# cvlc		command line vlc
# --sout		streaming protocol
# :demux 	video coding 

