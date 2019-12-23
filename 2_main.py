import sys
import cv2
import os
import time
import numpy as np
import re
import copy
from mpi4py import MPI

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'Vision'))
sys.path.append(os.path.join(base_dir, 'pySokoban'))
from Vision import camera
from Vision import coordinates
from coordinates import imgParser
from pySokoban.Level import Level
from zenbo_junior import myRobot
import control


class Game():
    def __init__(self, host):
        self.host = host
        if self.host:
            self.robot = myRobot(host)
  
        # pySokoban
        self.level_set = "magic_sokoban6"#"original"
        self.current_level = 7
        self.myLevel = Level(self.level_set, self.current_level)
        self.target_found = False
        self.game_ing = True
        
        # self.img_parser = imgParser(self.myLevel.matrix, 
            # self.cam.warped_w, self.cam.warped_h)
    
    def movePlayer(self, direction):
        
        matrix = self.myLevel.getMatrix()
        
        self.myLevel.addToHistory(matrix)
        
        x = self.myLevel.getPlayerPosition()[0]
        y = self.myLevel.getPlayerPosition()[1]
        
        #print boxes
        print("\tboxes coordination: ",self.myLevel.getBoxes())
        
        if direction == "Left":
            print("\t######### Moving Left #########")
            
            # if is_space
            if self.myLevel.matrix[y][x-1] == " ":
                print("\tOK Space Found")
                self.myLevel.matrix[y][x-1] = "@"
                if self.target_found == True:
                    self.myLevel.matrix[y][x] = "."
                    self.target_found = False
                else:
                    self.myLevel.matrix[y][x] = " "
            
            # if is_box
            elif self.myLevel.matrix[y][x-1] == "$":
                print("\tBox Found")
                if self.myLevel.matrix[y][x-2] == " ":
                    self.myLevel.matrix[y][x-2] = "$"
                    self.myLevel.matrix[y][x-1] = "@"
                    if self.target_found == True:
                        self.myLevel.matrix[y][x] = "."
                        self.target_found = False
                    else:
                        self.myLevel.matrix[y][x] = " "
                elif self.myLevel.matrix[y][x-2] == ".":
                    self.myLevel.matrix[y][x-2] = "*"
                    self.myLevel.matrix[y][x-1] = "@"
                    if self.target_found == True:
                        self.myLevel.matrix[y][x] = "."
                        self.target_found = False
                    else:
                        self.myLevel.matrix[y][x] = " "
                    
                    
            # if is_box_on_target
            elif self.myLevel.matrix[y][x-1] == "*":
                print("\tBox on target Found")
                if self.myLevel.matrix[y][x-2] == " ":
                    self.myLevel.matrix[y][x-2] = "$"
                    self.myLevel.matrix[y][x-1] = "@"
                    if self.target_found == True:
                        self.myLevel.matrix[y][x] = "."
                    else:
                        self.myLevel.matrix[y][x] = " "
                    self.target_found = True
                    
                elif self.myLevel.matrix[y][x-2] == ".":
                    self.myLevel.matrix[y][x-2] = "*"
                    self.myLevel.matrix[y][x-1] = "@"
                    if self.target_found == True:
                        self.myLevel.matrix[y][x] = "."
                    else:
                        self.myLevel.matrix[y][x] = " "
                    self.target_found = True
                    
            # if is_target
            elif self.myLevel.matrix[y][x-1] == ".":
                print("\tTarget Found")
                self.myLevel.matrix[y][x-1] = "@"
                if self.target_found == True:
                    self.myLevel.matrix[y][x] = "."
                else:
                    self.myLevel.matrix[y][x] = " "
                self.target_found = True
            
            # else
            else:
                print("\tThere is a wall here")
        
        elif direction == "Right":
            print("\t######### Moving Right #########")

            # if is_space
            if self.myLevel.matrix[y][x+1] == " ":
                print("\tOK Space Found")
                self.myLevel.matrix[y][x+1] = "@"
                if self.target_found == True:
                    self.myLevel.matrix[y][x] = "."
                    self.target_found = False
                else:
                    self.myLevel.matrix[y][x] = " "
            
            # if is_box
            elif self.myLevel.matrix[y][x+1] == "$":
                print("\tBox Found")
                if self.myLevel.matrix[y][x+2] == " ":
                    self.myLevel.matrix[y][x+2] = "$"
                    self.myLevel.matrix[y][x+1] = "@"
                    if self.target_found == True:
                        self.myLevel.matrix[y][x] = "."
                        self.target_found = False
                    else:
                        self.myLevel.matrix[y][x] = " "
                
                elif self.myLevel.matrix[y][x+2] == ".":
                    self.myLevel.matrix[y][x+2] = "*"
                    self.myLevel.matrix[y][x+1] = "@"
                    if self.target_found == True:
                        self.myLevel.matrix[y][x] = "."
                        self.target_found = False
                    else:
                        self.myLevel.matrix[y][x] = " "				
            
            # if is_box_on_target
            elif self.myLevel.matrix[y][x+1] == "*":
                print("\tBox on target Found")
                if self.myLevel.matrix[y][x+2] == " ":
                    self.myLevel.matrix[y][x+2] = "$"
                    self.myLevel.matrix[y][x+1] = "@"
                    if self.target_found == True:
                        self.myLevel.matrix[y][x] = "."
                    else:
                        self.myLevel.matrix[y][x] = " "
                    self.target_found = True
                    
                elif self.myLevel.matrix[y][x+2] == ".":
                    self.myLevel.matrix[y][x+2] = "*"
                    self.myLevel.matrix[y][x+1] = "@"
                    if self.target_found == True:
                        self.myLevel.matrix[y][x] = "."
                    else:
                        self.myLevel.matrix[y][x] = " "
                    self.target_found = True
                
            # if is_target
            elif self.myLevel.matrix[y][x+1] == ".":
                print("\tTarget Found")
                self.myLevel.matrix[y][x+1] = "@"
                if self.target_found == True:
                    self.myLevel.matrix[y][x] = "."
                else:
                    self.myLevel.matrix[y][x] = " "
                self.target_found = True
                
            # else
            else:
                print("\tThere is a wall here")

        elif direction == "Down":
            print("\t######### Moving Down #########")

            # if is_space
            if self.myLevel.matrix[y+1][x] == " ":
                print("\tOK Space Found")
                self.myLevel.matrix[y+1][x] = "@"
                if self.target_found == True:
                    self.myLevel.matrix[y][x] = "."
                    self.target_found = False
                else:
                    self.myLevel.matrix[y][x] = " "
            
            # if is_box
            elif self.myLevel.matrix[y+1][x] == "$":
                print("\tBox Found")
                if self.myLevel.matrix[y+2][x] == " ":
                    self.myLevel.matrix[y+2][x] = "$"
                    self.myLevel.matrix[y+1][x] = "@"
                    if self.target_found == True:
                        self.myLevel.matrix[y][x] = "."
                        self.target_found = False
                    else:
                        self.myLevel.matrix[y][x] = " "
                
                elif self.myLevel.matrix[y+2][x] == ".":
                    self.myLevel.matrix[y+2][x] = "*"
                    self.myLevel.matrix[y+1][x] = "@"
                    if self.target_found == True:
                        self.myLevel.matrix[y][x] = "."
                        self.target_found = False
                    else:
                        self.myLevel.matrix[y][x] = " "
            
            # if is_box_on_target
            elif self.myLevel.matrix[y+1][x] == "*":
                print("\tBox on target Found")
                if self.myLevel.matrix[y+2][x] == " ":
                    self.myLevel.matrix[y+2][x] = "$"
                    self.myLevel.matrix[y+1][x] = "@"
                    if self.target_found == True:
                        self.myLevel.matrix[y][x] = "."
                    else:
                        self.myLevel.matrix[y][x] = " "
                    self.target_found = True
                    
                elif self.myLevel.matrix[y+2][x] == ".":
                    self.myLevel.matrix[y+2][x] = "*"
                    self.myLevel.matrix[y+1][x] = "@"
                    if self.target_found == True:
                        self.myLevel.matrix[y][x] = "."
                    else:
                        self.myLevel.matrix[y][x] = " "
                    self.target_found = True
            
            # if is_target
            elif self.myLevel.matrix[y+1][x] == ".":
                print("\tTarget Found")
                self.myLevel.matrix[y+1][x] = "@"
                if self.target_found == True:
                    self.myLevel.matrix[y][x] = "."
                else:
                    self.myLevel.matrix[y][x] = " "
                self.target_found = True
                
            # else
            else:
                print("\tThere is a wall here")

        elif direction == "Up":
            print("\t######### Moving Up #########")

            # if is_space
            if self.myLevel.matrix[y-1][x] == " ":
                print("\tOK Space Found")
                self.myLevel.matrix[y-1][x] = "@"
                if self.target_found == True:
                    self.myLevel.matrix[y][x] = "."
                    self.target_found = False
                else:
                    self.myLevel.matrix[y][x] = " "
            
            # if is_box
            elif self.myLevel.matrix[y-1][x] == "$":
                print("\tBox Found")
                if self.myLevel.matrix[y-2][x] == " ":
                    self.myLevel.matrix[y-2][x] = "$"
                    self.myLevel.matrix[y-1][x] = "@"
                    if self.target_found == True:
                        self.myLevel.matrix[y][x] = "."
                        self.target_found = False
                    else:
                        self.myLevel.matrix[y][x] = " "

                elif self.myLevel.matrix[y-2][x] == ".":
                    self.myLevel.matrix[y-2][x] = "*"
                    self.myLevel.matrix[y-1][x] = "@"
                    if self.target_found == True:
                        self.myLevel.matrix[y][x] = "."
                        self.target_found = False
                    else:
                        self.myLevel.matrix[y][x] = " "					
                        
            # if is_box_on_target
            elif self.myLevel.matrix[y-1][x] == "*":
                print("\tBox on target Found")
                if self.myLevel.matrix[y-2][x] == " ":
                    self.myLevel.matrix[y-2][x] = "$"
                    self.myLevel.matrix[y-1][x] = "@"
                    if self.target_found == True:
                        self.myLevel.matrix[y][x] = "."
                    else:
                        self.myLevel.matrix[y][x] = " "
                    self.target_found = True
                    
                elif self.myLevel.matrix[y-2][x] == ".":
                    self.myLevel.matrix[y-2][x] = "*"
                    self.myLevel.matrix[y-1][x] = "@"
                    if self.target_found == True:
                        self.myLevel.matrix[y][x] = "."
                    else:
                        self.myLevel.matrix[y][x] = " "
                    self.target_found = True
                        
            # if is_target
            elif self.myLevel.matrix[y-1][x] == ".":
                print("\tTarget Found")
                self.myLevel.matrix[y-1][x] = "@"
                if self.target_found == True:
                    self.myLevel.matrix[y][x] = "."
                else:
                    self.myLevel.matrix[y][x] = " "
                self.target_found = True
                
            # else
            else:
                print("\tThere is a wall here")
        
        # Zenbo move
        
        print("\n\tBoxes remaining: " + str(len(self.myLevel.getBoxes())))
        
        if len(self.myLevel.getBoxes()) == 0:
            # self.myEnvironment.screen.fill((0, 0, 0))
            print("\n\tLevel Completed")
            # Zenbo say congratuations
    
    def parse_matrix_to_str(self, matrix):
        # print(self.myLevel.matrix)
        ret = []
        for list_m in matrix:
            s = "".join(str(m) for m in list_m)
            s += "\n"
            ret.append(s)
        return ret
        
    def parse_cv_to_matrix(self):
        frame = self.monitor()
        self.img_parser.update_matrix(self.cam, frame)
        
    def check_cv_matrix_is_coherent(self):
        pass

    def loop(self, comm, rank, has_robot):
        comm.send(True, dest=rank+1)
        
        while True:
            direction = None
            direction = comm.recv(source=rank+1)
            sys.stdout.flush()
            print("direction", direction)
            
            if direction == "Quit":
                break
            elif direction == "Help": # 
                m = copy.deepcopy(self.myLevel.matrix)
                list_direction = []
                
                while len(list_direction)==0:
                    list_str = self.parse_matrix_to_str(self.myLevel.matrix)
                    comm.send(list_str, dest=rank+1)
                    
                    list_direction = comm.recv(source=rank+1)
                    
                    m = self.myLevel.getLastMatrix()
                
                comm.send(has_robot, dest=rank+1)
                for idx, d in enumerate(list_direction):
                    if has_robot:
                        direction = ""
                        while direction != d:
                            # Zenbo say direction
                            comm.send(idx, dest=rank+1)
                            direction = comm.recv(source=rank+1)
                    self.movePlayer(direction)
                break
            
            elif direction is not None:
                self.movePlayer(direction)
                
        if self.host:
            self.robot.release()
            

        
