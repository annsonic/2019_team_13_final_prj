#
# https://www.geeksforgeeks.org/find-co-ordinates-of-contours-using-opencv-python/
# https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/

import numpy as np 
import cv2
import imutils
import sys
import copy
# from scipy import stats
import os
base_dir = os.path.abspath(os.path.dirname(__file__))
parentdir = os.path.dirname(base_dir)
sys.path.append(parentdir)
from constants import level_set   # Inside parent folder
from constants import current_level
from constants import dict_symbol

class imgParser():
    """ Get index of grid which is occupied by object
    
    matrix (list): 2D, recording each grid is occupied by what kind of object
    num_col (int): number of column of matrix
    num_row (int): number of row of matrix
    lat (numpy array): 1D, the horizontal center of each grid
    long (numpy array): 1D, the vertical center of each grid
    dict_symbol (dict): mapping object and symbol
    
    """
    
    def __init__(self, matrix, puzzle_w, puzzle_h):
        self.matrix = copy.deepcopy(matrix)
        [self.num_col, self.num_row] = self.getSize()
        self.lat = np.zeros(self.num_col)
        self.long = np.zeros(self.num_row)
        self.build_grid_center_points(puzzle_w, puzzle_h)
        self.dict_symbol = dict_symbol
        
    def build_grid_center_points(self, puzzle_w, puzzle_h):
        unit_w = int(puzzle_w / self.num_col)
        unit_h = int(puzzle_h / self.num_row)
        
        self.lat = np.arange(unit_w/2, puzzle_w, unit_w)
        self.long = np.arange(unit_h/2, puzzle_h, unit_h)
        # print(self.lat, self.long)
        
    def find_index_on_puzzle(self, x, y):
        # lat=np.linspace(15,30,61)
        # long=np.linspace(91,102,45)
        
        xi=np.searchsorted(self.lat, x)
        yi=np.searchsorted(self.long, y)
        
        # Compare the distance between lat[thisLat-1] and lat[thisLat]
        if 0< xi < len(self.lat):
            xi = list(self.lat).index(
                min((self.lat[xi-1], self.lat[xi]), key=lambda t: abs(x-t)))
        if 0< yi < len(self.long):
            yi = list(self.long).index(
                min((self.long[yi-1], self.long[yi]), key=lambda t: abs(y-t)))
        # print(xi, yi)
        return xi, yi
        
    def update_matrix(self, cam, warped):
        robot_contour, robot_yolo_form = object_get_rect(cam, warped, role="robot")
        box_contour, box_yolo_form = object_get_rect(cam, warped, role="box")
        
        xi_r, yi_r = self.find_index_on_puzzle(
            x=list(robot_yolo_form[0])[0], y=list(robot_yolo_form[0])[1])
        list_xi_b = []
        list_yi_b = []
        for box in box_yolo_form:
            xi, yi = self.find_index_on_puzzle(
                x=list(box)[0], y=list(box)[1])
            list_xi_b.append(xi)
            list_yi_b.append(yi)
        
        for i in range(0, len(self.matrix)):
            # Iterate all columns
            for k in range(0, len(self.matrix[i]) - 1):
                if self.matrix[i][k] == self.self.dict_symbol["box"]:
                    print('box', k, i)
                if self.matrix[i][k] == self.self.dict_symbol["robot"]:
                    print('robot', k, i)
                if self.matrix[i][k] == self.self.dict_symbol["box_on_goal"]:
                    print('box_on_goal', k, i)
                if self.matrix[i][k] == self.self.dict_symbol["robot_on_goal"]:
                    print('robot_on_goal', k, i)
                    # boxes.append([k, i])
        # return boxes

    def getSize(self):
        max_row_length = 0
        # Iterate all Rows
        for i in range(0, len(self.matrix)):
            # Iterate all columns
            row_length = len(self.matrix[i])
            if row_length > max_row_length:
                max_row_length = row_length
        return [max_row_length, len(self.matrix)]
    
