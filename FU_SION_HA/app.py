#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response

# Raspberry Pi camera module (requires picamera package)
from camera_pi import Camera

app = Flask(__name__)

# After gen is called infinite loop will take frame by frame from camera class,
# and yeild it to the client in jpeg data form
def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# When client is forwarded to /video_feed, it will call 'gen' function
# with imported camera class as a paremeter
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# When client demands root, index.html will forward it to video feed
@app.route('/')
def index():
    """Seurveillance camera monitoring"""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='192.168.0.16',port='5000', threaded=True, debug=False, use_reloader=False)
