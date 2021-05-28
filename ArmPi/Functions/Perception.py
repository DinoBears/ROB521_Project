"""
    Locate blocks
    
    Return:
        colorsDetected - colors of the blocks detected
        centers - center locations of the blocks detected
        rotAngles - rotation angles of the blocks detected
    
"""



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


class Perception():
    def __init__(self):
        # detected block characteristics
        self.colorsDetected = ()    # colors of the blocks detected
        self.centers = ()    # center locations of the blocks detected
        self.rotAngles = ()  # rotation angles of the blocks detected
        
        # color range for the blocks
        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
        } 
        
        
        

    
    
    def testing(self):
        print("testingPerception")
        
        return
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

