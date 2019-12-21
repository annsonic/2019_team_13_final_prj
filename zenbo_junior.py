import os
base_dir = os.path.abspath(os.path.dirname(__file__))
import random
import pyzenbo
from pyzenbo.modules.dialog_system import RobotFace

class myRobot():
    def __init__(self, host=None):
        self.r = pyzenbo.connect(host)
        
        # self.r.on_result_callback = self.on_result
        self.dist = 0.19
        self.face = {
        "positive": [RobotFace.DEFAULT, RobotFace.DEFAULT_STILL, 
                     RobotFace.CONFIDENT, RobotFace.INTERESTED, 
                     RobotFace.HAPPY, RobotFace.PLEASED, 
                     RobotFace.PROUD, RobotFace.SINGING, 
                     RobotFace.ACTIVE, RobotFace.AWARE_LEFT, 
                     RobotFace.AWARE_RIGHT],
        "negative": [RobotFace.SHY, RobotFace.EXPECTING, 
                      RobotFace.SHOCKED, RobotFace.DOUBTING]
                      }
        self.pos_line = ['yes sir', 'go go go', 'lets go', 'ok', 'hey hey',
                         'a piece of cake']
        
    def release(self):
        self.r.release()
        
    def on_result(self, *args):
        print('on_result', args)
        
    def say(self, line="Hi", mood="positive"):
        self.r.robot.set_expression(random.choice(self.face[mood]), line)
        
    def move(self, x, y, theta):
        result = self.r.motion.move_body(relative_x=x, 
                relative_y=y, 
                relative_theta_degree=theta, 
                speed_level=3,
                sync=True, 
                timeout=None)
        # print(result)
        # self.r.robot.set_expression(random.choice(self.pos_face), 
            # random.choice(self.pos_line))
    
    def forward(self):
        self.move(self.dist, 0, 0)
        
    def backward(self):
        self.move(0, 0, 180)
        self.forward()
        
    def right(self):
        self.move(0, 0, -90)
        self.forward()
    
    def left(self):
        self.move(0, 0, 90)
        self.forward()
        
    def move_head(self, pitch):
        # In Zenbo junior the range is -10(down) to 50(up)
        result = self.r.motion.move_head(yaw_degree=0, 
                pitch_degree=pitch, 
                speed_level=3, 
                sync=False, 
                timeout=None)

if __name__ == '__main__':
    host = '192.168.0.126'
    robot = myRobot(host)
    print('forward')
    # robot.forward()
    # robot.backward()
    robot.right()
    robot.left()
    # robot.move_head(pitch=10)
    
    # robot.release()