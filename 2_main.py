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

def init(comm, cam_id, host):
    reqs = []
    # reqs.append(comm.isend((Instruction.INIT,cam_id), dest=MPI_Rank.CAMERA))
    reqs.append(comm.isend((Instruction.INIT,), dest=MPI_Rank.USER))
    reqs.append(comm.isend((Instruction.INIT,host, cam_id), dest=MPI_Rank.ROBOT))
    reqs.append(comm.isend((Instruction.DETECT_FACE,), dest=MPI_Rank.ROBOT))
    # Polling MPI.isend is done
    for req in reqs:
        req.wait()

def accessory_in_position(comm, flag_exclude_robot=False):
    pass
    
def welcome(comm):
    # comm.send((Instruction.NOD,"positive"), dest=MPI_Rank.ROBOT)
    
    list_dict = [{"sentence": "哈囉 帥氣的大哥哥你好", "mood": "positive"},
                 {"sentence": "我們一起玩個小遊戲好嗎", "mood": "positive"}]
    comm.send((Instruction.SPEAK,list_dict), dest=MPI_Rank.ROBOT)
    
def training_user(comm):
    list_dict = [{"sentence": "請你用手勢控制我行動", "mood": "positive"},
                 {"sentence": "要依我的正面來判斷前後左右唷", "mood": "positive"},
                 {"sentence": "我們先來練習一下咩", "mood": "positive"}]
    comm.send((Instruction.SPEAK,list_dict), dest=MPI_Rank.ROBOT)
    list_list_dict = [
                 ("Up", [{"sentence": "出拳是前進 請你出拳", "mood": "positive"}]),
                 ("Down", [{"sentence": "手掌張開是後退 請你張開手掌", "mood": "positive"}]),
                 ("Right", [{"sentence": "手掌朝右是走右邊 請你指揮", "mood": "positive"}]),
                 ("Left", [{"sentence": "手掌朝左是走左邊 請你指揮", "mood": "positive"}])
                 ]
    
    
    for (gesture, list_dict) in list_list_dict:
        while True:
            comm.send((Instruction.ROBOT_GUIDE,(gesture, list_dict)), 
                    dest=MPI_Rank.ROBOT)
            comm.send((Instruction.ROBOT_GUIDE,), dest=MPI_Rank.USER)
            ret = comm.recv(source=MPI_Rank.ROBOT)
            print('\tmaster got', ret)
            sys.stdout.flush()
            if ret:
                break
    
def game(comm):
    
    reqs = []
    reqs.append(comm.isend((Instruction.PLAY,), dest=MPI_Rank.USER))
    reqs.append(comm.isend((Instruction.PLAY,), dest=MPI_Rank.ROBOT))
    # Polling MPI.isend is done
    for req in reqs:
        req.wait()
    
    (ret, gesture, list_actions) = comm.recv(source=MPI_Rank.ROBOT)
    # print(ret, gesture, list_actions)
    # sys.stdout.flush()
    while True:
        if len(list_actions)==0:
            break
        elif ret is True:
            gesture = list_actions.pop(0)
        
        # print('verify', gesture)
        # sys.stdout.flush()
        comm.send((Instruction.ROBOT_GUIDE,(gesture, 
                [{"sentence": "Please move {}".format(gesture), "mood": "positive"}])),
                dest=MPI_Rank.ROBOT)
        comm.send((Instruction.ROBOT_GUIDE,), dest=MPI_Rank.USER)
        # print(list_actions)
        # sys.stdout.flush()
        ret = comm.recv(source=MPI_Rank.ROBOT)
    
def congratuation(comm):
    list_dict = [{"sentence": "恭喜你成功破關", "mood": "positive"},
                 {"sentence": "你真是個天才", "mood": "positive"},
                 {"sentence": "我表現得也很不錯對吧", "mood": "positive"},
                 {"sentence": "請摸摸我的頭 讚美我一下嘿", "mood": "positive"}]
    comm.send((Instruction.SPEAK,list_dict), dest=MPI_Rank.ROBOT)
    
def exit(comm):
    reqs = []
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
    sys.stdout.flush()
    
    if comm.Get_size() <= len(list_workers_name):
        raise ValueError("Xinyi: We need more threads to run this program")
        sys.exit(1)
    
    if rank == MPI_Rank.MASTER:
        print("master part")
        sys.stdout.flush()
        
        init(comm, cam_id, host)
        
        if has_robot:
            welcome(comm)
            accessory_in_position(comm, flag_exclude_robot=True)
        training_user(comm)
            # # accessory_in_position(comm, flag_exclude_robot=False)
        game(comm)
        congratuation(comm)
        exit(comm)
        
    elif rank == MPI_Rank.ROBOT: # Robot
        print("robot part")
        sys.stdout.flush()
        
        if not has_robot:
            print('--- Use virtual environment ---')
            sys.stdout.flush()
            environment.pseudo_main(comm, rank)
        elif has_robot and (host is not None):
            print('--- Use robot ---')
            sys.stdout.flush()
            environment.main(comm, rank)
        else:
            raise ValueError("Xinyi: missing param host")
            sys.exit(1)
    
    elif rank == MPI_Rank.USER: # User
        print("user part")
        sys.stdout.flush()
        if ctrl_type == "keyboard":
            print('--- Use keyboard ---')
            sys.stdout.flush()
            control.pseudo_main(comm, rank)
        elif ctrl_type == "myo":
            print('--- Use Myo Armband ---')
            sys.stdout.flush()
            control.main(comm, rank)
        
    elif rank == MPI_Rank.CAMERA: # Camera
        print("Camera part")
        sys.stdout.flush()
        monitor.main(comm, rank)
        
    else:
        print("Useless process {}".format(rank))
        sys.stdout.flush()
        
    
    print("process {} is done".format(rank))
    sys.stdout.flush()

if __name__ == '__main__':
    # mpiexec -n 4 python 2_main.py
    
    main(cam_id=0, 
         has_robot=False, 
         host='192.168.50.216',
         ctrl_type="keyboard")
    
    # if len(sys.argv) > 1:
        # fn = sys.argv[1]
    # else:
        # fn = 'Vision/map/4.png' # 'shapes.png'
    # img2 = cv2.imread(fn)
    
    
    
    # sokoban.main()