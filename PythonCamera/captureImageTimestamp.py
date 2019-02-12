import picamera
from time import sleep
from subprocess import call
from datetime import datetime

#Take a picture
currentTime = datetime.now()
picTime = currentTime.strftime("%d%m%Y_%H:%M:%S")
name = "image"
filePath = "CapturedFiles/"+name+"_"+picTime+".jpg"

print ("About to take a picture!")
with picamera.PiCamera() as camera:
    camera.resolution = (1280,720)
    for i in range (3,0,-1):
        print(i)
        sleep(1)
    camera.capture(filePath)
print("Picture taken")

# Insert timestamp in bottom right corner
print ("Inserting timestamp...")
timestampMessage = picTime
timestampCommand = "/usr/bin/convert "+filePath+" -pointsize 32 -fill red \
    -annotate +800+700 '"+timestampMessage+"' "+filePath
call([timestampCommand], shell=True)
print ("Timestamp inserted")


