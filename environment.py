import os
import sys
import pygame
import numpy as np
base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'pySokoban'))
sys.path.append(os.path.join(base_dir, 'SokobanSolver'))

import pySokoban
from pySokoban.sokoban import mySokoban

from threading import Thread
import SokobanSolver
import SokobanSolver.sokoban as Solver_s
import SokobanSolver.search as search
import SokobanSolver.puzzler as puzzler
from puzzler import *

from zenbo_junior import myRobot
from constants import MPI_Rank
from constants import RobotMotion
from constants import has_robot
from constants import host
from constants import current_level
from constants import level_set
from constants import wait_time


class Solver(Thread):
    def __init__(self, level_set, current_level):
        super().__init__()
        self.warehouse = Solver_s.Warehouse()
        pySokoban_root = os.path.join(base_dir, 'pySokoban')
        maze_path = os.path.join(pySokoban_root, 'levels', level_set)
        self.warehouse.read_warehouse_file(
			os.path.join(maze_path, 'level'+str(current_level)))
        
        self.puzzle = SokobanPuzzle(self.warehouse)
        self.solution = None
        self.path = []
        self.started = False
        self.list_actions = []

    def run(self):
        self.solution = search.breadth_first_graph_search(self.puzzle)

        self.list_actions = [node.action for node in self.solution.path()]
        self.list_actions.pop(0)
        # print(list_event)
        
    def stop(self):
        self.stopped = True
        
    def parse_matrix_to_str(self, matrix):
        # print(self.myLevel.matrix)
        ret = []
        for list_m in matrix:
            s = "".join(str(m) for m in list_m)
            s += "\n"
            ret.append(s)
        # return ret
        self.warehouse.extract_locations(ret)
        
class Components():
    def __init__(self, comm):
        self.comm = comm
        if has_robot:
            if host != "":
                self.robot = myRobot(host)
            else:
                raise ValueError("Xinyi: missing param host")
                sys.exit(1)
        clock = pygame.time.Clock()
        self.dt = clock.tick(30) / 1000  
        # Makes the program halt for 'time' seconds
        
        self.game = mySokoban(level=current_level)
        self.game.initLevel()
        
        self.wait_time = wait_time
        

    def get_solution(self):
        self.solution = Solver(level_set, current_level)
        # print('self.game.myLevel.matrix \n', self.game.myLevel.matrix)
        # sys.stdout.flush()
        self.solution.parse_matrix_to_str(self.game.myLevel.matrix)
        self.solution.start()
        self.solution.join()
        self.solution.stop()
            
        print('\tlen of solution', len(self.solution.list_actions))
        sys.stdout.flush()
    
    def play(self):
        # 
        while True:
            # self.wait_time -= self.dt
            # if self.wait_time <= 0:
                # # TODO: call help
                # print("[INFO] Do you need help?")
                # response = input()
                # sys.stdout.flush()
                # if (response == "y") or (response == "Y"):
                    # self.get_solution()
                # self.wait_time = wait_time
                
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
                str_status = self.game.movePlayer("L")
                if has_robot and (str_status != "\tThere is a wall here"):
                    self.robot.left()
            elif inst == RobotMotion.RIGHT:
                str_status = self.game.movePlayer("R")
                if has_robot and (str_status != "\tThere is a wall here"):
                    self.robot.right()
            elif inst == RobotMotion.BACKWARD:
                str_status = self.game.movePlayer("D")
                if has_robot and (str_status != "\tThere is a wall here"):
                    self.robot.backward()
            elif inst == RobotMotion.FORWARD:
                str_status = self.game.movePlayer("U")
                if has_robot and (str_status != "\tThere is a wall here"):
                    self.robot.forward()
            elif inst == RobotMotion.EXIT:
                pygame.quit()
                break
            elif inst == RobotMotion.HELP:
                if has_robot:
                    # TODO: ask & listen
                    self.robot.say(line='沒問題 我一定會幫你的', mood="positive")
                self.get_solution()

def welcome(comm):
    # comm.send((Instruction.NOD,"positive"), dest=MPI_Rank.ROBOT)
    
    list_dict = [{"sentence": "哈囉 帥氣的大哥哥你好", "mood": "positive"},
                 {"sentence": "我們一起玩個小遊戲好嗎", "mood": "positive"}]
    # TODO: robot speak
    print(list_dict)
    sys.stdout.flush()
    comm.send((True,), dest=MPI_Rank.MASTER)

def main(comm):
    game_components = Components(comm)
    game_components.play()