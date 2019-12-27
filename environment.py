import os
import sys
import pygame
import numpy as np
import copy
base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'SokobanSolver'))
sys.path.append(os.path.join(base_dir, 'pySokoban'))
import pySokoban
# from pySokoban import sokoban
from pySokoban.sokoban import mySokoban
# sys.path.append(os.path.join(base_dir, 'Vision'))
# from Vision import coordinates
# from coordinates import imgParser
# from pySokoban.Level import Level
from threading import Thread
import SokobanSolver
import SokobanSolver.sokoban as Solver_s
import SokobanSolver.puzzler as puzzler
import SokobanSolver.search as search
from puzzler import *
from zenbo_junior import myRobot
from constants import MPI_Rank
from constants import Instruction
from constants import MyoGesture
from constants import RobotMotion
from constants import current_level
from constants import level_set


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
        
    def parse_matrix_to_str(self, matrix):
        # print(self.myLevel.matrix)
        ret = []
        for list_m in matrix:
            s = "".join(str(m) for m in list_m)
            s += "\n"
            ret.append(s)
        # return ret
        self.warehouse.extract_locations(ret)



def play(comm, rank, robot):
    while True:
        data = comm.recv(source=MPI_Rank.USER)
        inst = data[0]
        print('user_inst', inst)
        sys.stdout.flush()
        
        if (inst == RobotMotion.BACKWARD):
            robot.backward()
        elif (inst == RobotMotion.RIGHT):
            robot.right()
        elif (inst == RobotMotion.LEFT):
            robot.left()
        elif (inst == RobotMotion.FORWARD):
            robot.forward()
        elif (inst == RobotMotion.EXIT):
            break

def main(comm, rank):
    
    while True:
        data = comm.recv(source=MPI_Rank.MASTER)
        inst = data[0]
        print('inst', inst)
        sys.stdout.flush()
        if (inst == Instruction.INIT):
            if len(data) == 3:
                host = data[1]
                cam_id = data[2]
            else:
                raise ValueError("Xinyi: missing param host")
                sys.exit(1)
            
            robot = myRobot(host)
            
            reqs = []
            reqs.append(comm.isend((Instruction.INIT,cam_id), dest=MPI_Rank.CAMERA))
            reqs.append(comm.isend((Instruction.DISPLAY,), dest=MPI_Rank.CAMERA))
            for req in reqs:
                req.wait()
        
        elif (inst == Instruction.SPEAK):
            if len(data) == 2:
                list_dict = data[1]
                # print(list_dict)
            else:
                raise ValueError("Xinyi: missing param list_args")
                sys.exit(1)
            for d in list_dict:
                robot.say(line=d["sentence"], mood=d["mood"])
        
        elif (inst == Instruction.NOD):
            if len(data) == 2:
                mood = data[1]
            else:
                raise ValueError("Xinyi: missing param mood")
                sys.exit(1)
            robot.nod(mood)
        
        elif (inst == Instruction.DETECT_FACE):
            robot.detect_face()
        
        elif (inst == Instruction.ROBOT_GUIDE):
            if len(data) == 2:
                (gesture, list_dict) = data[1]
            else:
                raise ValueError("Xinyi: missing param (gesture, list_dict)")
                sys.exit(1)
            
            for d in list_dict:
                robot.say(line=d["sentence"], mood=d["mood"])
            ## TODO: listen to User
            # response = comm.recv(source=MPI_Rank.USER)
            # if response == gesture:
                # robot.move(mood)
            # if gesture == MyoGesture.FIST:
                # print('xinyi', 'Bingo!!!')
                ## TODO: tell master go next step
                # comm.send((Instruction.ROBOT_GUIDE, True), dest=MPI_Rank.ROBOT)
            # else:
            #   robot.say(line="哎呀Myo認錯手勢了 請你再做一次手勢", mood="negative")
        elif (inst == Instruction.PLAY):
            print('--- Lets play ---')
            play(comm, rank, robot)
            
        elif (inst == Instruction.EXIT):
            if robot is not None:
                robot.release()
            comm.send((Instruction.EXIT,), dest=MPI_Rank.CAMERA)
            break
        
        else:
            print('Invalid instruction in environment.py!!!!')
            sys.exit(1)
            
        
