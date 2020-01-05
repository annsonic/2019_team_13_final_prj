import os
import sys
import pygame
import numpy as np
import copy
import time
base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'pySokoban'))
# sys.path.append(os.path.join(base_dir, 'SokobanSolver'))

import pySokoban
from pySokoban.sokoban import mySokoban

from zenbo_junior import myRobot
from image_parser import ImgParser
from path_planning import Solver
from path_planning import which_box
from path_planning import calibrate_world
from constants import MPI_Rank
from constants import RobotMotion
from constants import has_robot
from constants import host
from constants import current_level
from constants import level_set
from constants import wait_time

        
class Components():
    def __init__(self, comm):
        self.comm = comm
        if has_robot:
            if host != "":
                self.robot = myRobot(host)
            else:
                raise ValueError("Xinyi: missing param host")
                sys.exit(1)
        
        self.game = mySokoban(level=current_level)
        self.game.initLevel()
        
        self.wait_time = wait_time
        self.list_suggestion = []
        self.renew_suggestion = True
        
        [self.num_row, self.num_col] = self.game.myLevel.getSize()
        self.parser = ImgParser(num_col=self.num_col, num_row=self.num_row)

    def get_solution(self, matrix):
        self.solution = Solver(level_set, current_level)
        # print('\treceive matrix \n\t', matrix)
        # sys.stdout.flush()
        self.solution.parse_matrix_to_str(matrix)
        self.solution.start()
        self.solution.join()
        self.solution.stop()
            
        self.list_suggestion = copy.deepcopy(self.solution.list_actions)
    
    def give_suggestion(self):
        count = 0
        while (len(self.list_suggestion)== 0):
            if count == 0:
                matrix = copy.deepcopy(self.game.myLevel.matrix)
            else:
                matrix = copy.deepcopy(self.game.myLevel.matrix_history[count])
            count -= 1
            
            self.get_solution(matrix)
        # print('count', count)
        # print('\tlen of solution', len(self.list_suggestion))
        # sys.stdout.flush()
        
        
        
        # # Pop out wrong history
        # flag_undo = False
        # while count <-1:
            # print('\t===undo move===')
            # sys.stdout.flush()
            # self.game.myLevel.getLastMatrix()
            
            # count += 1
            # flag_undo = True
            # self.game.drawLevel(self.game.myLevel.matrix)
            
        # # Tell which box is our first target
        # mind_list_boxes_pos = self.game.myLevel.getBoxes()
        # mind_player_pos = self.game.myLevel.getPlayerPosition()
        # first_box = which_box(mind_player_pos, mind_list_boxes_pos, self.list_suggestion)
        # print('\t===fisrt target box is at {}==='.format(first_box))
        # sys.stdout.flush()
        # # TODO: robot turns and faces first_box then says
        
        # # Calibrate the objects in physical world
        # if flag_undo:
            # # TODO: getBoxes
            # world_player_pos = [3, 2]
            # world_list_boxes_pos = [[4,4],[3,5],[4,5]]
            # # print('\tmind_list_boxes_pos, mind_player_pos', mind_list_boxes_pos, mind_player_pos)
            # # sys.stdout.flush()
            # # TODO: check mismatches and robot says let me undo
            # [num_row, num_col] = self.game.myLevel.getSize()
            # calibrate_world(world_player_pos, 
                    # world_list_boxes_pos,
                    # mind_player_pos,
                    # mind_list_boxes_pos,
                    # num_row, num_col)
            # # TODO: robot pushes the boxes back
            
            # flag_undo = False
    
    def play(self):
        print("== Enter play ==")
        sys.stdout.flush()
        
        while True:
            data = self.comm.recv(source=MPI_Rank.MASTER)
            # data = np.zeros(1, dtype=float)
            # req = self.comm.Irecv(buf=data, source=MPI_Rank.MASTER)
            # found = req.Test()
            # if not found:
                # continue
            inst = data[0]
            print("\tinst", inst)
            sys.stdout.flush()

            event = pygame.event.poll() 
            # work-around for pygame.display.update() got stuck
            
            if inst == RobotMotion.LEFT:
                self.robot.heading += 90
                self.robot.left()
                
            elif inst == RobotMotion.RIGHT:
                self.robot.heading -= 90
                self.robot.right()
                
            elif inst == RobotMotion.FORWARD:
                
                if (abs(self.robot.heading)%360 == 90):
                    str_status = self.game.movePlayer("U")
                    self.robot.heading = 90
                
                elif (abs(self.robot.heading)%360 == 180):
                    str_status = self.game.movePlayer("L")
                    self.robot.heading = 180
                    
                elif (abs(self.robot.heading)%360 == 0):
                    str_status = self.game.movePlayer("R")
                    self.robot.heading = 0
                    
                elif (abs(self.robot.heading)%360 == 270):
                    str_status = self.game.movePlayer("D")
                    self.robot.heading = 270
                
                
                if has_robot and (str_status == "can_move"):
                    self.robot.forward()
                elif str_status == "\tThere is a wall here":
                    self.robot.say(line="不行走 會撞牆啦", mood="negative")
                elif str_status == "can_not_move":
                    self.robot.say(line="太重了 我推不動", mood="negative")
                print(self.game.myLevel.matrix)
                sys.stdout.flush()
                
                flag_win = self.game.check_boxes()
                if flag_win:
                    self.robot.say(line="恭喜破關 你太厲害了", mood="positive")
                    pygame.quit()
                    break
                    
                self.renew_suggestion = True
                
            elif inst == RobotMotion.EXIT:
                pygame.quit()
                if host != "":
                    self.robot.release()
                break
            elif inst == RobotMotion.HELP:
                if has_robot:
                    # TODO: ask & listen
                    self.robot.say(line='算了 我自己來吧', mood="positive")
                
                if (self.renew_suggestion):# or (len(self.list_suggestion)==0):
                    self.list_suggestion = []
                    self.give_suggestion()
                    self.renew_suggestion = False
                    
                    
                    
                    for a_idx, action in enumerate(self.list_suggestion):
                        event = pygame.event.poll() 
                        # work-around for pygame.display.update() got stuck
                        
                        if action == "Left":
                            str_status = self.game.movePlayer("L")
                            self.robot.move(0, 0, 90, speed_level=1)
                            self.robot.move(0.185, 0, 0, speed_level=3)
                            # self.robot.backward()
                            self.robot.move(0, 0, -90, speed_level=3)
                            
                        elif action == "Right":
                            str_status = self.game.movePlayer("R")
                            self.robot.move(0, 0, -90, speed_level=1)
                            self.robot.move(0.185, 0, 0, speed_level=3)
                            # self.robot.backward()
                            self.robot.move(0, 0, 90, speed_level=3)
                            
                        elif action == "Up":
                            str_status = self.game.movePlayer("U")
                            self.robot.move(0.185, 0, 0, speed_level=3)
                            # self.robot.backward()
                        elif action == "Down":
                            str_status = self.game.movePlayer("D")
                            self.robot.move(0, 0, 180, speed_level=1)
                            self.robot.move(0.185, 0, 0, speed_level=3)
                            # self.robot.backward()
                            self.robot.move(0, 0, -180, speed_level=3)
                        
                    print(self.list_suggestion)
                    sys.stdout.flush()
                    self.robot.say(line='你太遜了', mood="negative")
                    
                break
                    
    def chat(self):
        # open camera
        
        dict_r = {"sentence": "請等我整理一下場地", "mood": "positive"}
        if host != "":
                self.robot.say(line=dict_r["sentence"], mood=dict_r["mood"])
                
                
        list_dict = [{"sentence": "對了 告訴你一個小秘密哦", "mood": "positive"},
                     {"sentence": "我是機器人學的守護神之一", "mood": "positive"},
                     {"sentence": "所以萬一你卡關太久了", "mood": "positive"},
                     {"sentence": "我會主動提供破關提示", "mood": "positive"},
                     ]

        for d in list_dict:
            print(d["sentence"])
            sys.stdout.flush()
            if host != "":
                self.robot.say(line=d["sentence"], mood=d["mood"])
        
        
        self.parser.update_point()
        [world_player_pos] = parser.find_index_on_puzzle("robot")
        world_list_boxes_pos = parser.find_index_on_puzzle("box")
        mind_list_boxes_pos = self.game.myLevel.getBoxes()
        mind_player_pos = self.game.myLevel.getPlayerPosition()
        
        calibrate_world(world_player_pos, 
                    world_list_boxes_pos,
                    mind_player_pos,
                    mind_list_boxes_pos,
                    num_row, num_col)
        
        print("== Exit chat ==")
        sys.stdout.flush()

