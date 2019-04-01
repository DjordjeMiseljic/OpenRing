import io
import time
import picamera
from base_camera import BaseCamera

# Camera class overrides base_camera by implementing frames method which yeild frames
class Camera(BaseCamera):
    @staticmethod
    def frames_jpeg():
        time.sleep(2)
        with picamera.PiCamera() as camera:
            print("Starting stream in 2 seconds")
            # let camera warm up
            time.sleep(1)

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
    def frames_rgb():
        with picamera.PiCamera() as camera:
            # let camera warm up
            # initialize the camera and grab a reference to the raw camera capture
            camera.resolution = tuple(conf["resolution"])
            camera.framerate = conf["fps"]
            rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))
            # allow the camera to warmup, then initialize the average frame, last
            # uploaded timestamp, and frame motion counter
            print("[INFO] warming up...")
            time.sleep(2)
            camera.capture(rawCapture, format="bgr")
            fframe = rawCapture.array
            rawCapture.truncate(0)
            for f in camera.capture_continuous(rawCapture, format="bgr",
                                               use_video_port=True):
                frame = f.array
                # resize the frame, convert it to grayscale, and blur it
                frame = imutils.resize(frame, width=500)
                yield frame
                rawCapture.truncate(0)
# start detect thread
Camera.initial_call()
