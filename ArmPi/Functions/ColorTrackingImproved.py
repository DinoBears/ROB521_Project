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
from ColorPerception import *
from MoveArm import *

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)


def main():
    print("hello")
    
    # Initializing perception tasks
    my_camera = Camera.Camera()
    my_camera.camera_open()
    perception = ColorPerception()
    perception.__target_color = ('red',)
    
    # Initializing movement tasks
    moveArm = MoveArm()
    moveArm.initMove() # Go to initial position
    
    th = threading.Thread(target=moveArm.move)
    th.setDaemon(True)
    th.start()
    
    
    # Run perception task
    while True:
        img = my_camera.frame
        if img is not None:
            
            # perception.Tracking.start_pick_up = moveArm.move.start_pick_up
            
            frame = img.copy()
            Frame, detect_color = perception.Tracking(frame)
            
            # update moveArm variables
            moveArm.detect_color = detect_color
            moveArm.rotation_angle = perception.rotation_angle
            moveArm.world_x = perception.world_x
            moveArm.world_y = perception.world_y
            moveArm.world_X = perception.world_X
            moveArm.world_Y = perception.world_Y
            moveArm.start_pick_up = perception.start_pick_up

            # Display frame
            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break

    my_camera.camera_close()
    cv2.destroyAllWindows()

    return

if __name__ == "__main__":
    main()
