import sys
import os
base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'myo-python'))
# from mpi4py import MPI
from threading import Thread
import cv2
import imutils
import pygame
import numpy as np
import time

import myo
import environment
from environment import Components
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
            print("Pose: ", self.lastpose)
            sys.stdout.flush()
            # print(" ")
            
        else:
            # print("no change")
            return self.lastpose
            pass
        # if event.pose == myo.Pose.fingers_spread:
            # return False
    
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

def send_pose_to_robot(pose):
    if pose == "wave_in":
        game_components.robot.left()
        game_components.robot.heading += 90
        current_wait_time = 0
    elif pose == "wave_out":
        game_components.robot.right()
        game_components.robot.heading -= 90
        current_wait_time = 0
                
    elif pose == "fist":
        if (abs(game_components.robot.heading)%360 == 90):
            # game_components.calibrate_rotation(th=10, dir=0)
            str_status = game_components.game.movePlayer("U")
            game_components.robot.heading = 90
    
        elif (abs(game_components.robot.heading)%360 == 180):

            str_status = game_components.game.movePlayer("L")
            game_components.robot.heading = 180
            
        elif (abs(game_components.robot.heading)%360 == 0):
            str_status = game_components.game.movePlayer("R")
            game_components.robot.heading = 0
            
        elif (abs(game_components.robot.heading)%360 == 270):
            str_status = game_components.game.movePlayer("D")
            game_components.robot.heading = 270
        
        
        if (str_status == "can_move"):
            game_components.robot.forward()
        elif str_status == "\tThere is a wall here":
            game_components.robot.say(line="不行走 會撞牆啦", mood="negative")
        elif str_status == "can_not_move":
            game_components.robot.say(line="太重了 我推不動", mood="negative")
    
        current_wait_time = 0
    
    
    elif pose == "help":
        game_components.robot.say(line='算了 我自己來吧', mood="positive")
        
        game_components.list_suggestion = []
        game_components.give_suggestion()

def myo_loop():
    # Zenbo welcom user
    game_components = Components(comm=None)
    game_components.chat()
    
    game_components.calibrate()
    
    myo.init(sdk_path=os.path.join(base_dir, 'myo-sdk-win-0.9.0'))
    hub = myo.Hub()
    listener = Listener()
    print("[INFO] listening ....")
    sys.stdout.flush()
    
    
    
    try:
        last_p = ""
        current_wait_time = 0
        clock = pygame.time.Clock()
        dt = clock.tick(30) / 1000
        # Makes the program halt for 'time' seconds
        
        while hub.run(listener.on_event, 130):
            
            
            ppose = listener.get_pose()
            event = pygame.event.poll()
            if ppose != last_p:
                last_p = ppose
                if ppose != "rest":
                    print("== myo detect ppose", ppose)
                    sys.stdout.flush()
                    
                    if ppose == "wave_in":
                        game_components.robot.left()
                        game_components.robot.heading += 90
                        current_wait_time = 0
                    elif ppose == "wave_out":
                        game_components.robot.right()
                        game_components.robot.heading -= 90
                        current_wait_time = 0
                                
                    elif ppose == "fist":
                        if (abs(game_components.robot.heading)%360 == 90):
                            # game_components.calibrate_rotation(th=10, dir=0)
                            str_status = game_components.game.movePlayer("U")
                            game_components.robot.heading = 90
                    
                        elif (abs(game_components.robot.heading)%360 == 180):

                            str_status = game_components.game.movePlayer("L")
                            game_components.robot.heading = 180
                            
                        elif (abs(game_components.robot.heading)%360 == 0):
                            str_status = game_components.game.movePlayer("R")
                            game_components.robot.heading = 0
                            
                        elif (abs(game_components.robot.heading)%360 == 270):
                            str_status = game_components.game.movePlayer("D")
                            game_components.robot.heading = 270
                        
                        
                        if (str_status == "can_move"):
                            game_components.robot.forward()
                        elif str_status == "\tThere is a wall here":
                            game_components.robot.say(line="不行走 會撞牆啦", mood="negative")
                        elif str_status == "can_not_move":
                            game_components.robot.say(line="太重了 我推不動", mood="negative")
                    
                        current_wait_time = 0
                    
                    
            else:
                current_wait_time += dt
                if current_wait_time > wait_time:
                    game_components.robot.say(line='算了 我自己來吧', mood="positive")
                        
                    game_components.list_suggestion = []
                    game_components.give_suggestion()
                    current_wait_time = 0
                
            
    finally:
        # comm.send((RobotMotion.EXIT,), dest=MPI_Rank.ROBOT)
        hub.stop()  # !! crucial
        game_components.vs.stop()
        pygame.quit()
    
