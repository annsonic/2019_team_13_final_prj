#!/usr/bin/python3

import time
import os
import sys
import pygame
import argparse
from functools import partial
from threading import Thread

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'SokobanSolver'))
import SokobanSolver
from SokobanSolver import search
from SokobanSolver import sokoban
from SokobanSolver import puzzler
from puzzler import *

sys.path.append(os.path.join(base_dir, 'pySokoban'))
import pySokoban
from pySokoban import sokoban_gui


_orig_print = print
def print(*args, **kwargs):
    _orig_print(*args, flush=True, **kwargs)

def cls():os.system('clear')

def action_to_pygame_event(list_actions):
    list_events = []

    for action in list_actions:
        if action == "Left":
            key=pygame.K_LEFT
        elif action == "Right":
            key = pygame.K_RIGHT
        elif action == "Up":
            key = pygame.K_UP
        elif action == "Down":
            key = pygame.K_DOWN
        my_event = pygame.event.Event(pygame.KEYDOWN, key=key, mod=0)
        list_events.append(my_event)

    return list_events


class Solver(Thread):
    def __init__(self, level_set, current_level):
        super().__init__()
        self.warehouse = sokoban.Warehouse()
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

        self.list_actions = [node.action for node in self.solution.path()]
        self.list_actions.pop(0)
        # print(list_event)

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
		'--theme',
		dest='theme',
		type=str,
		default='soft',
		help="style of art: 'soft', 'default'")
    parser.add_argument(
		'--level_set',
		dest='level_set',
		type=str,
		default='magic_sokoban6',
		help="type of maze: 'magic_sokoban6', 'original'")
    parser.add_argument(
		'--current_level',
		dest='current_level',
		type=int,
		default=7,
		help="please check levels dir for range")
    args = parser.parse_args()

    return args


def main(args):
    # Choose a theme
    theme = args.theme
    # Choose a level set
    level_set = args.level_set
    # Set the start Level
    current_level = args.current_level

    print('start solver')
    solution = Solver(level_set, current_level)
    solution.start()
    solution.join()
    # print(solution.list_actions)

    if solution.list_actions is not None:
        # Simulate key press event
        list_events = action_to_pygame_event(solution.list_actions)
        sokoban_gui.main(args, list_events)


if __name__ == '__main__':
    args = parse()
    main(args)