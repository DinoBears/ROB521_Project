"""
    Locates one block at a time based on targetColor
    
    Return:
        colorDetected - color of the block detected
        centers - center locations of the blocks detected
        rotAngles - rotation angles of the blocks detected
    
"""



#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
from CameraCalibration.CalibrationConfig import *


class Perception():
    def __init__(self):        
        # color range for the blocks
        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
        } 
        
        self.targetColor = ('red') # colors we are looking for
        self.targetPos = (0, 0) # target position 
        
        self.size = (640, 480)  # size of the image
        self.frame = ()     # image frame with lines and block detection
        
        self.param_data = np.load(map_param_path + '.npz')
        self.map_param_ = self.param_data['map_param']
        
        
        
    def Tracking(self, img):
        # initialize variables
        max_area = 0
        colorDetected = ()    # colors of the blocks detected
        centerX = ()    # center location of the block detected
        centerY = ()
        rotAngle = ()  # rotation angle of the block detected
        box = ()    # coordinates for points of box around block
        
        # resize image for processing
        img_copy = img.copy()
        frame_lab = self.resizeImg(img_copy)
        
        # check for bocks of the given target color
        for i in color_range:   #color_range comes from LABConfig.py
            if i in self.targetColor:               
                contours = self.getContours(frame_lab, i) # Use openCV to find contours
                areaMaxContour, area_max = self.getAreaMaxContour(contours)  # Find the largest contour
                
                # select the biggest contour found
                if areaMaxContour is not None:
                    if area_max > max_area:
                        max_area = area_max
                        colorDetected = i
                        areaMaxContour_max = areaMaxContour
                        
        if max_area > 2500:     # areas larger than 2500 are probably blocks
            # find position and angle of box
            centerX, centerY, rotAngle, box = self.getBoxLocation(areaMaxContour_max)
            
        # add lines and labeled box into the image
        self.editImg(img, colorDetected, centerX, centerY, box)        
        self.frame = img
        

        return colorDetected, centerX, centerY, rotAngle



    def resizeImg(self, img):
       # returns gaussian blur of a smaller image
       frame_resize = cv2.resize(img, self.size, interpolation=cv2.INTER_NEAREST)
       frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
       frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB) # convert image from BGR to LAB color space
       
       return frame_lab  


          
    def getContours(self, frame_lab, color):
        # returns an array of points for the contours of the given color 
        frame_mask = cv2.inRange(frame_lab, color_range[color][0], color_range[color][1])  # Make a mask from the image
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # Remove noise outside the objects of interest
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # Remove noise inside the objects of interest
        contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # Find the outline
        
        return contours


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

        
    def getBoxLocation(self, areaMaxContour_max):
        
        rect = cv2.minAreaRect(areaMaxContour_max) # makes the smallest possible box around given contour
        box = np.int0(cv2.boxPoints(rect))  # converts rect into four points
        
        roi = getROI(box) # makes a new box around 'box' with angle=0, for caluclations

        img_centerx, img_centery = getCenter(rect, roi, self.size, square_length)  # Get the center coordinates of the block
        
        world_x, world_y = convertCoordinate(img_centerx, img_centery, self.size) # Convert to real world coordinates
        
        
        rotAngle = rect[2]
    
        return world_x, world_y, rotAngle, box
        
    

    def editImg(self, img, colorDetected, centerX, centerY, box):
        # makes a red cross on the image
        img_h, img_w = img.shape[:2]

        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)
        
            
        # make a red cross over the target position
        px, py = self.convertW2P(self.targetPos[0], self.targetPos[1], self.size, img)

#         print("coordinates now:", int(px), int(py))
#         print("img_h, img_w", img_h, img_w)
#         print("converted back:", convertCoordinate(px, py, self.size))
        
        cv2.line(img, (int(px-100), int(py)), (int(px+100), int(py)), (0, 200, 0), 1)
        cv2.line(img, (int(px), int(py-100)), (int(px), int(py+100)), (0, 200, 0), 1)
        
        # makes a box with labeled coordinates
        if centerX:    
            cv2.drawContours(img, [box], -1, self.range_rgb[colorDetected], 2)
            cv2.putText(img, '(' + str(centerX) + ',' + str(centerY) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[colorDetected], 1) #draw center point
            
            # draw a line from box center to target
            wx, wy = self.convertW2P(centerX, centerY, self.size, img)
            cv2.line(img, (int(wx),int(wy)), (int(px), int(py)), (200, 0, 0), 1)
        return

    def convertW2P(self, x, y, size, img):
        img_h, img_w = img.shape[:2]

        px = img_w/2 + x/self.map_param_
        py = img_h - (y-11)/self.map_param_
    
        return px, py
