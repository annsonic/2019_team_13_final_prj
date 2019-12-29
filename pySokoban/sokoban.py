# Name: pySokoban
# Description: A sokoban implementation using python & pyGame
# Author: Kazantzakis Nikos <kazantzakisnikos@gmail.com>
# Date: 2015
# Last Modified: 31-03-2016

import pygame
import time
import sys
from Environment import Environment
from Level import Level

class mySokoban():
    def __init__(self, level = 1):
        # Create the environment
        self.myEnvironment = Environment()

        # Choose a theme
        self.theme = "soft"#"default"

        # Choose a level set
        self.level_set = "magic_sokoban6"#"original"

        # Set the start Level
        self.current_level = level

        self.myLevel = None
        self.target_found = False

    def drawLevel(self, matrix_to_draw):
        
        # Load level images
        wall = pygame.image.load(self.myEnvironment.getPath() + '/themes/' + self.theme + '/images/wall.png').convert()
        box = pygame.image.load(self.myEnvironment.getPath() + '/themes/' + self.theme + '/images/box.png').convert()
        box_on_target =  pygame.image.load(self.myEnvironment.getPath() + '/themes/' + self.theme + '/images/box_on_target.png').convert()
        space = pygame.image.load(self.myEnvironment.getPath() + '/themes/' + self.theme + '/images/space.png').convert()
        target = pygame.image.load(self.myEnvironment.getPath() + '/themes/' + self.theme + '/images/target.png').convert()
        player = pygame.image.load(self.myEnvironment.getPath() + '/themes/' + self.theme + '/images/player.png').convert()
        
        # If horizontal or vertical resolution is not enough to fit the level images then resize images
        if self.myLevel.getSize()[0] > self.myEnvironment.size[0] / 36 or self.myLevel.getSize()[1] > self.myEnvironment.size[1] / 36:
            
            # If level's x size > level's y size then resize according to x axis
            if self.myLevel.getSize()[0] / self.myLevel.getSize()[1] >= 1:
                new_image_size = self.myEnvironment.size[0]/self.myLevel.getSize()[0]
            # If level's y size > level's x size then resize according to y axis
            else:
                new_image_size = self.myEnvironment.size[1]/self.myLevel.getSize()[1]
            
            # Just to the resize job	
            wall = pygame.transform.scale(wall, (new_image_size,new_image_size))
            box = pygame.transform.scale(box, (new_image_size,new_image_size))
            box_on_target = pygame.transform.scale(box_on_target, (new_image_size,new_image_size))
            space = pygame.transform.scale(space, (new_image_size,new_image_size))
            target = pygame.transform.scale(target, (new_image_size,new_image_size))
            player = pygame.transform.scale(player, (new_image_size,new_image_size))	
            
        # Just a Dictionary (associative array in pyhton's lingua) to map images to characters used in level design 
        images = {'#': wall, ' ': space, '$': box, '.': target, '@': player, '*': box_on_target, '+': player}
        
        # Get image size. Images are always squares so it doesn't care if you get width or height
        box_size = wall.get_width()
        
        # Iterate all Rows
        for i in range (0,len(matrix_to_draw)):
            # Iterate all columns of the row
            for c in range (0,len(matrix_to_draw[i])):
                self.myEnvironment.screen.blit(images[matrix_to_draw[i][c]], (c*box_size, i*box_size))

        pygame.display.update()
				
    def movePlayer(self, direction):
        
        matrix = self.myLevel.getMatrix()
        
        self.myLevel.addToHistory(matrix)
        
        x = self.myLevel.getPlayerPosition()[0]
        y = self.myLevel.getPlayerPosition()[1]
        
        #print boxes
        print('\t', self.myLevel.getBoxes())
        str_status = ""
        if direction == "L":
            print("\t######### Moving Left #########")
            
            # if is_space
            if matrix[y][x-1] == " ":
                print("\tOK Space Found")
                str_status = "\tOK Space Found"
                matrix[y][x-1] = "@"
                if self.target_found == True:
                    matrix[y][x] = "."
                    self.target_found = False
                else:
                    matrix[y][x] = " "
            
            # if is_box
            elif matrix[y][x-1] == "$":
                print("\tBox Found")
                str_status = "\tBox Found"
                if matrix[y][x-2] == " ":
                    matrix[y][x-2] = "$"
                    matrix[y][x-1] = "@"
                    if self.target_found == True:
                        matrix[y][x] = "."
                        self.target_found = False
                    else:
                        matrix[y][x] = " "
                elif matrix[y][x-2] == ".":
                    matrix[y][x-2] = "*"
                    matrix[y][x-1] = "@"
                    if self.target_found == True:
                        matrix[y][x] = "."
                        self.target_found = False
                    else:
                        matrix[y][x] = " "
                    
                    
            # if is_box_on_target
            elif matrix[y][x-1] == "*":
                print("\tBox on target Found")
                str_status = "\tBox on target Found"
                if matrix[y][x-2] == " ":
                    matrix[y][x-2] = "$"
                    matrix[y][x-1] = "@"
                    if self.target_found == True:
                        matrix[y][x] = "."
                    else:
                        matrix[y][x] = " "
                    self.target_found = True
                    
                elif matrix[y][x-2] == ".":
                    matrix[y][x-2] = "*"
                    matrix[y][x-1] = "@"
                    if self.target_found == True:
                        matrix[y][x] = "."
                    else:
                        matrix[y][x] = " "
                    self.target_found = True
                    
            # if is_target
            elif matrix[y][x-1] == ".":
                print("\tTarget Found")
                str_status = "\tTarget Found"
                matrix[y][x-1] = "+" # Xinyi
                if self.target_found == True:
                    matrix[y][x] = "."
                else:
                    matrix[y][x] = " "
                self.target_found = True
            
            # else
            else:
                print("\tThere is a wall here")
                str_status = "\tThere is a wall here"
        
        elif direction == "R":
            print("\t######### Moving Right #########")

            # if is_space
            if matrix[y][x+1] == " ":
                print("\tOK Space Found")
                str_status = "\tOK Space Found"
                matrix[y][x+1] = "@"
                if self.target_found == True:
                    matrix[y][x] = "."
                    self.target_found = False
                else:
                    matrix[y][x] = " "
            
            # if is_box
            elif matrix[y][x+1] == "$":
                print("\tBox Found")
                str_status = "\tBox Found"
                if matrix[y][x+2] == " ":
                    matrix[y][x+2] = "$"
                    matrix[y][x+1] = "@"
                    if self.target_found == True:
                        matrix[y][x] = "."
                        self.target_found = False
                    else:
                        matrix[y][x] = " "
                
                elif matrix[y][x+2] == ".":
                    matrix[y][x+2] = "*"
                    matrix[y][x+1] = "@"
                    if self.target_found == True:
                        matrix[y][x] = "."
                        self.target_found = False
                    else:
                        matrix[y][x] = " "				
            
            # if is_box_on_target
            elif matrix[y][x+1] == "*":
                print("\tBox on target Found")
                str_status = "\tBox on target Found"
                if matrix[y][x+2] == " ":
                    matrix[y][x+2] = "$"
                    matrix[y][x+1] = "@"
                    if self.target_found == True:
                        matrix[y][x] = "."
                    else:
                        matrix[y][x] = " "
                    self.target_found = True
                    
                elif matrix[y][x+2] == ".":
                    matrix[y][x+2] = "*"
                    matrix[y][x+1] = "@"
                    if self.target_found == True:
                        matrix[y][x] = "."
                    else:
                        matrix[y][x] = " "
                    self.target_found = True
                
            # if is_target
            elif matrix[y][x+1] == ".":
                print("\tTarget Found")
                str_status = "\tTarget Found"
                matrix[y][x+1] = "+" # Xinyi
                if self.target_found == True:
                    matrix[y][x] = "."
                else:
                    matrix[y][x] = " "
                self.target_found = True
                
            # else
            else:
                print("\tThere is a wall here")
                str_status = "\tThere is a wall here"

        elif direction == "D":
            print("\t######### Moving Down #########")

            # if is_space
            if matrix[y+1][x] == " ":
                print("\tOK Space Found")
                str_status = "\tOK Space Found"
                matrix[y+1][x] = "@"
                if self.target_found == True:
                    matrix[y][x] = "."
                    self.target_found = False
                else:
                    matrix[y][x] = " "
            
            # if is_box
            elif matrix[y+1][x] == "$":
                print("\tBox Found")
                str_status = "\tBox Found"
                if matrix[y+2][x] == " ":
                    matrix[y+2][x] = "$"
                    matrix[y+1][x] = "@"
                    if self.target_found == True:
                        matrix[y][x] = "."
                        self.target_found = False
                    else:
                        matrix[y][x] = " "
                
                elif matrix[y+2][x] == ".":
                    matrix[y+2][x] = "*"
                    matrix[y+1][x] = "@"
                    if self.target_found == True:
                        matrix[y][x] = "."
                        self.target_found = False
                    else:
                        matrix[y][x] = " "
            
            # if is_box_on_target
            elif matrix[y+1][x] == "*":
                print("\tBox on target Found")
                str_status = "\tBox on target Found"
                if matrix[y+2][x] == " ":
                    matrix[y+2][x] = "$"
                    matrix[y+1][x] = "@"
                    if self.target_found == True:
                        matrix[y][x] = "."
                    else:
                        matrix[y][x] = " "
                    self.target_found = True
                    
                elif matrix[y+2][x] == ".":
                    matrix[y+2][x] = "*"
                    matrix[y+1][x] = "@"
                    if self.target_found == True:
                        matrix[y][x] = "."
                    else:
                        matrix[y][x] = " "
                    self.target_found = True
            
            # if is_target
            elif matrix[y+1][x] == ".":
                print("\tTarget Found")
                str_status = "\tTarget Found"
                matrix[y+1][x] = "+" # Xinyi
                if self.target_found == True:
                    matrix[y][x] = "."
                else:
                    matrix[y][x] = " "
                self.target_found = True
                
            # else
            else:
                print("\tThere is a wall here")
                str_status = "\tThere is a wall here"

        elif direction == "U":
            print("\t######### Moving Up #########")

            # if is_space
            if matrix[y-1][x] == " ":
                print("\tOK Space Found")
                str_status = "\tOK Space Found"
                matrix[y-1][x] = "@"
                if self.target_found == True:
                    matrix[y][x] = "."
                    self.target_found = False
                else:
                    matrix[y][x] = " "
            
            # if is_box
            elif matrix[y-1][x] == "$":
                print("\tBox Found")
                str_status = "\tBox Found"
                if matrix[y-2][x] == " ":
                    matrix[y-2][x] = "$"
                    matrix[y-1][x] = "@"
                    if self.target_found == True:
                        matrix[y][x] = "."
                        self.target_found = False
                    else:
                        matrix[y][x] = " "

                elif matrix[y-2][x] == ".":
                    matrix[y-2][x] = "*"
                    matrix[y-1][x] = "@"
                    if self.target_found == True:
                        matrix[y][x] = "."
                        self.target_found = False
                    else:
                        matrix[y][x] = " "					
                        
            # if is_box_on_target
            elif matrix[y-1][x] == "*":
                print("\tBox on target Found")
                str_status = "\tBox on target Found"
                if matrix[y-2][x] == " ":
                    matrix[y-2][x] = "$"
                    matrix[y-1][x] = "@"
                    if self.target_found == True:
                        matrix[y][x] = "."
                    else:
                        matrix[y][x] = " "
                    self.target_found = True
                    
                elif matrix[y-2][x] == ".":
                    matrix[y-2][x] = "*"
                    matrix[y-1][x] = "@"
                    if self.target_found == True:
                        matrix[y][x] = "."
                    else:
                        matrix[y][x] = " "
                    self.target_found = True
                        
            # if is_target
            elif matrix[y-1][x] == ".":
                print("\tTarget Found")
                str_status = "\tTarget Found"
                matrix[y-1][x] = "+" # Xinyi
                if self.target_found == True:
                    matrix[y][x] = "."
                else:
                    matrix[y][x] = " "
                self.target_found = True
                
            # else
            else:
                print("\tThere is a wall here")
                str_status = "\tThere is a wall here"
        
        self.drawLevel(matrix)
        
        sys.stdout.flush()
        return str_status
        
    def check_boxes(self, next_stage=True):
        print("\tBoxes remaining: " + str(len(self.myLevel.getBoxes())))
        
        if (len(self.myLevel.getBoxes()) == 0) and next_stage:
            # self.myEnvironment.screen.fill((0, 0, 0))
            print("Level Completed")
            self.current_level += 1
            self.initLevel()
            
        sys.stdout.flush()
		
    def initLevel(self):
        # Create an instance of this Level
        self.myLevel = Level(self.level_set, self.current_level)

        # Draw this level
        self.myEnvironment.screen.fill((0, 0, 0))
        self.drawLevel(self.myLevel.getMatrix())
        
        self.target_found = False
	

