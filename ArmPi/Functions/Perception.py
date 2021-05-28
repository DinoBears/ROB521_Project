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
        # # detected block characteristics
        # self.colorsDetected = ()    # colors of the blocks detected
        # self.centers = ()    # center locations of the blocks detected
        # self.rotAngles = ()  # rotation angles of the blocks detected
        
        # color range for the blocks
        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
        } 
        
        self.targetColor = ('red', 'green', 'blue')
        self.size = (640, 480)  # size of the image
        
        
    def Tracking(self, img):
        
        colorsDetected = ()    # colors of the blocks detected
        centers = ()    # center locations of the blocks detected
        rotAngles = ()  # rotation angles of the blocks detected
        
        # resize image for processing
        img_copy = img.copy()
        frame_lab = self.resizeImg(img_copy)
        
        # find location and size of contours
        
        
        # color_area_max = None
        # max_area = 0
        # areaMaxContour_max = 0
        

        for i in color_range:   #color_range comes from LABConfig.py
            if i in self.targetColor:               
                contours = self.getContours(frame_lab, i) # Use openCV to find contours
                print("i:", i)
                print("conours:", contours)
                
                # areaMaxContour, area_max = getAreaMaxContour(contours)  # Find the largest contour
                # if areaMaxContour is not None:
                #     if area_max > max_area:  # 找最大面积
                #         max_area = area_max
                #         color_area_max = i
                #         areaMaxContour_max = areaMaxContour

        return



    def resizeImg(self, img):
       # returns gaussian blur of a smaller image
       frame_resize = cv2.resize(img, self.size, interpolation=cv2.INTER_NEAREST)
       frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
       frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB) # convert image from BGR to LAB color space
       return frame_lab  


          
    def getContours(self, frame_lab, color):
        frame_mask = cv2.inRange(frame_lab, color_range[color][0], color_range[color][1])  # Make a mask from the image
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # Remove noise outside the objects of interest
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # Remove noise inside the objects of interest
        contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # Find the outline
        return contours
        
        
        
        
        
        
        
        
        
        
        

