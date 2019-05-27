import os
import cv2
import numpy as np
import face_recognition


def run(path):

    image = cv2.imread(path)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb, model="hog")
    
    if len(boxes) == 1:
        return True
    else:
        os.remove(path)
        return False
