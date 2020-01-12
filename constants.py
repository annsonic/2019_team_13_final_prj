import enum

user_title = "Xiao_he"

dict_title = {
    "class_mate_he": "帥氣的大哥哥",
    "class_mate_she": "漂亮的姊姊",
    "professor": "dear professor"}

cam_id = 1
has_robot = True
#host = "192.168.0.192"
host = "172.20.10.11"
ctrl_type = "myo"#"keyboard"#"myo"
wait_time = 5 # unit: seconds

dict_hsv = {
            "light_green": (46, 30, 80),
            "dark_green": (100, 255, 255),
            "light_yellow": (15, 35, 190),
            "dark_yellow": (45, 255, 255),
            "light_cyan": (80, 0, 190),
            "dark_cyan": (150, 85, 255),
            "light_blue": (90, 0, 0),
            "dark_blue": (150, 255, 255),
            "light_red": (0, 0, 0),
            "dark_red": (7, 255, 255),
            "light_orange": (5, 150, 0),
            "dark_orange": (17, 255, 255),
            "light_black": (0, 0, 0),
            "dark_black": (179, 100, 50),
            "light_white": (0, 0, 0),
            "dark_white": (179, 30, 255)
            }
            
dict_role_hsv = {
            "wall": {
                "light": dict_hsv["light_green"],
                "dark": dict_hsv["dark_green"],
                "area": 50000,
                "circle": False
                },
            "box": {
                "light": dict_hsv["light_yellow"],
                "dark": dict_hsv["dark_yellow"],
                "area": 200,
                "circle": False
                },
            "robot_orange": {
                "light": dict_hsv["light_orange"],
                "dark": dict_hsv["dark_orange"],
                "area": 100,
                "circle": False
                },
            "robot_face": {
                "light": dict_hsv["light_black"],
                "dark": dict_hsv["dark_black"],
                "area": 40,
                "circle": True
                },
            "robot_body": {
                "light": dict_hsv["light_white"],
                "dark": dict_hsv["dark_white"],
                "area": 500,
                "circle": True
                },
            }
            
level_set = "magic_sokoban6"
current_level = 7

dict_symbol = {
            "wall": "#",
            "robot": "@",
            "robot_on_goal": "+",
            "box": "$",
            "box_on_goal": "*",
            "goal": ".",
            "floor": " "
            }
            
unit_pace_length = 0.205 # unit:m
head_pitch = 10
            
class MPI_Rank(enum.IntEnum):
    MASTER = 1
    ROBOT = 0
     # The MPI_COMM_WORLD rank 0 process inherits standard input from mpirun.
     
# class Instruction(enum.Enum):
    # INIT = 0
    # EXIT = 1
    # # -------------- Instr of CAMERA ---------------
    # BB = 2 # Calculate bounding box and send
    # DISPLAY = 3
    # HIDING = 4
    # # -------------- Instr of ROBOT ----------------
    # SPEAK = 11
    # NOD = 12
    # DETECT_FACE = 13
    # ROBOT_GUIDE = 14
    # MOVE = 15
    # # -------------- Instr of User ----------------
    # PLAY = 21

# class MyoGesture(enum.IntEnum):
    # SPREAD = 0
    # WAVE_RIGHT = 1
    # WAVE_LEFT = 2
    # FIST = 3
    # DOUBLE_TAP = 4
    
class RobotMotion(enum.IntEnum):
    BACKWARD = 0
    RIGHT = 1
    LEFT = 2
    FORWARD = 3
    HELP = 4
    EXIT = 5