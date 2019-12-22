import sys
import os
import numpy as np
import re
import cv2

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'Vision'))
from Vision import camera
from Vision import coordinates
from Vision import perspective_transform
from zenbo_junior import myRobot


def main(cam_id=1,
         preview_camera=True, 
         has_robot=False, 
         host=None, 
         do_calibration=True):
    """For set up the camera and test connection with Zenbo junior
    
    Args:
        cam_id (int): device id of camera
        preview_camera (bool): whether to view video stream
        has_robot (bool): whether to test connection with robot
        host (str): ip which shows on Zenbo lab app
        do_calibration (bool): whether to calibrate camera with chessboard pattern
        
    """
    
    
    cam = camera.myCamera(id=cam_id)
    if has_robot and host:
        host = '192.168.0.126'
        robot = myRobot(host)
        robot.say("I like you")
    
    print("Step(1) Manually check view coverage and shoot chessboard images")
    if preview_camera:
        cam.camera_view()
    
    print("Step(2) Calibrate camera")
    if do_calibration:
        # intrinsic calibration
        cam.calibration()

    print("\tGot camera Intrinsic & Extrinsic parameters.")
    print("Step(3) Please keep the puzzle be clean")
    cam.camera_view()
    input("\tPress Enter if we are ready to do perspective transform...")
    
    cam.camera_view(mode="monitoring")
    
    files = [filename for filename in os.listdir(cam.folder) if filename.startswith("monitoring")]
    files = sorted(files, key=lambda x:float(re.findall("(\d+)",x)[0]))
    img_name = os.path.join(cam.folder, files[-1])
    img = cv2.imread(img_name)
    print("Step(3) Calculate perspective transformation matrix")
    cam.get_perspective(img)
    
    if True:
        print("\tThis is the transformed view sample:")
        warped = cam.bird_view(img)
        cv2.imshow("Original", img)
        cv2.imshow("Warped", warped)
            
          
        k = cv2.waitKey(0)
        # Exiting the window if 'q'/ESC is pressed on the keyboard. 
        if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
            cv2.destroyAllWindows()
    
    print("Finish preparation of camera")
    
    if has_robot:
        robot.release()

def test():
    cam = camera.myCamera(id=0)
    files = [filename for filename in os.listdir(cam.folder) if filename.startswith("monitoring")]
    files = sorted(files, key=lambda x:float(re.findall("(\d+)",x)[0]))
    img_name = os.path.join(cam.folder, files[-1])
    img = cv2.imread(img_name)
    print("Step(3) Calculate perspective transformation matrix")
    cam.get_perspective(img)
    
    if True:
        print("\tThis is the transformed view sample:")
        warped = cam.bird_view(img)
        cv2.imshow("Original", img)
        cv2.imshow("Warped", warped)
            
          
        k = cv2.waitKey(0)
        # Exiting the window if 'q'/ESC is pressed on the keyboard. 
        if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
            cv2.destroyAllWindows()

if __name__ == '__main__':
    # main(cam_id=1,
         # host='192.168.0.126')
    
    test()