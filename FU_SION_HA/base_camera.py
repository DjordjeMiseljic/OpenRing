from support.pyimagesearch.tempimage import TempImage
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import warnings
import datetime
import dropbox
import imutils
import json
import time
import threading
import cv2

try:
    from greenlet import getcurrent as get_ident
    print("<get identificator> imported from greenlet")
except ImportError:
    try:
        from thread import get_ident
        print("<get identificator> imported from thread")
    except ImportError:
        from _thread import get_ident
        print("<get identificator> imported from _thread")



# Helper class that tracks clients
class CameraEvent(object):
    """An Event-like class that signals all active clients when a new frame is available.  """
    def __init__(self):
        print('CAMERA EVENT : Starting init function')
        self.events = {}

    def wait(self):
        """Invoked from each client's thread to wait for the next frame."""
        ident = get_ident()
        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        """Invoked by the camera thread when a new frame is available."""
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if the client's event is already set, it means the client
                # did not process a previous frame
                # if the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove = ident
        if remove:
            del self.events[remove]

    def clear(self):
        """Invoked from each client's thread after a frame was processed."""
        self.events[get_ident()][0].clear()

    def destroy(self):
        """Invoked from stream thread when its switching to detect thread"""
        self.events.clear()


class BaseCamera(object):
    stream_thread_handle = None  # background thread that reads frames from camera
    detect_thread_handle = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    event = CameraEvent()

    def __init__(self):
        """Start the background camera thread if it isn't running yet."""
        print('BASE CAMERA : Starting init function')
        if BaseCamera.stream_thread_handle is None:
            BaseCamera.last_access = time.time()

            # start background frame thread
            BaseCamera.stream_thread_handle = threading.Thread(target=self.stream_thread)
            BaseCamera.stream_thread_handle.start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)


    # First method called by client thread when client connects via flask
    def get_frame(self):
        """Return the current camera frame."""
        BaseCamera.last_access = time.time()

        # wait for a signal from the camera thread
        BaseCamera.event.wait()
        BaseCamera.event.clear()

        return BaseCamera.frame

    def detect_motion (gray, avg, conf):
        # add gaussian blur to 
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        # accumulate the weighted average between the current frame and
        # previous frames, then compute the difference between the current
        # frame and running average
        cv2.accumulateWeighted(gray, avg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

        # threshold the delta image, dilate the thresholded image to fill
        # in holes, then find contours on thresholded image
        thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,
                cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
        return imutils.grab_contours(contours)

    def detect_face (gray, cascade):
        return cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(10, 20)
            #flags = cv2.CV_HAAR_SCALE_IMAGE
            )

    @staticmethod
    def frames_jpeg():
        """"Generator that returns frames from the camera in jpeg format"""
        raise RuntimeError('Must be implemented by subclasses.')

    #@staticmethod
    #def frames_rgb():
        #""""Generator that returns frames from the camera in rgb format"""
        #raise RuntimeError('Must be implemented by subclasses.')

    @classmethod
    def stream_thread(cls):
        """Camera background stream thread."""
        print('Starting stream thread.')
        time.sleep(2)
        frames_iterator = cls.frames_jpeg()
        for frame in frames_iterator:
            BaseCamera.frame = frame
            BaseCamera.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            if time.time() - BaseCamera.last_access > 5:
                frames_iterator.close()
                BaseCamera.event.destroy()
                print('Stopping camera thread due to inactivity.')
                break
        BaseCamera.stream_thread_handle = None
        # start detect thread
        BaseCamera.detect_thread_handle = threading.Thread(target=cls.detect_thread)
        BaseCamera.detect_thread_handle.start()

    @classmethod
    def detect_thread(cls):
        """Camera background detect thread."""
        print('Starting detect thread.')

        # load configuration from json file
        conf = json.load(open("support/conf.json"))
        # load definition of face for detection
        cascade_path= "support/haarcascade_frontalface_default.xml"

        # build a cascade face classifier
        cascade = cv2.CascadeClassifier(cascade_path)
        print("[SUCCESS] face classifier built")

        # filter warnings, load the configuration and initialize the Dropbox client
        warnings.filterwarnings("ignore")
        client = None

        # check to see if the Dropbox should be used
        if conf["use_dropbox"]:
            # connect to dropbox and start the session authorization process
            client = dropbox.Dropbox(conf["dropbox_access_token"])
            print("[SUCCESS] dropbox account linked")
            

        # initialize the camera and grab a reference to the raw camera capture
        camera = PiCamera()
        camera.resolution = tuple(conf["resolution"])
        camera.framerate = conf["fps"]
        rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))

        # allow the camera to warmup, then initialize the average frame, last
        # uploaded timestamp, and frame motion counter
        print("[INFO] warming up...")
        time.sleep(conf["camera_warmup_time"])
        avg = None
        lastUploaded = datetime.datetime.now()
        motionCounter = 0

        camera.capture(rawCapture, format="bgr")
        fframe = rawCapture.array
        fframe = imutils.resize(fframe, width=500)
        gray = cv2.cvtColor(fframe, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # if the average frame is None, initialize it
        print("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        rawCapture.truncate(0)
        frames=0
        fps=0
        sample_time=0

        for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

            frame = f.array
            # generator
            #frames_iterator = cls.frames_rgb()
            #for frame in frames_iterator:

            # exit thread if there is a client
            if BaseCamera.event.events:
                    #frames_iterator.close()
                print('Client detected, switching to stream thread.')
                cv2.destroyAllWindows()
                BaseCamera.detect_thread_handle = None
                rawCapture.truncate(0)
                camera = None
                break

            timestamp = datetime.datetime.now()
            text = "Unoccupied"

            # resize the frame, convert it to grayscale, and blur it
            frame = imutils.resize(frame, width=500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # find faces in frame
            faces = cls.detect_face(gray, cascade)

            # find movement in frame based on previous
            contours = cls.detect_motion(gray, avg, conf)

            #draw squares around detected faces"
            for (x, y, w, h) in faces:
                #print ("({0}, {1}, {2}, {3})".format(x, y, w, h))
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                text = "Occupied"

            # draw sqares around contours
            for c in contours:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < conf["min_area"]:
                        continue

                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "Occupied"

                
            # draw the text and timestamp on the frame
            ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
            cv2.putText(frame, "<{}>".format(text), (10, 20),
                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 2)
            cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_COMPLEX,
                0.35, (255, 0, 0), 1)


            # check to see if the room is occupied
            if text == "Occupied":
                # check to see if enough time has passed between uploads
                if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
                    # increment the motion counter
                    motionCounter += 1

                    # check to see if the number of frames with consistent motion is
                    # high enough
                    if motionCounter >= conf["min_motion_frames"]:
                        # check to see if dropbox sohuld be used
                        if conf["use_dropbox"]:
                            # write the image to temporary file
                            t = TempImage()
                            cv2.imwrite(t.path, frame)

                            # upload the image to Dropbox and cleanup the tempory image
                            print("[UPLOAD] {}".format(ts))
                            path = "/{base_path}/{timestamp}.jpg".format(
                                base_path=conf["dropbox_base_path"], timestamp=ts)
                            client.files_upload(open(t.path, "rb").read(), path)
                            t.cleanup()

                        # update the last uploaded timestamp and reset the motion
                        # counter
                        lastUploaded = timestamp
                        motionCounter = 0

            # otherwise, the room is not occupied
            else:
                    motionCounter = 0

            # check to see if the frames should be displayed to screen
            if conf["show_video"]:
                    # display the security feed
                    cv2.imshow("Security Feed", frame)
                    key = cv2.waitKey(1) & 0xFF

                    # if the `q` key is pressed, break from the lop
                    if key == ord("q"):
                            break

                    
            # clear the stream in preparation for the next frame
            rawCapture.truncate(0)
        