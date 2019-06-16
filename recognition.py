# import the necessary packages
from imutils.video import VideoStream
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import config
import numpy as np
import send_file
import gpio

send_timings = {}
send_interval = 360

# load the known faces and embeddings along with OpenCV"s Haar
# cascade for face detection
print("[INFO] loading encodings + face detector...")
gpio.init()
try:
    data = pickle.loads(open(config.ENCODINGS_PATH, "rb").read())
    knownEncodings = data["encodings"]
    knownNames = data["names"]
except EOFError:
    knownEncodings = []
    knownNames = []

detector = cv2.CascadeClassifier(config.HAAR_CASCADE_PATH)

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
# vs = VideoStream(src=0).start()
vs = cv2.VideoCapture(0)
time.sleep(2.0)

# loop over frames from the video file stream
while True:
	# grab the frame from the threaded video stream
    (ret, frame) = vs.read()
    # convert the input frame from (1) BGR to grayscale (for face
    # detection) and (2) from BGR to RGB (for face recognition)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # detect faces in the grayscale frame
    rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5,
                                      minSize=(30, 30),
                                      flags=cv2.CASCADE_SCALE_IMAGE)

    # OpenCV returns bounding box coordinates in (x, y, w, h) order
    # but we need them in (top, right, bottom, left) order, so we
    # need to do a bit of reordering
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    # compute the facial embeddings for each face bounding box
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []
    name = "Unknown" 
    # loop over the facial embeddings
    for encoding in encodings:
        # attempt to match each face in the input image to our known
        # encodings
        matches = face_recognition.compare_faces(knownEncodings, encoding)

        # check to see if we have found a match
        if True in matches:
            # find the indexes of all matched faces then initialize a
            # dictionary to count the total number of times each face
            # was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            # loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in matchedIdxs:
                name = knownNames[i]
                counts[name] = counts.get(name, 0) + 1
            # determine the recognized face with the largest number
            # of votes (note: in the event of an unlikely tie Python
            # will select first entry in the dictionary)
            name = max(counts, key=counts.get)
        # update the list of names
        names.append(name)
    # loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # draw the predicted face name on the image
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 1)
        cv2.putText(frame, name, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 1)
        print("[INFO] face recognized: " + name)

        # display the image to our screen
        if (name is not "Unknown"):

            cv2.imwrite("/home/pi/face.jpg", frame)
            try:
                timing = send_timings[name]
            except KeyError:
                send_timings[name] = time.time()
                send_file.run("/home/pi/face.jpg", name)
                continue
            if (time.time() - timing) > send_interval:
                send_timings[name] = time.time()
                gpio.disable()
                send_file.run("/home/pi/face.jpg", name)
                time.sleep(5)
                gpio.enable()

        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
