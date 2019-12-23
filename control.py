import sys
import os
import numpy as np
import time
from threading import Thread

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'SokobanSolver'))
sys.path.append(os.path.join(base_dir, 'myo-python'))
import SokobanSolver
import SokobanSolver.sokoban as Solver_s
from SokobanSolver import search
from SokobanSolver import puzzler
from puzzler import *

import myo


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

class Listener(myo.DeviceListener):
    
    def __init__(self):
        self.lastpose = None
        # print("Original pose : ", event.pose)
        
    def on_connected(self, event):
        print("Hello, '{}'! Finger Spread to exit.".format(event.device_name))
        # print(event.Arm)
        # event.device.vibrate(myo.VibrationType.short)
        event.device.vibrate(myo.VibrationType.long)
        event.device.request_battery_level()
        
    def dis_connected(self, event):
        print("GoodBye Myo~")
    
    def on_battery_level(self, event):
        print("Your battery level is:", event.battery_level)
    
    # def show_arm(self, event):
    # 	print("Myo is connected with: ", event.Arm)
    
    def on_orientation(self, event):
        ori = event.orientation
        acc = event.acceleration
        gyroscope = event.gyroscope
        # print("Orientation:", np.around(ori.x, decimals=3), np.around(ori.y, decimals=3), np.around(ori.z, decimals=3), np.around(ori.w, decimals=3))
           # print(event.orientation.x)
        # print("Orientation:", quat.x, quat.y, quat.z, quat.w)
    
    def on_pose(self, event):
        if event.pose != self.lastpose:
            self.lastpose = event.pose
            print(type(self.lastpose))
            # sys.stdout.write("\rNow the pose is %s", self.lastpose)
            # sys.stdout.flush()
            print("Pose: ", self.lastpose)
            print(" ")
        else:
            print("no change")
            pass
        if event.pose == myo.Pose.double_tap:
            return False
            
def action(listener):
    if listener.lastpose == myo.Pose.fingers_spread:
        cmd = "Down"
    elif listener.lastpose == myo.Pose.fist:
        cmd = "Up"
    elif listener.lastpose == myo.Pose.wave_in:
        cmd = "Left"
    elif listener.lastpose == myo.Pose.wave_out:
        cmd = "Right"

    elif listener.lastpose == myo.Pose.double_tap:
        cmd = "Help"
    
    comm.send(cmd, dest=rank-1)
    
    if cmd == "Help":
        list_str = comm.recv(source=rank-1)
        
        if list_str is None:
            cmd = "Quit"
            comm.send(cmd, dest=rank-1)
            sys.exit(1)
            
        print('start solver')
        solution = Solver(level_set, current_level)
        solution.warehouse.extract_locations(list_str)
        solution.start()
        solution.join()
        # print(solution.list_actions)
        
        if solution.list_actions is not None:
            comm.send(solution.list_actions, dest=rank-1)
        else:
            comm.send([], dest=rank-1)

def main(comm, rank, level_set, current_level, has_myo=False):
    
    if has_myo:
        myo.init(sdk_path=os.path.join(base_dir, 'myo-sdk-win-0.9.0'))
        hub = myo.Hub()
        arm = myo.Arm
        # print("Myo is connected with : ", arm.name)
        listener = Listener()
        print("listening ....")
    
    if (comm is not None) and (rank is not None):
        flag_ready = comm.recv(source=rank-1)
        if flag_ready:
            cmd = ""
            
            if has_myo:
                while hub.run(listener.on_event, 50):
                    action(listener)
                    time.sleep(1)
            else:
                cmd = "Help"
                comm.send(cmd, dest=rank-1)
    
                if cmd == "Help":
                    list_str = comm.recv(source=rank-1)
                    
                    if list_str is None:
                        cmd = "Quit"
                        comm.send(cmd, dest=rank-1)
                        
                    print('start solver')
                    solution = Solver(level_set, current_level)
                    solution.warehouse.extract_locations(list_str)
                    solution.start()
                    solution.join()
                    # print(solution.list_actions)
                    
                    if solution.list_actions is not None:
                        comm.send(solution.list_actions, dest=rank-1)
                    else:
                        comm.send([], dest=rank-1)
                    
                    # has_robot = comm.recv(source=rank-1)
                    # if has_robot:
                        # idx = 0
                        # while idx != len(solution.list_actions):
                            # step_idx = comm.recv(source=rank-1)
            print('Bye, bye!')

if __name__ == '__main__':
    comm = None
    rank = None
    level_set = 'magic_sokoban6'
    current_level = 7
    main(comm, rank, level_set, current_level)