from support.pyimagesearch.tempimage import TempImage
from picamera.array import PiRGBArray
from picamera import PiCamera
from pyfcm import FCMNotification
import socket
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
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident



# Helper class that tracks clients
class CameraEvent(object):
    """An Event-like class that signals all active clients when a new frame is available.  """
    def __init__(self):
        #print('[INFO] CAMERA EVENT : Starting init function')
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
    stream_thread_handle = None  # background thread that reads frames from camera and sends them to clients
    detect_thread_handle = None  # background thread that acts as surveillance camera
    socket_thread_handle = None  # background thread that recieves data via tcp
    conf =  None

    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    event = CameraEvent()
    # load definition of face for detection
    cascade_path= "support/haarcascade_frontalface_default.xml"

    def __init__(self):
        """Start the background camera thread if it isn't running yet."""
        #print('[INFO] BASE CAMERA : Starting init function')
        if BaseCamera.stream_thread_handle is None:
            BaseCamera.last_access = time.time()

            # start background frame thread
            BaseCamera.stream_thread_handle = threading.Thread(target=self.stream_thread)
            BaseCamera.stream_thread_handle.start()


            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)


    @classmethod
    def initial_call(cls):
        # load configuration from json file
        cls.fetchJSON()
        # start background detect thread
        cls.detect_thread_handle = threading.Thread(target=cls.detect_thread)
        cls.detect_thread_handle.start()
        # start background socket thread
        cls.socket_thread_handle = threading.Thread(target=cls.socket_thread)
        cls.socket_thread_handle.start()

    @classmethod
    def fetchJSON(cls):
    # Fetch conf from JSON file
        #print('[INFO] Local configuration updated')
        jsonFile = open("support/conf.json")
        cls.conf = json.load(jsonFile)
        jsonFile.close()

    @classmethod
    def updateJSON(cls):
    # Save changes to JSON file
        #print('[INFO] JSON file updated')
        jsonFile = open("support/conf.json", "w+")
        jsonFile.write(json.dumps(cls.conf, indent=4))
        jsonFile.close()
        
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

    #This method will be implemented by Camera.py class
    @staticmethod
    def frames_jpeg(conf):
        """"Generator that returns frames from the camera in jpeg format"""
        raise RuntimeError('Must be implemented by subclasses.')

    #This method will be implemented by Camera.py class
    @staticmethod
    def frames_rgb(conf):
        """"Generator that returns frames from the camera in rgb format"""
        raise RuntimeError('Must be implemented by subclasses.')

    @classmethod
    def socket_thread(cls):
        """Receive data from client via tcp communication"""
        print('[INFO] Starting socket thread')
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.bind(('192.168.0.16', 5002))
        serv.listen(1)
        print('[TCP] Listening on 192.168.0.16:5002')
        
        while True:
            conn, addr = serv.accept()
            try:
                from_client = ''
                print('[TCP] Accepted connection from address: {0}'.format(addr))
                while True:
                    #print('[TCP] Waiting to recieve data')
                    data = conn.recv(1024)
                    #print('[TCP] Data recieved')
                    if not data: 
                        #print('[TCP] No more data')
                        break
                    from_client += data.decode()
                    #print('[TCP] Data recieved from client:')
                    #extract data
                    #new_conf = from_client.strip();
                    new_conf = from_client.split("=");
                    #print ("opt: {}\n",new_conf[0])
                    #print ("val: {}\n",new_conf[1])
                    if(new_conf[0] == "use_dropbox"):
                        new_conf[1] = new_conf[1] == 'true'

                    if((new_conf[0])[:4] == "min_"):
                        new_conf[1] = int(new_conf[1])

                    cls.conf[new_conf[0]] = new_conf[1];
                    cls.updateJSON()
                    conn.send("Data recieved\n".encode())
                    print('[TCP] property {0} changed'.format(new_conf[0]))
            finally:
                conn.close()
                #print ('[TCP] client disconnected')


    @classmethod
    def stream_thread(cls):
        cls.fetchJSON()
        """Camera background stream thread."""
        print('[INFO] Starting stream thread')
        frames_iterator = cls.frames_jpeg(cls.conf)
        # MAIN FOR LOOP
        for frame in frames_iterator:
            BaseCamera.frame = frame
            BaseCamera.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            if time.time() - BaseCamera.last_access > 10:
                frames_iterator.close()
                BaseCamera.event.destroy()
                print('[INFO] Stopping camera thread due to inactivity')
                break
        BaseCamera.stream_thread_handle = None
        # start detect thread
        BaseCamera.detect_thread_handle = threading.Thread(target=cls.detect_thread)
        BaseCamera.detect_thread_handle.start()



    @classmethod
    def detect_thread(cls):
        cls.fetchJSON()
        """Camera background detect thread."""
        print('[INFO] Starting detect thread')

        # build a cascade face classifier
        cascade = cv2.CascadeClassifier(cls.cascade_path)
        print("[SUCCESS] Face detection object built")

        # filter warnings, load the configuration and initialize the Dropbox client
        warnings.filterwarnings("ignore")
        client = None

        # check to see if the Dropbox should be used
        if cls.conf["use_dropbox"]:
            # connect to dropbox and start the session authorization process
            client = dropbox.Dropbox(cls.conf["dropbox_access_token"])
            print("[SUCCESS] Dropbox account linked")

        # initialize some shit
        push_service = FCMNotification(cls.conf["api_key"])
        avg = None
        lastUploaded = datetime.datetime.now()
        motionFrameCounter = 0
        faceFrameCounter = 0
        sample_time = 0
        init_frame = 1

        frames_iterator = cls.frames_rgb(cls.conf)
        # MAIN FOR LOOP
        print("[SUCCESS] Data initialized")
        for frame in frames_iterator:


            #if its the first frame initialize everything, otherwise skip
            if init_frame:
                fframe = imutils.resize(frame, width=500)
                gray = cv2.cvtColor(fframe, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
                # initialize average frame
                print("[INFO] Detection thread started")
                avg = gray.copy().astype("float")
                init_frame = 0;
                continue
                    
            timestamp = datetime.datetime.now()
            motion_threat = False;
            face_threat = False;

            # resize the frame, convert it to grayscale, and blur it
            frame = imutils.resize(frame, width=500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)



            # Detection part:
            # find faces in frame
            faces = cls.detect_face(gray, cascade)
            # find movement in frame based on previous
            contours = cls.detect_motion(gray, avg, cls.conf)


            # Drawing on photo:
            # draw squares around detected faces"
            for (x, y, w, h) in faces:
                #print ("({0}, {1}, {2}, {3})".format(x, y, w, h))
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                face_threat = True

            # draw sqares around contours
            for c in contours:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < cls.conf["min_area"]:
                        continue
                # compute the bounding box for the contour, draw it on the frame,
                # and update the threat 
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                motion_threat = True
            # draw the timestamp on the frame
            ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
            cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.35, (255, 0, 0), 1)



            #update counters
            if motion_threat == True:
                motionFrameCounter += 1
            else:
                motionFrameCounter = 0

            if face_threat == True:
                faceFrameCounter += 1
            else:
                faceFrameCounter = 0



            # check to see if the room is occupied
            if motion_threat == True or face_threat == True:
                # check to see if enough time has passed between uploads
                if (timestamp - lastUploaded).seconds >= cls.conf["min_upload_seconds"]:
                    # increment the motion counter

                    # check to see if the number of frames with consistent motion is
                    # high enough
                    if motionFrameCounter >= cls.conf["min_motion_frames"] or faceFrameCounter >= cls.conf["min_face_frames"]:
                        # check to see if dropbox sohuld be used
                        # configure notification
                        message_title = "Security Warning"
                        if motionFrameCounter >= cls.conf["min_motion_frames"] :
                            message_body = "Movement detected on surveilance camera"
                            print("[WARNING] Movement detected {}".format(ts))
                        else:
                            message_body = "Person detected on surveillance camera"
                            print("[WARNING] Face detected {}".format(ts))
                        # send notification via firebase
                        push_service.notify_single_device(registration_id=cls.conf["token"],
                                                          message_title=message_title, message_body=message_body)
                        
                        if cls.conf["use_dropbox"]:
                            # write the image to temporary file
                            t = TempImage()
                            cv2.imwrite(t.path, frame)
                            # upload the image to Dropbox and cleanup the tempory image
                            print("[INET] Uploading captured photo {}".format(ts))
                            path = "/{base_path}/{timestamp}.jpg".format(
                                base_path=cls.conf["dropbox_base_path"], timestamp=ts)
                            client.files_upload(open(t.path, "rb").read(), path)
                            t.cleanup()
                        # update the last uploaded timestamp reset counters
                        lastUploaded = timestamp
                        faceFrameCounter = 0
                        motionFrameCounter = 0

            # check to see if the frames should be displayed to screen
            if cls.conf["show_video"]:
                    # display the security feed
                    cv2.imshow("Security Feed", frame)
                    key = cv2.waitKey(1) & 0xFF

                    # if the `q` key is pressed, break from the lop
                    if key == ord("q"):
                            break

            # if there is a client waiting for stream, shutdown this thread
            # and release camera reource
            if BaseCamera.event.events:
                print('[INFO] Client detected, switching to stream thread')
                frames_iterator.close()
                cv2.destroyAllWindows()
                BaseCamera.detect_thread_handle = None
                break
