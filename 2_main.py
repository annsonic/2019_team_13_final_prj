import sys
import os
base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'myo-python'))
from mpi4py import MPI
from threading import Thread
import cv2
import imutils
import pygame

import myo
import environment
from webcam import WebcamVideoStream
from webcam import test
from constants import cam_id
from constants import ctrl_type
from constants import wait_time
from constants import MPI_Rank
from constants import RobotMotion


class Listener(myo.DeviceListener):

    def __init__(self):
        self.lastpose = None
        # print("Original pose : ", event.pose)

    def on_connected(self, event):
        sys.stdout.flush()
        print("[INFO] Hello, '{}'! Double Tap to exit.".format(event.device_name))
        sys.stdout.flush()
        # print(event.Arm)
        # event.device.vibrate(myo.VibrationType.short)
        event.device.vibrate(myo.VibrationType.long)
        event.device.request_battery_level()
	
    def dis_connected(self, event):
        sys.stdout.flush()
        print("GoodBye Myo~")
        sys.stdout.flush()

    def on_battery_level(self, event):
        sys.stdout.flush()
        print("Your battery level is:", event.battery_level)
        sys.stdout.flush()

    def on_orientation(self, event):
        ori = event.orientation
        acc = event.acceleration
        gyroscope = event.gyroscope
		# print("Orientation:", np.around(ori.x, decimals=3), np.around(ori.y, decimals=3), np.around(ori.z, decimals=3), np.around(ori.w, decimals=3))
	#     print(event.orientation.x)
		# print("Orientation:", quat.x, quat.y, quat.z, quat.w)

    def on_pose(self, event):
        
        if event.pose != self.lastpose:
            self.lastpose = event.pose
            # print("Pose: ", self.lastpose)
            # print(" ")
            
        else:
            # print("no change")
            return self.lastpose
            pass
        if event.pose == myo.Pose.double_tap:
            return False
    
    def get_pose(self):
        
        if self.lastpose == myo.Pose.double_tap:
            return "double_tap"
        elif self.lastpose == myo.Pose.fist:
            return "fist"
        elif self.lastpose == myo.Pose.fingers_spread:
            return "fingers_spread"
        elif self.lastpose == myo.Pose.wave_in:
            return "wave_in"
        elif self.lastpose == myo.Pose.wave_out:
            return "wave_out"
        elif self.lastpose == myo.Pose.rest:
            return "rest"
        else:
            return ""

def send_pose_to_robot(comm, pose):
    if pose == "wave_in":
        comm.send((RobotMotion.LEFT,), dest=MPI_Rank.ROBOT)
    elif pose == "wave_out":
        comm.send((RobotMotion.RIGHT,), dest=MPI_Rank.ROBOT)
    elif pose == "fingers_spread":
        comm.send((RobotMotion.BACKWARD,), dest=MPI_Rank.ROBOT)
    elif pose == "fist":
        comm.send((RobotMotion.FORWARD,), dest=MPI_Rank.ROBOT)
    elif pose == "double_tap":
        comm.send((RobotMotion.EXIT,), dest=MPI_Rank.ROBOT)
    elif pose == "help":
        comm.send((RobotMotion.HELP,), dest=MPI_Rank.ROBOT)

def myo_loop(comm):
    print("[INFO] sampling THREADED frames from webcam...")
    vs = WebcamVideoStream(src=cam_id).start()
    
    myo.init(sdk_path=os.path.join(base_dir, 'myo-sdk-win-0.9.0'))
    hub = myo.Hub()
    listener = Listener()
    print("[INFO] listening ....")
    sys.stdout.flush()
    
    folder = os.path.join(base_dir, 'Vision', 'camera_data')
    
    try:
        last_p = ""
        current_wait_time = 0
        clock = pygame.time.Clock()
        dt = clock.tick(30) / 1000
        # Makes the program halt for 'time' seconds
        
        while hub.run(listener.on_event, 130):
            frame = vs.read()
            frame = imutils.resize(frame, width=400)
            
            cv2.imshow("Frame", frame)
            k = cv2.waitKey(1)
            if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
                cv2.destroyAllWindows()
                break
            
            ppose = listener.get_pose()
            
            if ppose != last_p:
                last_p = ppose
                if ppose != "rest":
                    print("== myo detect ppose", ppose)
                    sys.stdout.flush()
                    img_name = os.path.join(folder, 
                            "{}_{}.png".format("monitoring", 3))
                    cv2.imwrite(img_name, frame)
                    send_pose_to_robot(comm, ppose)
            else:
                current_wait_time += dt
                if current_wait_time > wait_time:
                    send_pose_to_robot(comm, "help")
                    current_wait_time = 0
                
            
    finally:
        hub.stop()  # !! crucial
        vs.stop()
    
