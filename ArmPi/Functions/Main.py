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
from Move import Move

def main():
    print("Running: Push Blocks")
    
    # initializations
    my_camera = Camera.Camera()
    my_camera.camera_open()
    blocks = Perception()
    moveArm = Move()
    
    # begin threads
    th = threading.Thread(target=moveArm.move)
    th.setDaemon(True)
    th.start()
    
    
    while True:
        img = my_camera.frame
        if img is not None:
            frame = img.copy()
            
            colorDetected, center, rotAngle = blocks.Tracking(frame)
            
            # passing information to arm
            print("passing  info")
            moveArm.colorDetected = colorDetected
            moveArm.lastCenter = moveArm.center
            moveArm.center = center
            moveArm.rotAngle = rotAngle
            
            
            # Display image
            cv2.imshow('Frame', blocks.frame)

            key = cv2.waitKey(1)
            if key == 27:
                break
    
    my_camera.camera_close()
    cv2.destroyAllWindows()
    
    
    
    
    return


if __name__ == "__main__":
    main()