def main(cam_id=0,
         has_robot=True, 
         host=None):
    
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    node_name = MPI.Get_processor_name()
    print("Hello world from process {} at {}".format(rank, node_name))
    
    if rank == 0:
        print("Passive part")
        if not has_robot:
            host = None
        
        g = Game(host)
        
            
        # Robot get ready
        # g.parse_cv_to_matrix()
        
        g.loop(comm, rank, has_robot)
        
        print("process {} is done".format(rank))
        
    elif rank == 1:
        sys.stdout.flush()
        print("Active part")
        control.main(comm, rank, level_set='magic_sokoban6', current_level=7)
        print("process {} is done".format(rank))
    
    elif rank == 2:
        sys.stdout.flush()
        print("Camera part")
        
        vs = camera.myCamera(id=cam_id).start()
        while True:
            frame = vs.read()
            cv2.imshow("Frame", frame)
            k = cv2.waitKey(1)
            if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
                break
            
        cv2.destroyAllWindows()
        vs.stop()
        
        
        
        sys.stdout.flush()
        print("process {} is done".format(rank))

if __name__ == '__main__':
    # mpiexec -n 2 python 2_main.py
    
    main(cam_id=0, 
         has_robot=False, 
         host='192.168.0.126')
    
    # if len(sys.argv) > 1:
        # fn = sys.argv[1]
    # else:
        # fn = 'Vision/map/4.png' # 'shapes.png'
    # img2 = cv2.imread(fn)
    
    
    
    # sokoban.main()