def approx2_rect(img, bg='black', skew=False, area=100, scale=0.03):
    
    if len(img.shape)==3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.GaussianBlur(img, (3, 3), 0)
    # Converting image to a binary image 
    # ( black and white only image). 
    if bg == 'white':
        th = cv2.THRESH_BINARY_INV
    else:
        th = cv2.THRESH_BINARY
    _, threshold = cv2.threshold(img, 0, 255, th+cv2.THRESH_OTSU)
    if False:
        cv2.imshow('threshold', threshold)
        k = cv2.waitKey(0)
        # Exiting the window if 'q'/ESC is pressed on the keyboard. 
        if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
            cv2.destroyAllWindows()
    # Detecting contours in image. 
    contours = cv2.findContours(threshold, cv2.RETR_EXTERNAL, 
                                   cv2.CHAIN_APPROX_SIMPLE) 
    cnts = imutils.grab_contours(contours)
    
    list_contour = []
    list_yolo_form = []
    
    for cnt in cnts :
        
        # Filter out small contours
        if (cv2.contourArea(cnt) < area):
            continue
        if (not skew) and (cv2.contourArea(cnt) > area*2):
            continue
        # print(cv2.contourArea(cnt))
        # Filter out line segments
        # Note: scale 0.03 depends on environment settings
        
        approx = cv2.approxPolyDP(cnt, 
            epsilon=scale*cv2.arcLength(cnt, True), closed=True) 
        # print(len(approx))
        if (len(approx)!=4):
            continue
        
        if skew:# if rotated
            a, b, c, d = approx
            
            p1 = np.matrix(a) # upper left
            p2 = np.matrix(b) # lower left
            p3 = np.matrix(c) # lower right
            p4 = np.matrix(d) # upper right
            
            moment = cv2.moments(approx)
            xc = moment["m10"] / moment["m00"]
            yc = moment["m01"] / moment["m00"]
            w = (np.linalg.norm(d-a)+np.linalg.norm(c-b))/2
            h = (np.linalg.norm(b-a)+np.linalg.norm(c-d))/2
        else:
            x, y, w, h = cv2.boundingRect(approx)
            p1 = np.matrix([[x, y]])
            p2 = np.matrix([[x + w, y]])
            p3 = np.matrix([[x, y + h]])
            p4 = np.matrix([[x + w, y + h]])
            xc = x + w/2.0
            yc = y + h/2.0
            
        list_contour.append(np.array([p1, p2, p3, p4]).astype(int))
        list_yolo_form.append(np.array([xc, yc, w, h]).astype(int))
    # print(len(list_contour))
    if len(list_yolo_form) == 0:
        raise ValueError('Error to detect rectangles.')
        sys.exit(1)
    
    return list_contour, list_yolo_form
    
def visualize_contour(img2, list_contour, list_yolo_form):  
    font = cv2.FONT_HERSHEY_DUPLEX 
    
    if len(img2.shape)<3:
        img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)
    # Going through every contours found in the image. 
    for idx,approx in enumerate(list_contour):
        # draws boundary of contours. 
        cv2.drawContours(img2, [approx], 0, (0, 0, 255), 5)  
      
        # Used to flatted the array containing 
        # the co-ordinates of the vertices. 
        n = approx.ravel()  
        i = 0
        # print(n)
        for j in n : 
            if(i % 2 == 0): 
                x = n[i] 
                y = n[i + 1] 
      
                # String containing the co-ordinates. 
                string = "({},{})".format(x,y)
                
                if(i == 0): 
                    # text on topmost co-ordinate. 
                    cv2.putText(img=img2, 
                        text="Arrow tip ({},{})".format(x, y), 
                        org=(x, y), 
                        fontFace=font, 
                        fontScale=0.7, 
                        color=(255, 255, 255), 
                        thickness=2)
                else: 
                    # text on remaining co-ordinates. 
                    cv2.putText(img2, string, (x, y),  
                              font, 0.7, (0, 255, 0), 2)  
            i = i + 1
        
        cX = list_yolo_form[idx][0]
        cY = list_yolo_form[idx][1]
        # put text and highlight the center
        cv2.circle(img2, (cX, cY), 5, (255, 255, 255), -1)
        cv2.putText(img2, "centroid ({},{})".format(cX, cY), 
                   (cX - 25, cY - 25),
                   font, 
                   0.7, (255, 255, 255), 2)
        
    # Showing the final image. 
    cv2.namedWindow( 'contours',cv2.WINDOW_AUTOSIZE)
    cv2.imshow('contours', img2)
    img_name = os.path.join(base_dir, "{}.png".format("log_get_rect"))
    cv2.imwrite(img_name, img2)
      
    k = cv2.waitKey(0)
    # Exiting the window if 'q'/ESC is pressed on the keyboard. 
    if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
        cv2.destroyAllWindows()

