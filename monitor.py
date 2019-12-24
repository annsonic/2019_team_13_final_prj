import os
import sys
import cv2
base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'Vision'))
from Vision import camera
from constants import MPI_Rank
from constants import Instruction

def init(cam_id):
    vs = camera.myCamera(id=cam_id).start()
    return vs
    
def display(vs):
    while True:
        frame = vs.read()
        cv2.imshow("Frame", frame)
        k = cv2.waitKey(1)
        if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
            break
        
    cv2.destroyAllWindows()

def main(comm, rank):
    vs = None
    
    while True:
        data = comm.recv(source=MPI_Rank.MASTER)
        inst = data[0]
        
        if inst == Instruction.INIT:
            if len(data) == 2:
                cam_id = data[1]
            else:
                raise ValueError("Xinyi: missing param cam_id")
                sys.exit(1)
            vs = init(cam_id)
            # display(vs)
        elif inst == Instruction.EXIT:
            if vs is not None:
                vs.stop()
            
            break
        else:
            print('Invalid instruction!!!!')
            sys.exit(1)
    

if __name__ == '__main__':
    comm = None
    rank = None
    main(comm, rank)