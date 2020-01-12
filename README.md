# 2019_robotics_final_prj

* Environment
  
  Python 3
  ```
  pip install pygame
  pip install imutils
  Under pyzenbo folder, launch python setup.py install or python3 setup.py install
  ```
  Install Myo SDK, please referring to 
  
  https://support.getmyo.com/hc/en-us/articles/202657596-Getting-starting-with-Myo-on-Windows
  
* Execution

  ```
  python 2_main.py
  ```

* Modules
  - **pySokoban** is a playground. We use this to visualize the maze of sokoban.
    Forked from https://github.com/kazantzakis/pySokoban
  
    - Under root folder, executes:  python pySokoban/sokoban.py

    - Sample of warehouse maze:
    
    <a href="url"><img src="https://github.com/annsonic/2019_team_13_final_prj/blob/master/doc/maze.jpg" width="100" height="100"></a>
    
    
    | Keyboard  | Function |
    | ------------- | ------------- |
    | Arrow Up  | Moving Up  |
    | Arrow Down  | Moving Down  |
    | Arrow Right  | Moving Right  |
    | Arrow Left  | Moving Left  |
    | Keypad +  | Level Up  |
    | Keypad -  | Level Down  |
    | Key R  | Renew  |
    | Keypad Esc  | Quit Game  |

  - **SokobanSolver** is a path-planer, working for only 1 user-specified sokoban-level.
    Forked from https://github.com/Dotrar/SokobanSolver
    
    - Under root folder, executes:  python sokobanSolver_pySokoban.py
  - **Vision** is for localization of robot and boxes by image from the webcam. 
  
    Our Color filter is in HSV color space. We visualize the filtering performance by this tool.
    
    - Under root folder, executes:  python Vision/hsv_th.py <your image>
  
    Example:
    
    | Before  | After |
    | ------------- | ------------- |
    | <a href="url"><img src="https://github.com/annsonic/2019_team_13_final_prj/blob/master/doc/hsv_1.jpg" width="100" height="100"></a>  | <a href="url"><img src="https://github.com/annsonic/2019_team_13_final_prj/blob/master/doc/hsv_2.jpg" width="100" height="100"></a>  |

     
    
