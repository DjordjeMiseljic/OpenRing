import picamera
from time import sleep

# Setup the camera such that it closes
# when we are done with it
# camera = picamera.PiCamera() -> so this is bad
print ("About to take a picture!")
with picamera.PiCamera() as camera:
    camera.resolution = (1280,720)
    for i in range (3,0,-1):
        print(i)
        sleep(1)
    camera.capture("CapturedFiles/python_image.jpg")
print ("Picture taken")


    
