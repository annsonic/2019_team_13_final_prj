import os
base_dir = os.path.abspath(os.path.dirname(__file__))
import random
import json
import time

import pyzenbo
from pyzenbo.modules.dialog_system import RobotFace
from pyzenbo.modules.utility import PlayAction
from constants import unit_pace_length
from constants import head_pitch


class myRobot():
    def __init__(self, host=None):
        self.r = pyzenbo.connect(host)
        
        # self.r.on_result_callback = self.on_result
        self.dist = unit_pace_length
        
        self.heading = 90
        
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
        
        self.former_line_index = None
        self.former_phrase_index = 0
        self.list_motion_line = [
            ['一二三 到臺灣', '臺灣有個阿里山', '阿里山上有神木', '我們一起去看樹'],
            ['一二三 到臺灣', '臺灣有個阿里山', '小火車啊嘟嘟嘟', '帶我們一起看日出'],
            ['小皮球 香蕉油', '滿地開花二十一', '二五六 二五七', '二八 二九 三十一'],
            ['城門城門幾丈高', '三十六丈高', '騎白馬 帶把刀', '走進城門滑一跤'],
            ['小老鼠 上燈台', '偷油吃 下不來', '叫媽媽 媽不來', '嘰哩咕嚕咕嚕滾下來'],
            ['三輪車 跑得快', '上面坐個老太太', '要五毛 給一塊', '你說奇怪不奇怪'],
            ['一角兩角三角錢', '四角五角六角半', '七角八角手插腰', '十一角十二角打電話',
             '喂 你家媽媽在不在', '不在 不在 去買菜'],
            ['星期一猴子穿新衣', '星期二猴子肚子餓', '星期三猴子去爬山',
             '星期四猴子看電視', '呈期五猴子去跳舞', '星期六猴子去斗六',
             '星期七猴子擦油漆', '星期八猴子吹喇叭', '星期九猴子去喝酒'],
            ['炒羅蔔 炒羅蔔 切 切 切', '包餃子 包餃子 捏 捏 捏', 
             '好孩子 好孩子 摸 摸 頭', '壞孩子 壞孩子 打嘴巴'],
            ['新年到 大團圓', '橘子年糕壓歲錢', '吃了糖果嘴甜甜', '大吉大利過新年'],
            ['新年祝福你', '好運伴著你', '財神跟著你', '名車美女屬於你', 
             '黴運躲著你', '喜事圍繞你'],
            ['yes sir'], ['go go go'], ['lets go'], ['嘿嘿'], ['a piece of cake'],
            ['Here we go 啊壘啊雷啊雷'], ['ok'],
            ['啦 啦 阿 阿 阿', '馬 馬 嗎 媽 媽', '嘎嘎 嗚 啦啦', 'Want your bad romance']
            ]
        
    def release(self):
        self.r.release()
        
    def on_result(self, **args):
        if args['cmd'] != 31:
            print('on_result', args)
        
    def say(self, line="Hi", mood="positive"):
        # self.move_head(pitch=head_pitch)
        self.r.robot.set_expression(random.choice(self.face[mood]), line, 
            sync=False, timeout=1)
        self.r.robot.set_expression(RobotFace.DEFAULT, " ", sync=True, timeout=1)
        
    def motion_say(self):
        # self.move_head(pitch=head_pitch)
        
        if (self.former_line_index is None):
            self.former_line_index = 0
            self.former_phrase_index = 0
            
        elif self.former_phrase_index == len(self.list_motion_line[self.former_line_index]):
            self.former_line_index = random.choice(range(len(self.list_motion_line)))
            self.former_phrase_index = 0
            
        # speak
        self.r.robot.set_expression(random.choice(self.face["positive"]), 
            self.list_motion_line[self.former_line_index][self.former_phrase_index], 
            sync=True, timeout=1)
        self.former_phrase_index += 1
            
    def move(self, x, y, theta, speed_level=1):
        self.move_head(pitch=30)
        result = self.r.motion.move_body(relative_x=x, 
                relative_y=y, 
                relative_theta_degree=theta, 
                speed_level=speed_level,
                sync=True, 
                timeout=15)
        # print(result)
        
        # self.move_head(pitch=10)
    
    def forward(self):
        
        self.motion_say()
        # self.move_head(pitch=10)
        self.move(self.dist, 0, 0, speed_level=3)
        
        # To prevent hitting box
        self.backward()
        
    def backward(self):
        self.r.motion.remote_control_body(
            direction=2, sync=True, timeout=1)
        
        time.sleep(0.7)
        self.r.motion.remote_control_body(
            direction=0, sync=True, timeout=1)
        
    def right(self):
        self.motion_say()
        # self.move_head(pitch=10)
        self.move(0, 0, -90, speed_level=3)
        # self.move(self.dist, 0, 0)
    
    def left(self):
        self.motion_say()
        # self.move_head(pitch=10)
        self.move(0, 0, 90, speed_level=3)
        # self.move(self.dist, 0, 0)
        
    def move_head(self, pitch):
        # In Zenbo junior the range is -10(down) to 50(up)
        result = self.r.motion.move_head(yaw_degree=0, 
                pitch_degree=pitch, 
                speed_level=3, 
                sync=True, 
                timeout=None)
                
    def nod(self, mood):
        self.r.utility.play_emotional_action(
            face=random.choice(self.face[mood]), 
            play_action=PlayAction.NOD_1,          
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
        
        self.move_head(pitch=head_pitch)
        
        result = self._detect_f()
        
        # trial = 0
        # while (result is None):
            # result = self._detect_f()
            # trial += 1
            # if trial > 4:
                # break
            # self.r.motion.move_body(relative_x=x, 
                # relative_y=y, 
                # relative_theta_degree=theta, 
                # speed_level=3,
                # sync=True, 
                # timeout=15)
                
        # if result is not None:
            # if len(result)==1:
                # str_dict_xyz = result[0]['context']['nameValuePairs']['faceLoc']
                # dict_xyz = json.loads(str_dict_xyz)
                # print('------detect------', dict_xyz['y'])
                   
            
        # self.r.robot.set_expression(RobotFace.DEFAULT, " ", sync=False, timeout=1)
        # TODO: zenbo see user face to face

if __name__ == '__main__':
    host = "192.168.43.97"
    robot = myRobot(host)
    
    
    # robot.r.motion.move_body(relative_x=0.5, 
                # relative_y=0, 
                # relative_theta_degree=0, 
                # speed_level=3,
                # sync=False, 
                # timeout=15)
    
    
    # robot.r.robot.set_expression(RobotFace.HAPPY, "哈  哈  哈", 
            # sync=True, timeout=1)
    # robot.r.robot.set_expression(RobotFace.HAPPY, "你需要做復健了", 
            # sync=True, timeout=1)
    # robot.r.robot.set_expression(RobotFace.SHY, "", 
            # sync=True, timeout=1)
            
    # robot.r.robot.set_expression(RobotFace.HAPPY, "嘎 嘎 烏拉拉", 
            # sync=True, timeout=1)
    # robot.r.robot.set_expression(RobotFace.HAPPY, "嚕 八 嚕巴巴", 
            # sync=True, timeout=1)
    # robot.r.robot.set_expression(RobotFace.HAPPY, "頂叮叮叮頂丁", 
            # sync=True, timeout=1)
    
    # robot.motion_say()
    # print('forward')
    robot.forward()
    
    robot.right()
    robot.forward()
    
    robot.left()
    robot.left()
    robot.forward()
    # robot.move_head(pitch=30)
    
    # robot.release()