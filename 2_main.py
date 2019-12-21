import sys
import cv2
import os
import time
import numpy as np
import re

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'Vision'))
sys.path.append(os.path.join(base_dir, 'pySokoban'))
from Vision import camera
from Vision import coordinates
from pySokoban.Level import Level
from zenbo_junior import myRobot

class Game():
    def __init__(self, cam_id, host):
        self.cam = camera.myCamera(id=cam_id)
        self.host = host
        if self.host:
            self.robot = myRobot(host)
        # Choose a level set
        self.level_set = "magic_sokoban6"#"original"
        # Set the start Level
        self.current_level = 7
        self.myLevel = Level(self.level_set, self.current_level)
        self.target_found = False
        self.game_ing = True
        
    def monitor(self):
        # Use test images
        files = [filename for filename in os.listdir(self.cam.folder) if filename.startswith("monitoring")]
        files = sorted(files, key=lambda x:float(re.findall("(\d+)",x)[0]))
        img_name = os.path.join(self.cam.folder, files[-1])
        frame = cv2.imread(img_name)
        
        # ret, frame = self.cam.cam.read() # OK
        
        if (len(self.cam.cam_mtx)==3 \
            and len(self.cam.dist[0])==5 \
            and len(self.cam.newcam_mtx)==3):
            frame = self.cam.undistort(frame)
            # print("Xinyi: using undistort")
        if len(self.cam.M)==3:
            frame = self.cam.bird_view(frame)
            # print("Xinyi: using bird_view")
        
        cv2.imshow("monitor", frame)
        k = cv2.waitKey(1)
        # Exiting the window if 'q'/ESC is pressed on the keyboard. 
        if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
            self.game_ing = False
            
        return frame
        
    def parse_cv_to_matrix(self):
        pass

    def loop(self):
        while self.game_ing:
            frame = self.monitor()
                
            # if True: # Get gesture event and robot is static
                # Parse frame to matrix status
                # movePlayer()
            
        cv2.destroyAllWindows()
        
        if self.host:
            self.robot.release()
            

def main(cam_id=0,
         has_robot=True, 
         host=None):
    
    
    if not has_robot:
        host = None
    
    g = Game(cam_id, host)
    
    g.loop()
    # game_ing = True
    # while game_ing:
        # cam.camera_view(robot=True)
        
        # coordinate parsing for each grid
        
        # build matrix of puzzle status
    

if __name__ == '__main__':
    # main(preview_camera=True)
    
    main(cam_id=0, 
         has_robot=False, 
         host='192.168.0.126')
    
    # if len(sys.argv) > 1:
        # fn = sys.argv[1]
    # else:
        # fn = 'Vision/map/4.png' # 'shapes.png'
    # img2 = cv2.imread(fn)
    
    
    
    # sokoban.main()