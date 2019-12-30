import os
import sys
import copy
base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'SokobanSolver'))

from threading import Thread
import SokobanSolver
import SokobanSolver.sokoban as Solver_s
import SokobanSolver.search as search
import SokobanSolver.puzzler as puzzler
from puzzler import *

from constants import current_level
from constants import level_set


class Solver(Thread):
    def __init__(self, level_set, current_level):
        super().__init__()
        self.warehouse = Solver_s.Warehouse()
        pySokoban_root = os.path.join(base_dir, 'pySokoban')
        maze_path = os.path.join(pySokoban_root, 'levels', level_set)
        self.warehouse.read_warehouse_file(
			os.path.join(maze_path, 'level'+str(current_level)))
        
        self.puzzle = SokobanPuzzle(self.warehouse)
        self.solution = None
        self.path = []
        self.started = False
        self.list_actions = []

    def run(self):
        self.solution = search.breadth_first_graph_search(self.puzzle)
        
        if self.solution:
            self.list_actions = [node.action for node in self.solution.path()]
            self.list_actions.pop(0)
            # print(list_event)
        else:
            self.list_actions = []
        
    def stop(self):
        self.stopped = True
        
    def parse_matrix_to_str(self, matrix):
        # print(self.myLevel.matrix)
        ret = []
        for list_m in matrix:
            s = "".join(str(m) for m in list_m)
            s += "\n"
            ret.append(s)
        # return ret
        self.warehouse.extract_locations(ret)

def which_box(mind_player_pos, mind_list_boxes_pos, list_suggestion):
    # print('list_suggestion', list_suggestion)
    # sys.stdout.flush()
    x = mind_player_pos[0]
    y = mind_player_pos[1]
    
    tmp_x = x
    tmp_y = y
    
    dict_unit_x = {
        "Left": -1,
        "Right": 1,
        "Up": 0,
        "Down": 0
        }
    
    dict_unit_y = {
        "Left": 0,
        "Right": 0,
        "Up": -1,
        "Down": 1
        }
    
    for step in list_suggestion:
        tmp_x += dict_unit_x[step]
        tmp_y += dict_unit_y[step]
        
        for box in mind_list_boxes_pos:
            if (tmp_x == box[0]) and (tmp_y == box[1]):
                return box
                
def calibrate_world(world_player_pos, 
                    world_list_boxes_pos,
                    mind_player_pos,
                    mind_list_boxes_pos,
                    num_row, num_col):
    matrix = []
    for col in range(num_col):
        matrix.append([])
        for row in range(num_row):
            matrix[col].append(' ')
            
    for box in mind_list_boxes_pos:
        matrix[box[1]][box[0]] = '.'
        
    for box in world_list_boxes_pos:
        x = box[0]
        y = box[1]
        if (matrix[y][x] == '.'):
            matrix[y][x] = '*'
        else:
            matrix[y][x] = '$'
            
    x = world_player_pos[0]
    y = world_player_pos[1]
    if (matrix[y][x] == '.'):
        matrix[y][x] = '+'
    else:
        matrix[y][x] = '@'
        
    matrix[0][0] = '#'
    matrix[num_col-1][0] = '#'
    matrix[0][num_row-1] = '#'
    matrix[num_col-1][num_row-1] = '#'
    
    solution = Solver(level_set, current_level)
    solution.parse_matrix_to_str(matrix)
    print('matrix', matrix)
    # print('solution.warehouse.targets', solution.warehouse.targets)
    # print('solution.warehouse.worker', solution.warehouse.worker)
    # print('solution.warehouse.boxes', solution.warehouse.boxes)
    solution.start()
    solution.join()
    solution.stop()
    print('solution.list_actions', solution.list_actions)
    # list_suggestion = copy.deepcopy(solution.list_actions)
    
    # print('list_suggestion', list_suggestion)
    sys.stdout.flush()
            