def pseudo_play(comm, rank, game, 
        times=1, help_ing=False, list_actions=[], current_suggestion = ""):
    
    counter = 0
    while (counter < times):
        comm.send((Instruction.DISPLAY,), dest=MPI_Rank.CAMERA)
        print('\tenv call camera')
        sys.stdout.flush()

        
        data = comm.recv(source=MPI_Rank.USER)
        inst = data[0]
        
        print("Robot Play", inst)
        sys.stdout.flush()
        
        counter += 1
        event = pygame.event.poll() # work-around for pygame.display.update() got stuck
        if inst == RobotMotion.LEFT:
            if help_ing:
                if current_suggestion != "Left":
                    print("Ohhh, please pose {} again".format(current_suggestion))
                    sys.stdout.flush()
                    return False
                else:
                    if len(list_actions)>0:
                        current_suggestion = list_actions.pop(0)
                        print('Next, please move {}'.format(current_suggestion))
                        sys.stdout.flush()
            print('\tleft')
            sys.stdout.flush()
            game.movePlayer("L")
            
            
        elif inst == RobotMotion.RIGHT:
            if help_ing:
                if current_suggestion != "Right":
                    print("Ohhh, please pose {} again".format(current_suggestion))
                    sys.stdout.flush()
                    return False
                else:
                    if len(list_actions)>0:
                        current_suggestion = list_actions.pop(0)
                        print('Next, please move {}'.format(current_suggestion))
                        sys.stdout.flush()
            print('\tright')
            sys.stdout.flush()
            game.movePlayer("R")
        elif inst == RobotMotion.BACKWARD:
            if help_ing:
                if current_suggestion != "Down":
                    print("Ohhh, please pose {} again".format(current_suggestion))
                    sys.stdout.flush()
                    return False
                else:
                    if len(list_actions)>0:
                        current_suggestion = list_actions.pop(0)
                        print('Next, please move {}'.format(current_suggestion))
                        sys.stdout.flush()
            print('\tbackward')
            sys.stdout.flush()
            game.movePlayer("D")
        elif inst == RobotMotion.FORWARD:
            if help_ing:
                if current_suggestion != "Up":
                    print("Ohhh, please pose {} again".format(current_suggestion))
                    sys.stdout.flush()
                    return False
                else:
                    if len(list_actions)>0:
                        current_suggestion = list_actions.pop(0)
                        print('Next, please move {}'.format(current_suggestion))
                        sys.stdout.flush()
            print('\tforward')
            sys.stdout.flush()
            game.movePlayer("U")
        elif inst == RobotMotion.HELP:
            print('\tCall for solution')
            sys.stdout.flush()
            help_ing = True
            
            solution = Solver(level_set, current_level)
            solution.parse_matrix_to_str(game.myLevel.matrix)
            solution.start()
            solution.join()
            
            # print('len', len(solution.list_actions))
            list_actions = copy.copy(solution.list_actions)
            if len(solution.list_actions)>0:
                current_suggestion = list_actions.pop(0)
                print('Please move {}'.format("Left"))
                sys.stdout.flush()
        elif inst == RobotMotion.EXIT:
            break
            
        if (len(game.myLevel.getBoxes()) == 0):
            print("Level Completed")
            sys.stdout.flush()
            comm.send((Instruction.EXIT,), dest=MPI_Rank.USER)
            break
        else:
            comm.send((Instruction.PLAY,), dest=MPI_Rank.USER)
            
    return True

def pseudo_main(comm, rank):
    while True:
        data = comm.recv(source=MPI_Rank.MASTER)
        inst = data[0]
        
        print("Env", inst)
        sys.stdout.flush()
        if inst == Instruction.INIT:
            if len(data) == 3:
                cam_id = data[2]
            else:
                raise ValueError("Xinyi: missing param cam_id")
                sys.exit(1)
            
            reqs = []
            reqs.append(comm.isend((Instruction.INIT,cam_id), dest=MPI_Rank.CAMERA))
            reqs.append(comm.isend((Instruction.DISPLAY,), dest=MPI_Rank.CAMERA))
            for req in reqs:
                req.wait()
            
            game = mySokoban(level=current_level)
            game.initLevel()
        elif (inst == Instruction.DETECT_FACE):
            pass
        elif (inst == Instruction.SPEAK):
            pass
        elif (inst == Instruction.ROBOT_GUIDE):
            print('--- Lets practice ---')
            sys.stdout.flush()
            
            if len(data) == 2:
                (gesture, list_dict) = data[1]
            else:
                raise ValueError("Xinyi: missing param (gesture, list_dict)")
                sys.exit(1)
            
            for d in list_dict:
                print(d["sentence"])
                sys.stdout.flush()
                
            comm.send(("start",), dest=MPI_Rank.USER)
            print('\tenv call user', 'True')
            sys.stdout.flush()
        
            ret = pseudo_play(comm, rank, game, times=1, 
                help_ing=True, list_actions=[], current_suggestion = gesture)
            
            print('\tenv got', ret)
            sys.stdout.flush()
            comm.send(ret, dest=MPI_Rank.MASTER)
            
            
        elif (inst == Instruction.PLAY):
            print('--- Lets play ---')
            sys.stdout.flush()
            pseudo_play(comm, rank)
        elif (inst == Instruction.EXIT):
            comm.send((Instruction.EXIT,), dest=MPI_Rank.CAMERA)
            print('--- camera bye~ ---')
            sys.stdout.flush()
            break
        else:
            print('!!!! Invalid instruction in envronment !!!!')
            sys.stdout.flush()
            sys.exit(1)
            
    

if __name__ == '__main__':
    comm = None
    rank = None
    main(comm, rank)