def get_rect(img2, bg='black', skew=False, area=100, scale=0.03):  
    
    list_contour, list_yolo_form = approx2_rect(img2, bg, skew, area, scale)
    
    if False:
        visualize_contour(img2.copy(), list_contour, list_yolo_form)
    
    # arr_yolo_form = np.array(list_yolo_form)
    # grids are always squares so it doesn't care if you get width or height
    # common_width = stats.mode(arr_yolo_form[:][:,2])[0][0]
    # print(common_width)
    
    return list_contour, list_yolo_form

    
def object_get_rect(cam, warped, role):
    obj = cam.color_filter(warped, 
            cam.dict_role_hsv[role]["light"], 
            cam.dict_role_hsv[role]["dark"])
    if np.sum(obj) == 0:
        raise ValueError("Xinyi: Can not detect color of {} in this image".format(role))
        sys.exit(1)
            
    list_contour, list_yolo_form = get_rect(
            obj, bg='black', skew=False, 
            area=cam.dict_role_hsv[role]["area"],
            scale=cam.dict_role_hsv[role]["scale"])
    return list_contour, list_yolo_form
    
def test():
    import camera
    import re
    
    cam = camera.myCamera(id=0)
    
    files = [filename for filename in os.listdir(cam.folder) if filename.startswith("monitoring")]
    files = sorted(files, key=lambda x:float(re.findall("(\d+)",x)[0]))
    img_name = os.path.join(cam.folder, files[-1])
    img = cv2.imread(img_name)
    
    # cam.get_perspective(img) # Calculate transformation matrix again
    
    warped = cam.bird_view(img)
    
    robot_contour, robot_yolo_form = object_get_rect(cam, warped, role="robot")
    box_contour, box_yolo_form = object_get_rect(cam, warped, role="box")
    # print(robot_contour, robot_yolo_form)
    # print(box_contour, box_yolo_form)
    
    # if False:
        # print("\tThis is the transformed view sample:")
        # cv2.imshow("Original", img)
        # cv2.imshow("Warped", box)
            
          
        # k = cv2.waitKey(0)
        # # Exiting the window if 'q'/ESC is pressed on the keyboard. 
        # if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
            # cv2.destroyAllWindows()
    
    matrix = []
    parentdir = os.path.dirname(base_dir)
    with open(os.path.join(parentdir, 'pySokoban', 'levels', level_set + '/level'+str(current_level))) as f:
        for row in f.read().splitlines():
            matrix.append(list(row))
    img_parser = imgParser(matrix, puzzle_w=cam.warped_w, puzzle_h=cam.warped_h)
    
    xi, yi = img_parser.find_index_on_puzzle(
        x=list(robot_yolo_form[0])[0], y=list(robot_yolo_form[0])[1])
    print('robot x_idx {} y_idx {}'.format(xi, yi))
    for box in box_yolo_form:
        xi, yi = img_parser.find_index_on_puzzle(
        x=list(box)[0], y=list(box)[1])
        print('box x_idx {} y_idx {}'.format(xi, yi))
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        fn = sys.argv[1]
    else:
        fn = os.path.join(base_dir, 'map/2.png')
    
    test()