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


class ColorPerception():
    def __init__(self):
        self.range_rgb = {
                    'red': (0, 0, 255),
                    'blue': (255, 0, 0),
                    'green': (0, 255, 0),
                    'black': (0, 0, 0),
                    'white': (255, 255, 255),
                }                               # RGB values for target colors
        self.__target_color = ('red',)          # color(s) to target
        
        self.size = (640, 480)                  # size of the image
        self.roi = ()                           # region of interest
        self.rect = ()                          # minimum area rectangle around ROI 
        self.rotation_angle = ()                # angle of the block
        self.center_list = ()                   # list of (x, y) coordinates for ROIs
        
        self.last_x = 0
        self.last_y = 0
        self.world_x = 0
        self.world_y = 0
        self.world_X = 0
        self.world_Y = 0
        
        self.__isRunning = True                 # tells us if we should be running the program, if false, return an image
        self.get_roi = False                    # true if ROI has been found
        self.start_pick_up = False              # tells the robot arm to start picking up blocks
        
        self.still_time = 1.5                   # amount of time in seconds that the block must be still before robot picks up block
        self.t1 = 0                             # time when the block is first seen  
        self.begin_timer = True                 # True if a new timer can begin, starts a new t1
        pass




    def Tracking(self, img):
        # input: frame -one camera frame
        # output: imgOut -processed image with ROIs
        detect_color = ()
        center_list = []
        
        if not self.__isRunning:
            print("Not Running")
            imgOut = img
        
        if self.__isRunning:
            # make the image small and also add a cross to it
            self.drawRedLines(img)
            img_copy = img.copy()
            frame_gb = self.resizeImg(img_copy)
            
            # If we are looking for a ROI but are also starting to pick up a thing, stop looking for a ROI
            if self.get_roi and self.start_pick_up:
                self.get_roi = False
                frame_gb = getMaskROI(frame_gb, self.roi, self.size)  # makes a mask 
            
            # If we aren't picking up a thing yet, look for ROIs
            if not self.start_pick_up:
                contours, detect_color = self.getContours(frame_gb)
                areaMaxContour, area_max = self.getAreaMaxContour(contours)  # Find the largest contour
                
                # If a big enough contour was found, mark it
                if area_max > 2500:
                    self.get_roi = True
                    self.locateCenters(areaMaxContour, img, detect_color)
                    
                    # See how long the block has been there
                    timer = self.getRoiTime()
                    if timer > self.still_time:
                        count = 1
                        center_list.extend((self.world_x, self.world_y))
                        self.start_pick_up = True
                        self.world_X, self.world_Y = np.mean(np.array(center_list).reshape(count, 2), axis=0)
#                     print("timer:", timer)
                
                
            imgOut = img  
            
        return imgOut, detect_color
    
    def drawRedLines(self, img):
        # makes a red cross on the image
        img_h, img_w = img.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)
        return
        
    def resizeImg(self, img):
        # returns gaussian blur of a smaller image
        frame_resize = cv2.resize(img, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        return frame_gb
    
    def getContours(self, frame_gb):
        # find the contours of the image
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB) # convert image from BGR to LAB color space
        
        for i in color_range:
            if i in self.__target_color:
                detect_color = i
                frame_mask = cv2.inRange(frame_lab, color_range[detect_color][0], color_range[detect_color][1])  # Perform bit operations on the original image and mask
                opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # Open operation
                closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # Closed operation
                contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # Find the outline
        
        print("perception: detect color:", detect_color)
        return contours, detect_color
    
    def getAreaMaxContour(self, contours):
        # get the largest contour
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours:  # Traverse all contours
            contour_area_temp = math.fabs(cv2.contourArea(c))  # Calculate the contour area
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:  # Only when the area is greater than 300, the contour of the largest area is effective to filter interference
                    area_max_contour = c

        return area_max_contour, contour_area_max 
    
    def locateCenters(self, areaMaxContour, img, detect_color):
        # find the center of the contour and draw a box
        self.rect = cv2.minAreaRect(areaMaxContour)
        self.rotation_angle = self.rect[2]
        box = np.int0(cv2.boxPoints(self.rect))
        self.roi = getROI(box) # Get roi area

        img_centerx, img_centery = getCenter(self.rect, self.roi, self.size, square_length)  # Get the center coordinates of the block
        self.world_x, self.world_y = convertCoordinate(img_centerx, img_centery, self.size) # Convert to real world coordinates
        
        cv2.drawContours(img, [box], -1, self.range_rgb[detect_color], 2)
        cv2.putText(img, '(' + str(self.world_x) + ',' + str(self.world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[detect_color], 1) # Draw center point
        
        return
        
    def getRoiTime(self):
        distance = math.sqrt(pow(self.world_x - self.last_x, 2) + pow(self.world_y - self.last_y, 2)) #对比上次坐标来判断是否移动 Compare the last coordinate to determine whether to move
        self.last_x, self.last_y = self.world_x, self.world_y
        

        t2 = time.time()
        if distance < 0.3:
            if self.begin_timer:
                self.begin_timer = False
                self.t1 = time.time()
            timer = t2 - self.t1
        else:
            timer = 0
        
        return timer
                    
    
    
