import os
import sys
base_dir = os.path.abspath(os.path.dirname(__file__))
# sys.path.append(os.path.join(base_dir, 'Vision'))
# sys.path.append(os.path.join(base_dir, 'pySokoban'))
# from Vision import coordinates
# from coordinates import imgParser
# from pySokoban.Level import Level
from zenbo_junior import myRobot
from constants import MPI_Rank
from constants import Instruction
from constants import MyoGesture
from constants import RobotMotion


def init(host):
    robot = myRobot(host)
    return robot

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
    robot = None
    
    while True:
        data = comm.recv(source=MPI_Rank.MASTER)
        inst = data[0]
        print('inst', inst)
        sys.stdout.flush()
        if (inst == Instruction.INIT):
            if len(data) == 2:
                host = data[1]
            else:
                raise ValueError("Xinyi: missing param host")
                sys.exit(1)
            
            robot = init(host)
        
        elif (robot is None):
            raise ValueError("Xinyi: We should connect with robot first")
            sys.exit(1)
        
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
            
            break
        
        else:
            print('Invalid instruction in environment.py!!!!')
            sys.exit(1)
            
def pseudo_main(comm, rank):
    sys.path.append(os.path.join(base_dir, 'pySokoban'))
    import pygame
    import pySokoban
    from pySokoban import sokoban
    
    hub = None
    listener = None
    ret = 1
    
    while (ret == 1):
        data = comm.recv(source=MPI_Rank.MASTER)
        inst = data[0]
        
        if inst == Instruction.INIT:
            if len(data) == 2:
                ctrl_type = data[1]
            else:
                raise ValueError("Xinyi: missing param ctrl_type")
                sys.exit(1)
            # hub, listener = init(ctrl_type)
            
            game = sokoban.mySokoban()
            game.initLevel()
            
            game_ing = True
            while game_ing:
                pygame.quit()
                game_ing = False
                break
            
        elif inst == Instruction.EXIT:
            break
        else:
            sys.stdout.flush()
            print('Invalid instruction!!!!')
            sys.exit(1)
    

if __name__ == '__main__':
    comm = None
    rank = None
    main(comm, rank)