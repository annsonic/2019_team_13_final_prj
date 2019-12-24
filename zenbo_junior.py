import os
base_dir = os.path.abspath(os.path.dirname(__file__))
import random
import pyzenbo
from pyzenbo.modules.dialog_system import RobotFace
from pyzenbo.modules.utility import PlayAction
from constants import unit_pace_length


class myRobot():
    def __init__(self, host=None):
        self.r = pyzenbo.connect(host)
        
        # self.r.on_result_callback = self.on_result
        self.dist = unit_pace_length
        self.face = { # RobotFace.SINGING,
        "positive": [RobotFace.DEFAULT, RobotFace.DEFAULT_STILL, 
                     RobotFace.CONFIDENT, RobotFace.INTERESTED, 
                     RobotFace.HAPPY, RobotFace.PLEASED, 
                     RobotFace.PROUD,  
                     RobotFace.ACTIVE, RobotFace.AWARE_LEFT, 
                     RobotFace.AWARE_RIGHT],
        "negative": [RobotFace.SHY, RobotFace.EXPECTING, RobotFace.INNOCENT,
                     RobotFace.SHOCKED, RobotFace.DOUBTING]
                    }
        self.pos_line = ['yes sir', 'go go go', 'lets go', 'ok', 'hey hey',
                         'a piece of cake']
        
    def release(self):
        self.r.release()
        
    def on_result(self, *args):
        print('on_result', args)
        
    def say(self, line="Hi", mood="positive"):
        self.r.robot.set_expression(random.choice(self.face[mood]), line, sync=False, timeout=1)
        self.r.robot.set_expression(RobotFace.DEFAULT, " ", sync=False, timeout=1)
        
    def move(self, x, y, theta):
        self.move_head(pitch=30)
        result = self.r.motion.move_body(relative_x=x, 
                relative_y=y, 
                relative_theta_degree=theta, 
                speed_level=3,
                sync=True, 
                timeout=15)
        # print(result)
        
        self.move_head(pitch=10)
    
    def forward(self):
        self.r.robot.set_expression(random.choice(self.face["positive"]), 
            random.choice(self.pos_line), sync=False, timeout=1)
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
                
    def nod(self, mood):
        self.r.utility.play_emotional_action(
            face=random.choice(self.face[mood]), 
            play_action=PlayAction.SHAKE_HEAD_1,          
            sync=False, timeout=1)
            
    def _detect_f(self):
        self.r.vision.request_detect_person(
            interval=1,
            enable_debug_preview=True,
            enable_detect_head=True,
            sync=False,
            timeout=10)
        result = self.r.vision.wait_for_detect_face(
                             interval=1,
                             enable_debug_preview=True,
                             enable_detect_head=True,
                             enable_face_posture=True,
                             enable_candidate_obj=True,
                             enable_head_gaze_classifier=False,
                             timeout=10)
        return result
        
    def detect_face(self):
        self.r.robot.set_expression(RobotFace.HIDEFACE, " ", sync=False, timeout=1)
        result = self._detect_f()
        
        # When can not detect before timeout, result = None
        # Sample of found (person is at Zenbo's right-hand side)
        # detect [{'context': {'nameValuePairs': {'uuid': 'IID:-15', 
                                                  # 'tid': 3, 
                                                  # 'faceLoc': '{"x":-0.16414534,"y":-0.116298735,"z":1.0603619}', 
                                                  # 'faceAngle': '{"x":-1.2512693,"y":11.677047,"z":-0.43951565}', 
                                                  # 'faceBox': '{"bottom":0.0,
                                                               # "faceUp":{"x":0.0,"y":0.0,"z":0.0},
                                                               # "left":0.0,
                                                               # "lookAt":{"x":0.0,"y":0.0,"z":0.0},
                                                               # "right":0.0,
                                                               # "top":0.0}', 
                                                               # 'faceEmotion': 0, 
                                                               # 'faceLocCam': '{"h_height":0.14375,
                                                                               # "h_width":0.1078125,
                                                                               # "x":0.625,
                                                                               # "y":0.65625}', 
                                                               # 'validHeadROI': True, 
                                                               # 'validDepth': True, 
                                                               # 'candidate': False, 
                                                               # 'gazeDirection': '"GAZE_NOT_KNOWN"', 
                                                               # 'headPoseConfidence': 100, 
                                                               # 'recognitionScore': '{}'
                                                               # }}}]
        trial = 0
        while (result is None) and (trial < 3):
            self.r.motion.move_body(
                relative_x=0.0, relative_y=0, relative_theta_degree=90,
                speed_level=1, sync=False, timeout=1)
            
            result = self._detect_f()
            trial += 1
            
        self.r.robot.set_expression(RobotFace.DEFAULT, " ", sync=False, timeout=1)
        # TODO: zenbo see user face to face

if __name__ == '__main__':
    host = '192.168.0.126'
    robot = myRobot(host)
    # print('forward')
    # robot.forward()
    # robot.backward()
    # robot.right()
    robot.left()
    # robot.move_head(pitch=30)
    
    # robot.release()