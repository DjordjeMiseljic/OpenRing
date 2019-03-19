raspivid -t 0 -hf -w 640 -h 320 -fps 25 -o - | nc 192.168.0.16 9000