def main():
    game = mySokoban()
    # Initialize Level
    game.initLevel()
    
    game_ing = True
    while game_ing:
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.movePlayer("L")
                    game.check_boxes()
                elif event.key == pygame.K_RIGHT:
                    game.movePlayer("R")
                    game.check_boxes()
                elif event.key == pygame.K_DOWN:
                    game.movePlayer("D")
                    game.check_boxes()
                elif event.key == pygame.K_UP:
                    game.movePlayer("U")
                    game.check_boxes()
                elif event.key == pygame.K_u:
                    game.drawLevel(game.myLevel.getLastMatrix())
                elif event.key == pygame.K_r:
                    game.initLevel()
                elif (event.key == pygame.K_KP_PLUS) or (event.key == pygame.K_0):
                    if game.current_level<50:
                        print("Level Up")
                        game.current_level += 1
                        game.initLevel()
                    else:
                        print("Sorry, it's the final level")
                elif (event.key == pygame.K_KP_MINUS) or (event.key == pygame.K_9):
                    if game.current_level >1:
                        print("Level Down")
                        game.current_level -= 1
                        game.initLevel()
                    else:
                        print("Sorry, it's the beginning level")
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.QUIT:
                pygame.quit()
                # sys.exit()
                game_ing = False
                break
        
    return 0

if __name__ == '__main__':
    main()
    sys.exit(0)