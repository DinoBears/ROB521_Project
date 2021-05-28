#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

class Move():
    def __init__(self):
        # coordinates for the cube home positions
        self.coordinate = {
            'red':   (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5,  1.5),
            'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
            }      

        # inputs from Perception
        self.colorDetected = ()
        self.center = ()
        self.rotAngle = ()
        
        # for timekeeping
        self.lastCenter = ()
        self.t1 = 0
        self.timer = ()
        self.beginTimer = True
        
        # user parameters
        self.waitTime = 1.5    # time to wait before picking up a block
        
    def move(self):
        print("Begin Move")
        
        while True:
            
            timer = self.timing()
            
            # If a block has been detected, and hasn't moved for a while, start to grab it
            if timer > self.waitTime:
                self.beginTimer = True    # reset the timer
            
        
        
    def timing(self):
        # runs the timer when the block isn't moving
        timer = 0
        
        if len(self.lastCenter)==2 and len(self.center)==2:
            t2 = time.time()
            x, y = self.center
            last_x, last_y = self.lastCenter
            
            distance = math.sqrt(pow(x - last_x, 2) + pow(y - last_y, 2))
            
            if distance < 0.3:
                if self.beginTimer:
                    self.t1 = t2
                    self.beginTimer = False
                timer = t2 - self.t1
            else:
                timer = 0

        return timer
        