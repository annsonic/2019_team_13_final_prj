import sys
import os
import pygame
base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'myo-python'))
import myo
from constants import MPI_Rank
from constants import Instruction
from constants import RobotMotion


class Listener(myo.DeviceListener):
    
    def __init__(self):
        self.lastpose = None
        # print("Original pose : ", event.pose)
        
    def on_connected(self, event):
        print("Hello, '{}'! double_tap to exit.".format(event.device_name))
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
            # print(type(self.lastpose))
            # sys.stdout.write("\rNow the pose is %s", self.lastpose)
            # sys.stdout.flush()
            print("Pose: ", self.lastpose)
            print(" ")
        else:
            print("no change")
            pass
        sys.stdout.flush()
        if event.pose == myo.Pose.double_tap:
            return False
    
    def get_pose(self):
        
        if self.lastpose == myo.Pose.double_tap:
            # return "double_tap"
            return ""
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

def parse_pose_to_robot_cmd(comm, pose):
    if pose == "wave_in":
        comm.send((RobotMotion.LEFT,), dest=MPI_Rank.ROBOT)
    elif pose == "wave_out":
        comm.send((RobotMotion.RIGHT,), dest=MPI_Rank.ROBOT)
    elif pose == "fingers_spread":
        comm.send((RobotMotion.BACKWARD,), dest=MPI_Rank.ROBOT)
    elif pose == "fist":
        comm.send((RobotMotion.FORWARD,), dest=MPI_Rank.ROBOT)
        
def main(comm, rank):
    myo.init(sdk_path=os.path.join(base_dir, 'myo-sdk-win-0.9.0'))
    hub = myo.Hub()
    
    listener = Listener()
    print("listening ....")
    
    while True:
            
        data = comm.recv(source=MPI_Rank.MASTER)
        inst = data[0]
        sys.stdout.flush()
        if inst == Instruction.INIT:
            pass
        elif inst == Instruction.ROBOT_GUIDE:
            # wait for robot
            gaming = comm.recv(source=MPI_Rank.ROBOT)
            print('\tuser hear robot', gaming)
            sys.stdout.flush()
            
            list_pose = []
            last_p = ""
            while hub.run(listener.on_event, 100):
                ppose = listener.get_pose()
                if (ppose != last_p):
                    print("\t!!!!!")
                    sys.stdout.flush()
                    last_p = ppose
                    print("\tppose", ppose)
                    sys.stdout.flush()
                    if ppose != "rest":
                        list_pose.append(ppose)
                        
                if len(list_pose)>10:
                    pose = max(set(list_pose), key=list_pose.count)
                    parse_pose_to_robot_cmd(comm, pose)
                    break
            print('end training')
            sys.stdout.flush()
                
        elif inst == Instruction.EXIT:
            break
        else:
            print('Invalid instruction!!!!')
            sys.exit(1)

###
def pseudo_wait(time):
    """
    Makes the program halt for 'time' seconds or until the user press Quit on the window.
    
    """
    
    clock = pygame.time.Clock()
    waiting = True
    event = None
    while waiting:
        dt = clock.tick(30) / 1000  # Takes the time between each loop and convert to seconds.
        time -= dt
        
        event = pygame.event.poll()
        if (event.type == pygame.KEYDOWN) or (event.type == pygame.QUIT):
            waiting = False
        if time <= 0:
            waiting = False
            event = None

    return  event

def pseudo_play(comm, times=None):
    
    counter = 0
    while (counter<times):
        
        if times > 1:
            event = pseudo_wait(time=5)
        else:
            event = pygame.event.poll()
        
        if event is None:
            comm.send((RobotMotion.HELP,), dest=MPI_Rank.ROBOT)
            print("user leave active mode")
            sys.stdout.flush()
            break
        elif event.type == pygame.KEYDOWN:
            # print('\tUser', event)
            # sys.stdout.flush()
            if event.key == pygame.K_LEFT:
                comm.send((RobotMotion.LEFT,), dest=MPI_Rank.ROBOT)
            elif event.key == pygame.K_RIGHT:
                comm.send((RobotMotion.RIGHT,), dest=MPI_Rank.ROBOT)
            elif event.key == pygame.K_DOWN:
                comm.send((RobotMotion.BACKWARD,), dest=MPI_Rank.ROBOT)
            elif event.key == pygame.K_UP:
                comm.send((RobotMotion.FORWARD,), dest=MPI_Rank.ROBOT)
            
            elif event.key == pygame.K_ESCAPE:
                comm.send((RobotMotion.EXIT,), dest=MPI_Rank.ROBOT)
                pygame.quit()
                counter = times + 1
                break
        
        elif event.type == pygame.QUIT:
            comm.send((RobotMotion.EXIT,), dest=MPI_Rank.ROBOT)
            pygame.quit()
            counter = times + 1
            break
        
        else:
            continue
        
        counter += 1
        print('\tuser counter', counter)
        sys.stdout.flush()
        if times > 1:
            data = comm.recv(source=MPI_Rank.ROBOT)
            inst = data[0]
            print("Check exit", inst)
            sys.stdout.flush()
            if (inst == Instruction.EXIT):
                # comm.send((RobotMotion.EXIT,), dest=MPI_Rank.ROBOT)
                pygame.quit()
                print("User Bye~", inst)
                sys.stdout.flush()
                break
        
            
def pseudo_main(comm, rank):
    while True:
        data = comm.recv(source=MPI_Rank.MASTER)
        inst = data[0]
        
        print("Control", inst)
        sys.stdout.flush()
        if inst == Instruction.INIT:
            pygame.init()
            display_surface = pygame.display.set_mode((400, 100))
            pygame.display.set_caption('Robot Controller')
            font = pygame.font.Font(pygame.font.get_default_font(), 14)
            text_surface = font.render('Press arrow keys in this window', 
                                        True, pygame.Color('orange'))
            display_surface.blit(text_surface, dest=(80,40))
            pygame.display.flip()
        elif inst == Instruction.ROBOT_GUIDE:
            print('\t--- User practice ---')
            sys.stdout.flush()  
            
            # wait for robot
            gaming = comm.recv(source=MPI_Rank.ROBOT)
            print('\tuser hear robot', gaming)
            sys.stdout.flush()
            
            pseudo_play(comm, times=1)
            
            print('end training')
            sys.stdout.flush()
        elif inst == Instruction.PLAY:
            print('\t--- Pygame Play ---')
            sys.stdout.flush()
            
            pseudo_play(comm, times=100)
        elif inst == Instruction.EXIT:
            print('\t--- Pygame Bye~ ---')
            sys.stdout.flush()
            pygame.quit()
            break
        else:
            print('\t!!!! Invalid instruction in control !!!!')
            sys.stdout.flush()
            sys.exit(1)
            break

if __name__ == '__main__':
    comm = None
    rank = None
    
    main(comm, rank)