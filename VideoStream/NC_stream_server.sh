#!/bin/bash
raspivid -t 0 -hf -w 640 -h 480 -fps 25 -b 2000000 -o - | nc 192.168.0.10 9000
