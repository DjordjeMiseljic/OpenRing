import io
import time
import picamera
import cv2
from base_camera import BaseCamera

# Camera class overrides base_camera by implementing frames method which yeild frames
class Camera(BaseCamera):
    @staticmethod
    def frames_jpeg(conf):
        # wait for other thread to shut down
        time.sleep(1)
        with picamera.PiCamera() as camera:
            camera.resolution = tuple(conf["resolution"])
            camera.framerate = conf["fps"]
            print("[INFO] Camera warming up")
            time.sleep(conf["camera_warmup_time"])

            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # return current frame
                stream.seek(0)
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

    @staticmethod
    def frames_rgb(conf):
        with picamera.PiCamera() as camera:

            # initialize the camera and grab a reference to the raw camera capture
            #camera = PiCamera()
            camera.resolution = tuple(conf["resolution"])
            camera.framerate = conf["fps"]
            rawCapture = picamera.array.PiRGBArray(camera, size=tuple(conf["resolution"]))

            # allow the camera to warmup, then initialize the average frame, last
            # uploaded timestamp, and frame motion counter
            print("[INFO] Camera warming up")
            time.sleep(conf["camera_warmup_time"])

            for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

                # return current frame
                yield f.array
                rawCapture.truncate(0)



# INITIALLY START DETECT THREAD UNTIL CLIENT CALLS
Camera.initial_call()
