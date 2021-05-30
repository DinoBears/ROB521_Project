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
        self.centerX = ()
        self.centerY = ()
        self.rotAngle = ()
        
        # for timekeeping
        self.lastCenterX = ()
        self.lastCenterY = ()
        self.t1 = 0
        self.timer = ()
        self.beginTimer = True
        
        # user parameters
        self.waitTime = 1.5    # time to wait before picking up a block
        
        # Other initializations
        self.AK = ArmIK()
        self.servo1 = 500                   # block close angle for the gripper
        self.tracking = True                # shows if we are actively looking for blocks
        self.targetPos = (0,0)                 # target position
        self.goalMet = False                # shows if the block is at the given goal
        
    def move(self):
        targetX, targetY = self.targetPos
        print("Begin Move")
        self.initMove()
        
        while True:
            reachable = False
            timer = self.timing()
            
            # If a block has been detected, and hasn't moved for a while, run arm
            if timer > self.waitTime:
                self.beginTimer = True    # reset the timer
                
                goalDistance = self.getDistance(targetX, targetY, self.centerX, self.centerY)
#                 print("goalDistance:", goalDistance)
                
                if goalDistance < 1:
                    print("Goal Reached")
                    self.goalMet = True
                    self.initMove() # go back to start
                else:
                    self.tracking = False
                    
                    angle = self.getAngle(targetX, targetY, self.centerX, self.centerY)  # angle of the block position in relation to the target
                    self.gripperAngle(angle) # turn gripper to be facing target
                    pointX, pointY = self.getPoint(targetX, targetY, self.centerX, self.centerY, 10) # find a point behind the block
#                     self.goToBlock(pointX, pointY)  # go behind block
#                     time.sleep(3)
                    dist = -goalDistance+4
                    pointX, pointY = self.getPoint(targetX, targetY, self.centerX, self.centerY, dist) # find a point behind the block
#                     self.goToBlock(targetX, targetY)  # go up to block
#                     time.sleep(3)
#                     self.defaultPos()
                    
                    self.tracking = True
                
                self.tracking = True
                self.center = ()
                self.lastCenter = ()
           
    def getPoint(self, x1, y1, x2, y2, dist):
        goalDistance = self.getDistance(x1, y1, x2, y2)
        
        dx = dist*((x2-x1)/goalDistance)
        dy = dist*((y2-y1)/goalDistance)
        
        xOut = x2 + dx
        yOut = y2 + dy
#         
#         print("x1, y1", x1, y1)
#         print("x2, y2", x2, y2)
#         print("dx, dy", dx, dy)
#         print("x3, y3", xOut, yOut)
        
        return xOut, yOut
                
    def getAngle(self, x1, y1, x2, y2):
        sideX = x2-x1
        sideY = y2-y1
        angleOut = ()
        
        angle = abs(math.atan((sideY/sideX)))
        angle = (angle*180)/math.pi
        
        if sideX > 0 and sideY > 0:
            angleOut = angle   # first quadrant
        elif sideX < 0 and sideY > 0:
            angleOut = 180 - angle  # second quadrant
        elif sideX < 0 and sideY < 0:
            angleOut = 180 + angle  # third quadrant
        else:
            angleOut = 360 - angle  # fourth quadrant

        return int(angleOut)
    
    def gripperAngle(self, angle):
        # calculate gripper angle and move
        if angle < 180:
            servoAngle = -(80/18)*angle+900  # servo is at 900 at 0 degrees, 100 at 180 degrees
        else:
            servoAngle = -(80/18)*(angle-180)+900
    
        Board.setBusServoPulse(2, int(servoAngle), 500)
        time.sleep(0.8)
        return
    
    
    def getDistance(self, x1, y1, x2, y2):
#         print("x1, y1", x1, y1)
#         print("x2, y2", x2, y2)
        distance = math.inf
        if x1 and x2:
            distance = math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))
        return distance 
           
                
                
    def goToBlock(self, x, y):
        # get close to block
        self.AK.setPitchRangeMoving((x, y, 2), -90, -90, 0)
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
        # go to home position, assumes block is in grasp
        Board.setBusServoPulse(2, 500, 500)         
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)  # Move the arm up
        time.sleep(1)
        return
        
    def storeBlock(self):
        # turn gripper to align with store location box
        servo2_angle = getAngle(self.coordinate[self.colorDetected][0], self.coordinate[self.colorDetected][1], -90)
        Board.setBusServoPulse(2, servo2_angle, 500)
        time.sleep(0.8)
        
        # go to block's store location
        self.AK.setPitchRangeMoving((self.coordinate[self.colorDetected][0], self.coordinate[self.colorDetected][1], self.coordinate[self.colorDetected][2] + 3), -90, -90, 0)
        time.sleep(2.5)
        
        # open gripper
        Board.setBusServoPulse(1, self.servo1 - 200, 500)
        time.sleep(0.8)

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
        
        if self.centerX and self.lastCenterX:
            t2 = time.time()
            
            distance = self.getDistance(self.centerX, self.centerY, self.lastCenterX, self.lastCenterY)
            if distance < 0.3:
                if self.beginTimer:
                    self.t1 = t2
                    self.beginTimer = False
                timer = t2 - self.t1
            else:
                timer = 0


        return timer
