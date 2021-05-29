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
        
        # Other initializations
        self.AK = ArmIK()
        self.servo1 = 500                   # block close angle for the gripper
        self.tracking = True                # shows if we are actively looking for blocks
        
        
    def move(self):
        print("Begin Move")
        self.initMove()
        
        while True:
            reachable = False
            timer = self.timing()
            
            # If a block has been detected, and hasn't moved for a while, run arm
            if timer > self.waitTime:
                x, y = self.center
                self.beginTimer = True    # reset the timer
                self.tracking = False
                
                self.goToBlock(x, y) # go down to block
                self.grabBlock(x, y) # turn gripper and go to pick up block
                self.defaultPos() # go back to home position
                
    def goToBlock(self, x, y):
        # get close to block
        self.AK.setPitchRangeMoving((x, y - 2, 5), -90, -90, 0)
        time.sleep(0.02)
        return
            
    
    def grabBlock(self, x, y):
        # open gripper
        Board.setBusServoPulse(1, self.servo1 - 280, 500) 
        
        # turn gripper to match block
        servo2_angle = getAngle(x, y, self.rotAngle) 
        Board.setBusServoPulse(2, servo2_angle, 500) 
        time.sleep(0.8)
        
        # put gripper around block
        self.AK.setPitchRangeMoving((x, y, 2), -90, -90, 0, 1000)
        time.sleep(2)
        
        # close gripper
        Board.setBusServoPulse(1, self.servo1, 500)
        time.sleep(1)
        return
        
    def defaultPos(self):
        # go to home position
        Board.setBusServoPulse(2, 500, 500)         
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)  # Move the arm up
        time.sleep(1)
        return
        
        
    def initMove(self):
        # Initial position
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
        return
    
        
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
        
#     def checkReach(self, target):
#         reachable = False
#         x, y = target
#         
#         result = self.AK.setPitchRangeMoving((x, y - 2, 5), -90, -90, 0)
#         
#         if result == False:
#             reachable = False
#         else:
#             reachable = True
#             time.sleep(result[2]/1000)    # wait a bit so that the arm doesn't move
#         print("result:", result)
#         print("reachable", reachable)
# 
#         return reachable