def keyboard_loop(comm):
    print("[INFO] sampling THREADED frames from webcam...")
    vs = WebcamVideoStream(src=cam_id).start()
    
    # Show controller window
    pygame.init()
    display_surface = pygame.display.set_mode((400, 100))
    pygame.display.set_caption('Robot Controller')
    font = pygame.font.Font(pygame.font.get_default_font(), 14)
    text_surface = font.render('Press arrow keys in this window', 
                                True, pygame.Color('orange'))
    display_surface.blit(text_surface, dest=(80,40))
    pygame.display.flip()
    
    folder = os.path.join(base_dir, 'Vision', 'camera_data')
    
    try:
        # last_p = ""
        current_wait_time = 0
        clock = pygame.time.Clock()
        dt = clock.tick(30) / 1000
        # Makes the program halt for 'time' seconds
        
        while True:
            frame = vs.read()
            frame = imutils.resize(frame, width=400)
            
            cv2.imshow("Frame", frame)
            k = cv2.waitKey(1)
            if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
                cv2.destroyAllWindows()
                break
            
            event = pygame.event.poll()
            
            if event.type == pygame.KEYDOWN:
                
                img_name = os.path.join(folder, 
                            "{}_{}.png".format("monitoring", 3))
                cv2.imwrite(img_name, frame)
                
                if event.key == pygame.K_LEFT:
                    send_pose_to_robot(comm, "wave_in")
                elif event.key == pygame.K_RIGHT:
                    send_pose_to_robot(comm, "wave_out")
                elif event.key == pygame.K_DOWN:
                    send_pose_to_robot(comm, "fingers_spread")
                elif event.key == pygame.K_UP:
                    send_pose_to_robot(comm, "fist")
                elif event.key == pygame.K_h:
                    send_pose_to_robot(comm, "help")
                elif (event.key == pygame.K_ESCAPE) or (event.key == pygame.K_q):
                    comm.send((RobotMotion.EXIT,), dest=MPI_Rank.ROBOT)
                    break
            
            elif event.type == pygame.QUIT:
                comm.send((RobotMotion.EXIT,), dest=MPI_Rank.ROBOT)
                break
            else:
                current_wait_time += dt
                if current_wait_time > wait_time:
                    send_pose_to_robot(comm, "help")
                    current_wait_time = 0
            
    finally:
        vs.stop()

def welcome(comm):
    data = comm.recv(source=MPI_Rank.ROBOT)

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    node_name = MPI.Get_processor_name()
    print("Hello world from process {} at {}".format(rank, node_name))
    sys.stdout.flush()
    
    if comm.Get_size() < 2:
        raise ValueError("Xinyi: We need more threads to run this program")
        sys.exit(1)
    
    if rank == MPI_Rank.MASTER:
        print("== perception part ==")
        sys.stdout.flush()
        
        welcome(comm)
        
        if ctrl_type=="keyboard":
            keyboard_loop(comm)
        else: # Polling signals from Myo
            myo_loop(comm)
        
        comm.send((RobotMotion.EXIT,), dest=MPI_Rank.ROBOT)
    elif rank == MPI_Rank.ROBOT: # Robot
        print("== robot part ==")
        sys.stdout.flush()
        
        environment.welcome(comm)
        environment.main(comm)
        
    else:
        print("== Useless process {} ==".format(rank))
        sys.stdout.flush()
        
    pygame.display.quit()
    pygame.quit()
    print("== process {} is done ==".format(rank))
    sys.stdout.flush()

if __name__ == '__main__':
    main()
    # mpiexec -n 2 python 2_main.py