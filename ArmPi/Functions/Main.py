"""
    Main file for ROB 521 Project. Detects blocks and pushes them to a given position.
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
from Perception import Perception


def main():
    print("Running: Push Blocks")
    
    # initializations
    my_camera = Camera.Camera()
    my_camera.camera_open()
    blocks = Perception()
    
    while True:
        img = my_camera.frame
        if img is not None:
            frame = img.copy()
            
            colorDetected, center, rotAngle = blocks.Tracking(frame)
            print("colorDetected:", colorDetected)
            print("center:", center)
            print("rotAngle:", rotAngle)
            
            # Display image
            cv2.imshow('Frame', img)

            key = cv2.waitKey(1)
            if key == 27:
                break
    
    my_camera.camera_close()
    cv2.destroyAllWindows()
    
    
    
    
    return


if __name__ == "__main__":
    main()
