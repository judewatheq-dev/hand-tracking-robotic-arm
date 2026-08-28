import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2 as cv
import numpy as np
import time
import mediapipe as mp
from pyfirmata2 import Arduino, SERVO
import math

#Define arduino 
board = Arduino('COM3')

#Define each finger
thumbPin = board.digital(8)
pointerPin = board.digital(9)
middlePin = board.digital(10)
ringPin = board.digital(11)
pinkyPin = board.digital(12)
thumbJoint = board.digital(13)

rotationPin = board.digital(3)

#set pins to servo 
thumbPin.mode = SERVO
pointerPin.mode = SERVO
middlePin.mode = SERVO
ringPin.mode = SERVO
pinkyPin.mode = SERVO
thumbJoint.mode = SERVO
rotationPin.mode = SERVO

#servo should be set at zero
thumbPin.write(0)
pointerPin.write(0)
middlePin.write(0)
ringPin.write(0)
pinkyPin.write(0)

#Thumb joint servo should never be out of the interval 180-90 degrees !!!
thumbJoint.write(180)
rotationPin.write(0)

#opening camera
cam = cv.VideoCapture(0)

#intializing hands
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

#Id #s for each joint
tipIds = [4, 8, 12, 16, 20] #for tips of fingers
dipIds = [3, 7, 11, 15, 19] #for joint below tip
pipIds = [2, 6, 10, 14, 18] #joint below it 

#servo functions 
def moveServoAngle(angle, pin):
    if angle > 160:
        pin.write(0) #if its staight then it will make it fully straight
    elif angle <= 160: #if bent even slighlty will bentd it fully   (there are no in betweens!!)
        pin.write(180)

def moveServoBool(isUp, pin):
    if isUp:
        pin.write(180)
    else:
        pin.write(0)

class HandDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):       
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon 
        self.trackCon = trackCon 

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode, max_num_hands=self.maxHands,min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

        self.tipIds = [4, 8, 12, 16, 20] #for tips of fingers
        self.dipIds = [3, 7, 11, 15, 19] #for joint below tip
        self.pipIds = [2, 6, 10, 14, 18] #joint below it 
        self.jointlist = [[4,3,2],[8,7,6], [12,11,10], [16,15,14], [20,19,18]]
        self.landmarks = []

 