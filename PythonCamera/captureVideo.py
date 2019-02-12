import picamera
from time import sleep
from subprocess import call

name = "pythonVideo"
# Record a video
print("Recording video...")
with picamera.PiCamera() as camera:
    camera.start_recording("CapturedFiles/"+name+".h264")
    sleep(10)
    camera.stop_recording()
print("Video Saved")

# Convert video to mp4 file format
print("Converting video...")
command = "MP4Box -add CapturedFiles/"+name+".h264 CapturedFiles/"+name+".mp4"
call([command], shell=True)
print("Video converted")


