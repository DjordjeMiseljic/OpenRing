#!/bin/bash

mplayer -fps 25 -demuxer h264es ffmpeg://tcp://192.168.0.16:9000
