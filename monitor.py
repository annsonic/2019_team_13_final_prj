import os
import sys
import cv2
from mpi4py import MPI
import numpy as np
base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'Vision'))
from Vision import camera
from constants import MPI_Rank
from constants import Instruction


def main(comm, rank):
    
    while True:
        
        data = comm.recv(source=MPI_Rank.ROBOT)
        inst = data[0]
        # sys.stdout.flush()
        # print("Monitor", inst)
        if inst == Instruction.INIT:
            if len(data) == 2:
                cam_id = data[1]
            else:
                raise ValueError("Xinyi: missing param cam_id")
                sys.exit(1)
            
            vs = camera.myCamera(id=cam_id)#.start()
            # break
        elif inst == Instruction.DISPLAY:
            # while True:
                ret, frame = vs.cam.read()
                cv2.imshow("Monitor", frame)
                
                k = cv2.waitKey(1)
                if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
                    cv2.destroyAllWindows()
                    # break
        elif inst == Instruction.EXIT:
                cv2.destroyAllWindows()
                break
        else:
            print('\tInvalid instruction in monitor!!!!')
            sys.stdout.flush()
            sys.exit(1)
    
    
    
    # arr = np.zeros(3, dtype=float)
    # while True:
        # ret, frame = vs.cam.read()
        # cv2.imshow("Monitor", frame)
        
        # k = cv2.waitKey(1)
        # if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
            # cv2.destroyAllWindows()
            # break
        
        # # if comm.Probe(source=int(MPI_Rank.ROBOT), tag=0):
            # # pass
        # # if comm.Probe(source=MPI_Rank.ROBOT, tag=1):
            # # print("tt")
        
        # req = comm.irecv(buf=arr, source=MPI_Rank.ROBOT, tag=1)
        # (found,a) = req.test()
        
        # if found:
            # print(found, arr)
            # arr = np.zeros(3, dtype=float)
            # break
            # # data = comm.recv(source=MPI_Rank.ROBOT)
            # # inst = data[0]
            # # sys.stdout.flush()
            # # print("Monitor", inst)
            
            # # if inst == Instruction.EXIT:
                # # # cv2.destroyAllWindows()
                # # print('tt2')
                # # # if vs is not None:
                    # # # vs.stop()
                
                # # break
            # # else:
                # # print('\t!!!! Invalid instruction in monitor !!!!')
                # # sys.exit(1)
    

if __name__ == '__main__':
    comm = None
    rank = None
    main(comm, rank)