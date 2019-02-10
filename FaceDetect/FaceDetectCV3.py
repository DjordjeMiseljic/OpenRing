import sys, cv2
# **************************************************************************
# CV3 VERSION
# Refactored https://realpython.com/blog/python/face-recognition-with-python/
# ***************************************************************************

def cascade_detect(cascade, image):
    "detect objects"
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cascade.detectMultiScale(
        gray_image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
        #flags = cv2.CV_HAAR_SCALE_IMAGE
        )

def detections_draw(image, detections):
    "draw squares around detected objects"
    for (x, y, w, h) in detections:
        print "({0}, {1}, {2}, {3})".format(x, y, w, h)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

def main(argv=None):
    "Main function for face detection"
    if argv is None:
        argv = sys.argv

    image_path = sys.argv[1]

    if len(sys.argv) > 2:
        result_path = sys.argv[2]
    else:
        result_path = None

    if len(sys.argv) > 3:
        cascade_path = sys.argv[3]
    else:
        cascade_path = "haarcascade_frontalface_default.xml"
    print "NOTE: Arguments set"

    cascade = cv2.CascadeClassifier(cascade_path)
    image = cv2.imread(image_path)

    if image is None:
        print "ERROR: Image did not load."
        return 2
    print "NOTE: Image loaded"

    detections = cascade_detect(cascade, image)
    print "NOTE: Cascade detect passed"
    detections_draw(image, detections)
    print "NOTE: Detections Draw passed"

    print "Found {0} objects!".format(len(detections))
    if result_path is None:
        cv2.imshow("Objects found", image)
        cv2.waitKey(0)
    else:
        cv2.imwrite(result_path, image)

if __name__ == "__main__":
    sys.exit(main())
