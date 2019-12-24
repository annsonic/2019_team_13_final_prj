dict_hsv = {
            "light_green": (46, 30, 0),
            "dark_green": (100, 255, 255),
            "light_yellow": (15, 35, 0),
            "dark_yellow": (45, 255, 255),
            "light_cyan": (80, 0, 190),
            "dark_cyan": (150, 85, 255),
            "light_blue": (90, 0, 0),
            "dark_blue": (150, 255, 255),
            "light_red": (0, 0, 0),
            "dark_red": (7, 255, 255),
            "light_orange": (5, 150, 0),
            "dark_orange": (17, 255, 255),
            "light_white": (0, 0, 0),
            "dark_white": (60, 0, 255)
            }
            
dict_role_hsv = {
            "wall": {
                "light": dict_hsv["light_green"],
                "dark": dict_hsv["dark_green"],
                "area": 10000,
                "scale": 0.1
                },
            "box": {
                "light": dict_hsv["light_yellow"],
                "dark": dict_hsv["dark_yellow"],
                "area": 1000,
                "scale": 0.1
                },
            "robot": {
                "light": dict_hsv["light_orange"],
                "dark": dict_hsv["dark_orange"],
                "area": 300,
                "scale": 0.03
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