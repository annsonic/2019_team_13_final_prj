import sys
import cv2
import os
import time
import numpy as np
import re
import copy
from mpi4py import MPI

base_dir = os.path.abspath(os.path.dirname(__file__))
import environment
import control
import monitor
from constants import MPI_Rank
from constants import Instruction
from constants import MyoGesture


list_workers_name = [name for name, w in MPI_Rank.__members__.items()]
list_workers_value = [w.value for name, w in MPI_Rank.__members__.items()]
list_workers_name.remove('MASTER')
list_workers_value.remove(MPI_Rank.MASTER)
# print(list_workers_name, list_workers_value) #['ROBOT', 'USER', 'CAMERA'] [1, 2, 3]

def init(comm, cam_id, host, ctrl_type):
    reqs = []
    reqs.append(comm.isend((Instruction.INIT,cam_id), dest=MPI_Rank.CAMERA))
    reqs.append(comm.isend((Instruction.INIT,ctrl_type), dest=MPI_Rank.USER))
    reqs.append(comm.isend((Instruction.INIT,host), dest=MPI_Rank.ROBOT))
    # Polling MPI.isend is done
    for req in reqs:
        req.wait()

def accessory_in_position(comm, flag_exclude_robot=False):
    pass
    
def welcome(comm):
    comm.send((Instruction.DETECT_FACE,), dest=MPI_Rank.ROBOT)
    
    comm.send((Instruction.NOD,"positive"), dest=MPI_Rank.ROBOT)
    
    list_dict = [{"sentence": "哈囉 帥氣的大哥哥你好", "mood": "positive"},
                 {"sentence": "我們一起玩個小遊戲好嗎", "mood": "positive"}]
    comm.send((Instruction.SPEAK,list_dict), dest=MPI_Rank.ROBOT)
    
def training_user(comm):
    list_dict = [{"sentence": "請你用手勢控制我行動", "mood": "positive"},
                 {"sentence": "要依我的正面來判斷前後左右唷", "mood": "positive"},
                 {"sentence": "我們先來練習一下咩", "mood": "positive"}]
    comm.send((Instruction.SPEAK,list_dict), dest=MPI_Rank.ROBOT)
    list_list_dict = [
                 (MyoGesture.FIST, [{"sentence": "出拳是前進", "mood": "positive"}]),
                 (MyoGesture.SPREAD, [{"sentence": "手掌張開是後退", "mood": "positive"}]),
                 (MyoGesture.WAVE_RIGHT, [{"sentence": "手掌朝右是走右邊", "mood": "positive"}]),
                 (MyoGesture.WAVE_LEFT, [{"sentence": "手掌朝左是走左邊", "mood": "positive"}])
                 ]
    for (gesture, list_dict) in list_list_dict:
        comm.send((Instruction.ROBOT_GUIDE,(gesture, list_dict)), 
                dest=MPI_Rank.ROBOT)
        ##TODO
        # ret = comm.recv(source=MPI_Rank.ROBOT)
    
def game(comm, ctrl_type):
    print('xinyi test game')
    comm.send((Instruction.PLAY,ctrl_type), dest=MPI_Rank.USER)
    comm.send((Instruction.PLAY,), dest=MPI_Rank.ROBOT)
    
def congratuation(comm):
    pass
    
def exit(comm):
    reqs = []
    reqs.append(comm.isend((Instruction.EXIT,), dest=MPI_Rank.CAMERA))
    reqs.append(comm.isend((Instruction.EXIT,), dest=MPI_Rank.USER))
    reqs.append(comm.isend((Instruction.EXIT,), dest=MPI_Rank.ROBOT))
    # Polling MPI.isend is done
    for req in reqs:
        req.wait()

def main(cam_id=0,
         has_robot=True, 
         host=None,
         ctrl_type="keyboard"):
    
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    node_name = MPI.Get_processor_name()
    print("Hello world from process {} at {}".format(rank, node_name))
    
    if comm.Get_size() <= len(list_workers_name):
        raise ValueError("Xinyi: We need more threads to run this program")
        sys.exit(1)
    
    if rank == MPI_Rank.MASTER:
        sys.stdout.flush()
        print("master part")
        
        init(comm, cam_id, host, ctrl_type)
        
        # if has_robot:
            # welcome(comm)
            # accessory_in_position(comm, flag_exclude_robot=True)
            # training_user(comm)
            # accessory_in_position(comm, flag_exclude_robot=False)
        game(comm, ctrl_type)
        congratuation(comm)
        exit(comm)
        
    elif rank == MPI_Rank.ROBOT: # Robot
        sys.stdout.flush()
        print("robot part")
        
        if not has_robot:
            print('--- Use virtual environment ---')
            environment.pseudo_main(comm, rank)
        elif has_robot and (host is not None):
            print('--- Use robot ---')
            environment.main(comm, rank)
        else:
            raise ValueError("Xinyi: missing param host")
            sys.exit(1)
    
    elif rank == MPI_Rank.USER: # User
        sys.stdout.flush()
        print("user part")
        control.main(comm, rank)
        
    elif rank == MPI_Rank.CAMERA: # Camera
        sys.stdout.flush()
        print("Camera part")
        
        monitor.main(comm, rank)
        
    else:
        sys.stdout.flush()
        print("Useless process {}".format(rank))    
        
        
    sys.stdout.flush()
    print("process {} is done".format(rank))

if __name__ == '__main__':
    # mpiexec -n 4 python 2_main.py
    
    main(cam_id=0, 
         has_robot=True, 
         host='192.168.0.126',
         ctrl_type="keyboard")
    
    # if len(sys.argv) > 1:
        # fn = sys.argv[1]
    # else:
        # fn = 'Vision/map/4.png' # 'shapes.png'
    # img2 = cv2.imread(fn)
    
    
    
    # sokoban.main()