# 2019_robotics_final_prj

* Environment
  
  Python 3
  ```
  pip install pygame
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
    | Key r  | Renew  |
    | Keypad Esc  | Quit Game  |

  - **SokobanSolver** is a path-planer, working for only 1 user-specified sokoban-level.
    Forked from https://github.com/Dotrar/SokobanSolver
    
    - Under root folder, executes:  python sokobanSolver_pySokoban.py
