from imutils import paths
import face_recognition
import pickle
import cv2
import os
import config


def add(name):

    try:
        data = pickle.loads(open(config.ENCODINGS_PATH, "rb").read())
        knownEncodings = data["encodings"]
        knownNames = data["names"]
    except EOFError:
        knownEncodings = []
        knownNames = []
    
    # grab the paths to the input images in our dataset
    imagePaths = list(paths.list_images("dataset" + "/" +name))

    # loop over the image paths
    for (i, imagePath) in enumerate(imagePaths):
        # extract the person name from the image path
        name = imagePath.split(os.path.sep)[-2]

        # load the input image and convert it from RGB (OpenCV ordering)
        # to dlib ordering (RGB)
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # detect the (x, y)-coordinates of the bounding boxes
        # corresponding to each face in the input image
        boxes = face_recognition.face_locations(rgb, model="hog")

        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb, boxes)

        # loop over the encodings
        for encoding in encodings:
            # add each encoding + name to our set of known names and
            # encodings
            knownEncodings.append(encoding)
            knownNames.append(name)

    # dump the facial encodings + names to disk
    data = {"encodings": knownEncodings, "names": knownNames}
    print(data)
    f = open(config.ENCODINGS_PATH, "wb")
    f.write(pickle.dumps(data))
    f.close()
    return True

def delete(name):

    try:
        data = pickle.loads(open(config.ENCODINGS_PATH, "rb").read())
        knownEncodings = data["encodings"]
        knownNames = data["names"]
    except EOFError:
        return -1
    
    try:
        index = knownNames.index(name)
        print(index)
        del knownNames[index]
        del knownEncodings[index]
        f = open(config.ENCODINGS_PATH, "wb")
        f.write(pickle.dumps(data))
        f.close()
        return True
    except:
        pass
    
    