def keyboard_loop():
    
    # Zenbo welcom user
    game_components = Components(comm=None)
    game_components.chat()
    
    # game_components.calibrate()
    
    # # Show controller window
    # pygame.init()
    # display_surface = pygame.display.set_mode((400, 100))
    # pygame.display.set_caption('Robot Controller')
    # font = pygame.font.Font(pygame.font.get_default_font(), 14)
    # text_surface = font.render('Press arrow keys in this window', 
                                # True, pygame.Color('orange'))
    # display_surface.blit(text_surface, dest=(80,40))
    # pygame.display.flip()
    
    
    # Start playing
    try:
        # last_p = ""
        current_wait_time = 0
        clock = pygame.time.Clock()
        dt = clock.tick(30) / 1000
        # Makes the program halt for 'time' seconds
        
        while True:
            # frame = game_components.vs.read()
            # frame = imutils.resize(frame, width=400)
            
            # cv2.imshow("Frame", frame)
            # k = cv2.waitKey(1)
            # if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
                # cv2.destroyAllWindows()
                # break
            
            event = pygame.event.poll()
            
            if event.type == pygame.KEYDOWN:
                
                
                if event.key == pygame.K_LEFT:
                    game_components.robot.left()
                    game_components.robot.heading += 90
                    current_wait_time = 0
                elif event.key == pygame.K_RIGHT:
                    game_components.robot.right()
                    game_components.robot.heading -= 90
                    current_wait_time = 0
                
                elif event.key == pygame.K_UP:
                    if (abs(game_components.robot.heading)%360 == 90):
                        # game_components.calibrate_rotation(th=10, dir=0)
                        str_status = game_components.game.movePlayer("U")
                        game_components.robot.heading = 90
                
                    elif (abs(game_components.robot.heading)%360 == 180):

                        str_status = game_components.game.movePlayer("L")
                        game_components.robot.heading = 180
                        
                    elif (abs(game_components.robot.heading)%360 == 0):
                        str_status = game_components.game.movePlayer("R")
                        game_components.robot.heading = 0
                        
                    elif (abs(game_components.robot.heading)%360 == 270):
                        str_status = game_components.game.movePlayer("D")
                        game_components.robot.heading = 270
                    
                    
                    if (str_status == "can_move"):
                        game_components.robot.forward()
                    elif str_status == "\tThere is a wall here":
                        game_components.robot.say(line="不行走 會撞牆啦", mood="negative")
                    elif str_status == "can_not_move":
                        game_components.robot.say(line="太重了 我推不動", mood="negative")
                
                    current_wait_time = 0
                
                elif event.key == pygame.K_h:
                    # send_pose_to_robot(comm, "help")
                    
                    game_components.robot.say(line='算了 我自己來吧', mood="positive")
                    
                    game_components.list_suggestion = []
                    game_components.give_suggestion()
                    current_wait_time = 0
                    
                    
                elif (event.key == pygame.K_ESCAPE) or (event.key == pygame.K_q):
                    # comm.send((RobotMotion.EXIT,), dest=MPI_Rank.ROBOT)
                    break
                    
                flag_win = game_components.game.check_boxes()
                if flag_win:
                    game_components.robot.say(line="恭喜破關 你太厲害了", mood="positive")
                    # pygame.quit()
                    break
            
            elif event.type == pygame.QUIT:
                # comm.send((RobotMotion.EXIT,), dest=MPI_Rank.ROBOT)
                break
            else:
                current_wait_time += dt
                if current_wait_time > wait_time:
                    # send_pose_to_robot(comm, "help")
                    current_wait_time = 0
            
    finally:
        game_components.vs.stop()
        pygame.quit()
    
    
    

def welcome(comm):
    while True:
        data = comm.recv(source=MPI_Rank.ROBOT)
        
        if data:
            break
    print("== Exit welcome_user ==")
    sys.stdout.flush()
    


    
def main():
    
        
    # Note: we need press Esc to leave keyboard_loop(comm) or myo_loop(comm)
    if ctrl_type=="keyboard":
        keyboard_loop()
    else: # Polling signals from Myo
        myo_loop()
    
    
    sys.exit(0)

if __name__ == '__main__':
    main()
    # mpiexec -n 2 python 2_main.py