def welcome(comm):
    user_angle = 0
    if host != "":
        robot = myRobot(host)
        robot.detect_face()
    
    list_dict = [{"sentence": "哈囉 帥氣的大哥哥你好", "mood": "positive"},
                 {"sentence": "我們一起玩個小遊戲好嗎", "mood": "positive"}]

    for d in list_dict:
        print(d["sentence"])
        sys.stdout.flush()
        if host != "":
            robot.say(line=d["sentence"], mood=d["mood"])
            
    
    if host != "":
        # wait zenbo stops talking
        time.sleep(5)
        # robot.release()
    # Sync with MASTER 
    comm.send((True,), dest=MPI_Rank.MASTER)
    print("== Exit welcome ==")
    sys.stdout.flush()

def training_user(comm):
    if host != "":
        robot = myRobot(host)
    
    list_dict = [{"sentence": "請你用手勢控制我行動", "mood": "positive"},
                 {"sentence": "要依我的正面來判斷前後左右唷", "mood": "positive"},
                 {"sentence": "我們先來練習一下咩", "mood": "positive"}]
    for d in list_dict:
        print(d["sentence"])
        sys.stdout.flush()
        if host != "":
            robot.say(line=d["sentence"], mood=d["mood"])
            # wait zenbo stops talking
            time.sleep(1)
    
    list_list_dict = [
                 (RobotMotion.FORWARD, [{"sentence": "出拳是前進 請你出拳", 
                                         "direction": "前進",
                                         "mood": "positive"}]),
                 (RobotMotion.RIGHT, [{"sentence": "手掌朝右是走右邊 請你指揮", 
                                       "direction": "往右",
                                       "mood": "positive"}]),
                 (RobotMotion.LEFT, [{"sentence": "手掌朝左是走左邊 請你指揮", 
                                      "direction": "往左",
                                      "mood": "positive"}]),
                 # (RobotMotion.BACKWARD, [{"sentence": "手掌張開是後退 請你張開手掌", 
                                          # "direction": "後退",
                                          # "mood": "positive"}])
                 ]
    
    
    for (gesture, list_dict) in list_list_dict:
        print(list_dict[0]["sentence"])
        sys.stdout.flush()
        if host != "":
            robot.say(line=list_dict[0]["sentence"], mood=list_dict[0]["mood"])
            time.sleep(3)
        # timeout = 0
        # while True:
            # Sync with MASTER 
            print("== Robot Send instruction ==")
            sys.stdout.flush()
            comm.send((RobotMotion.HELP,gesture), dest=MPI_Rank.MASTER)
            
            while True:
                data = comm.recv(source=MPI_Rank.MASTER)
                inst = data[0]
                # # if timeout == 0:
                    # # inst = data[0]
                print("\trobot got inst", inst)
                sys.stdout.flush()
                
                if inst == gesture:
                    if host != "":
                        if inst == RobotMotion.LEFT:
                            robot.left()
                        elif inst == RobotMotion.RIGHT:
                            robot.right()
                        elif inst == RobotMotion.BACKWARD:
                            robot.backward()
                        elif inst == RobotMotion.FORWARD:
                            robot.forward()
                    break
                # if timeout > 10000:
                    # if host != "":
                        # robot.say(line="哎呀 可能Myo認錯手勢了 看成{}",
                                  # mood="negative")
                        # robot.say(line="請你再做一次{}手勢哦".format(list_dict[0]["direction"]), 
                                  # mood="negative")
                    # timeout = 0
                # timeout += 1
            
    if host != "":
        robot.release()
    # Sync with MASTER 
    comm.send((RobotMotion.EXIT,), dest=MPI_Rank.MASTER)
    print("== Exit training_user ==")
    sys.stdout.flush()

def main(comm):
    game_components = Components(comm)
    
    # game_components.chat()
    
    game_components.play()