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


class MoveArm():
    def __init__(self):
        self.coordinate = {
            'red':   (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5,  1.5),
            'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
            }                                   # coordinates for the cube home positions
        
        
        self.world_x = 0
        self.world_y = 0
        self.world_X = 0
        self.world_Y = 0
        
        self.__isRunning = True             # tells us if we should be running the program, if false, return an image
        self.first_move = True
        self.start_pick_up = False          # tells the robot arm to start picking up blocks
        self.action_finish = True
        self.detect_color = 'None'
        self.track = False
        self.servo1 = 500                   # close angle for the gripper
        self._stop = False
        self.rotation_angle = ()
            
        self.AK = ArmIK()
        
    def move(self):
        
        print("running move")
        
        unreachable = False
        
        while True:
            if self.__isRunning:
                if self.first_move and self.start_pick_up:
                    print("troubleshooting: if first move and start pick up")
                    
                    self.action_finish = False
                    self.set_rgb(self.detect_color) # Make the LEDs light up with the block color
                    self.setBuzzer(0.1) # Sound the buzzer
                    
                    # Check if block is reachable
                    #world_X = self.world_X
                    #world_Y = self.world_Y
                    print("self.world_X, self.world_Y:", self.world_X, self.world_Y)
                    result = self.AK.setPitchRangeMoving((self.world_X, self.world_Y - 2, 5), -90, -90, 0) # Do not fill in the running time parameters, adaptive running time
                    #result = AK.setPitchRangeMoving((world_X, world_Y - 2, 5), -90, -90, 0)
                    
                    print("result:", result)
                    
                    if result == False:
                        unreachable = True
                        print("Can't reach it")
                        time.sleep(0.02)
                    else:
                        print("Can reach it")
                        unreachable = False
                        time.sleep(result[2]/1000) # The third item of the return parameter is time
                    self.start_pick_up = False
                    self.first_move = False
                    self.action_finish = True
                    
                elif not self.first_move and not unreachable: # Not the first time an object has been detected
                    print("troubleshooting: if not first move and not unreachable")
                    
                    self.set_rgb(self.detect_color)
                    
                    if self.track: # If it is the tracking stage
                        if not self.__isRunning: # Stop and exit flag detection
                            continue
                        print("going to x,y")
                        self.AK.setPitchRangeMoving((self.world_x, self.world_y - 2, 5), -90, -90, 0, 20)
                        time.sleep(0.02)                    
                        self.track = False
                    
                    if self.start_pick_up: # If the object hasn’t moved for a while, start to grip
                        self.action_finish = False
                        if not self.__isRunning: # Stop and exit flag detection
                            continue
                        Board.setBusServoPulse(1, self.servo1 - 280, 500)  # open gripper
                        print("open gripper")
                        # Calculate the angle that the gripper needs to rotate
                        servo2_angle = getAngle(self.world_X, self.world_Y, self.rotation_angle)
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        print("turn gripper")
                        time.sleep(0.8)
                        
                        if not self.__isRunning:
                            continue
                        print("go down to grip")
                        self.AK.setPitchRangeMoving((self.world_X, self.world_Y, 2), -90, -90, 0, 1000)  # lower the altitude
                        time.sleep(2)
                        
                        if not self.__isRunning:
                            continue
                        print("close gripper")
                        Board.setBusServoPulse(1, self.servo1, 500)  # close grip
                        time.sleep(1)
                        
                        if not self.__isRunning:
                            continue
                        Board.setBusServoPulse(2, 500, 500)
                        print("lift arm")
                        self.AK.setPitchRangeMoving((self.world_X, self.world_Y, 12), -90, -90, 0, 1000)  # Move the arm up
                        time.sleep(1)
                        
                        if not self.__isRunning:
                            continue
                        # Sort and place different colored squares
                        print("go to place block")
                        print("self.detect_color",self.detect_color)
                        print("self.coordinate[self.detect_color][0]", self.coordinate[self.detect_color][0])
                        print("gtg")
                        result = self.AK.setPitchRangeMoving((self.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], 12), -90, -90, 0)   
                        print("result:", result)
                        time.sleep(result[2]/1000)
                        
                        if not self.__isRunning:
                            continue
                        print("turn gripper")
                        servo2_angle = getAngle(self.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], -90)
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(0.5)
    
                        if not self.__isRunning:
                            continue
                        
                        self.AK.setPitchRangeMoving((self.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], self.coordinate[self.detect_color][2] + 3), -90, -90, 0, 500)
                        time.sleep(0.5)
                        
                        if not self.__isRunning:
                            continue
                        self.AK.setPitchRangeMoving((self.coordinate[self.detect_color]), -90, -90, 0, 1000)
                        time.sleep(0.8)
                        
                        if not self.__isRunning:
                            continue
                        Board.setBusServoPulse(1, self.servo1 - 200, 500)  # Open the gripper and put down block
                        time.sleep(0.8)
                        
                        if not self.__isRunning:
                            continue                    
                        self.AK.setPitchRangeMoving((self.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], 12), -90, -90, 0, 800)
                        time.sleep(0.8)
    
                        self.initMove()  # back to first position
                        time.sleep(1.5)
                        
                        self.reset()
                    else:
                        time.sleep(0.01)
                        
                        
            else:
                if self._stop:
                    self._stop = False
                    Board.setBusServoPulse(1, self.servo1 - 70, 300)
                    time.sleep(0.5)
                    Board.setBusServoPulse(2, 500, 500)
                    self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
                    time.sleep(1.5)
                time.sleep(0.01)
             
                    
    def set_rgb(self, color):
        if color == "red":
            Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
            Board.RGB.show()
        elif color == "green":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
            Board.RGB.show()
        elif color == "blue":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
            Board.RGB.show()
        else:
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
            Board.RGB.show()
                    
        
        
    def setBuzzer(self, timer):
        # make a buzzer sound for duration of 'timer'
        Board.setBuzzer(0)
        Board.setBuzzer(1)
        time.sleep(timer)
        Board.setBuzzer(0)
        print("Buzzer")
        

    def initMove(self):
        # Initial position
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
        
        
    def stop(self):
        # Stop tracking things
        self._stop = True
        self.__isRunning = False
        print("ColorTracking Stop")
        
    def reset(self):
        # Reset variables
        self.first_move = True
        self.start_pick_up = False
        self.action_finish = True
        self.detect_color = 'None'
        self.track = False

    def initMove(self):
        # Go to initial position
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

        
        
        
