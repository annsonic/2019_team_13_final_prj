import cv2
import sys
import os
import numpy as np

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'Vision'))

from Vision import coordinates
from coordinates import object_get_rect
from Vision import perspective_transform
from constants import dict_hsv
from constants import dict_role_hsv


class ImgParser():
    """ Takes cares of images from camera
    
    """
    
    def __init__(self, num_col, num_row):
        self.folder = os.path.join(base_dir, 'Vision', 'camera_data')
        self.img = self.read()
        
        self.M = np.zeros(1)
        self.warped_w = 0
        self.warped_h = 0
        self.get_perspective()
        # print(self.warped_w, self.warped_h)
        
        self.robot_contour, self.robot_yolo_form = self.get_object_4p_xywh(role="robot")
        self.box_contour, self.box_yolo_form = self.get_object_4p_xywh(role="box")
        
        self.num_col = num_col
        self.num_row = num_row
        self.lat = np.zeros(num_col)
        self.long = np.zeros(num_row)
        self.build_grid_center_points()
        
    def read(self):
        fn = os.path.join(self.folder, 'monitoring_1.png') # 'shapes.png'
        print(fn)
        self.img = cv2.imread(fn)
        
        
    def color_filter(self, img, light, dark):
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_img, light, dark)
        segment = cv2.bitwise_and(img, img, mask=mask)
        return segment
        
    def get_perspective(self, area=150000):
        self.read()
        
        # Target at wall
        segment = self.color_filter(self.img, 
            dict_role_hsv["wall"]["light"], 
            dict_role_hsv["wall"]["dark"])
        if np.sum(segment) == 0:
            raise ValueError("Xinyi: Can not detect color of wall in this image")
            sys.exit(1)
        segment = cv2.cvtColor(segment, cv2.COLOR_BGR2GRAY)
        
        # Note: kernel size is depend on the puzzle in image
        # segment = cv2.GaussianBlur(segment, (15, 15), 0)
        # # apply Canny edge detection using a wide threshold, tight
        # # threshold, and automatically determined threshold
        # # segment = self.auto_canny(segment)
        segment = cv2.Canny(segment, 20, 160)
        
        if False:
            cv2.namedWindow( 'raw',cv2.WINDOW_AUTOSIZE)
            cv2.namedWindow( 'seg',cv2.WINDOW_AUTOSIZE)
            cv2.imshow('raw', img)
            cv2.imshow('seg', segment)
            # k = cv2.waitKey(0)
            # # Exiting the window if 'q'/ESC is pressed on the keyboard. 
            # if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
                # cv2.destroyAllWindows()
        
        
        # # Filter out noisy shapes and smooth the edges
        # # Note: kernel size is depend on the puzzle in image
        kernel = np.ones((15,15),np.uint8)
        segment = cv2.morphologyEx(segment, cv2.MORPH_CLOSE, kernel)
        # segment = cv2.dilate(segment, (20, 20), 10)
        # segment = cv2.erode(segment, (20, 20), 10)
        # segment = cv2.morphologyEx(segment, cv2.MORPH_OPEN, kernel)
        if False:
            cv2.namedWindow( 'filtered',cv2.WINDOW_AUTOSIZE)
            cv2.imshow('filtered', segment)
            k = cv2.waitKey(0)
            # Exiting the window if 'q'/ESC is pressed on the keyboard. 
            if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
                cv2.destroyAllWindows()
                img_name = os.path.join(self.folder, "{}.png".format("filt"))
                cv2.imwrite(img_name, segment)
        # Get outermost contour
        list_contour, list_yolo_form = coordinates.get_rect(
            segment, bg='black', skew=True, area=area)
        
        if len(list_yolo_form) == 0:
            raise ValueError("Xinyi: Get too many rectangles.")
            sys.exit(1)
        
        # Arrange vertexes in the manner four_point_transform() wants
        pts = np.zeros(shape=(4,2))
        for idx, pt in np.ndenumerate(list_contour[0]):
            pts[idx[0]][idx[2]] = pt
            
        # Calculate transformation matrix and save it
        (warped, 
         self.M, 
         self.warped_w, 
         self.warped_h) = perspective_transform.four_point_transform(segment, pts, ret=True)
        
    def bird_view(self):
        warped = cv2.warpPerspective(self.img, self.M, (self.warped_w, self.warped_h))
        
        return warped
        
    def get_object_4p_xywh(self, role):
        warped = self.bird_view()
        if False:
            cv2.imshow('transformed', warped)
            k = cv2.waitKey(0)
            # Exiting the window if 'q'/ESC is pressed on the keyboard. 
            if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
                cv2.destroyAllWindows()
        list_contour, list_yolo_form = object_get_rect(None, warped, role=role)
        return list_contour, list_yolo_form
        
    
    def update_point(self):
        print("update robot")
        self.robot_contour, self.robot_yolo_form = self.get_object_4p_xywh(role="robot")
        print("update box")
        self.box_contour, self.box_yolo_form = self.get_object_4p_xywh(role="box")
        
        # print(robot_contour, robot_yolo_form)
        # print(box_contour, box_yolo_form)
        
    def get_center_point(self, role):
        
        list_obj = []
        if role == "robot":
            xc = self.robot_yolo_form[0][0]
            yc = self.robot_yolo_form[0][1]
            list_obj.append([xc, yc])
        elif role == "box":
            for box in self.box_yolo_form:
                xc = box[0]
                yc = box[1]
                list_obj.append([xc, yc])
        return list_obj
                
    def build_grid_center_points(self):
        unit_w = int(self.warped_w / self.num_col)
        unit_h = int(self.warped_h / self.num_row)
        
        self.lat = np.arange(unit_w/2, self.warped_w, unit_w)
        self.long = np.arange(unit_h/2, self.warped_h, unit_h)
        # print(self.lat, self.long)
        
    def find_index_on_puzzle(self, role):
        list_obj = self.get_center_point(role)
        
        list_index = []
        
        for i in range(len(list_obj)):
            [x, y] = list_obj[i]
            
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
            list_index.append([xi, yi])
        return list_index
         
if __name__ == '__main__':
    parser = ImgParser(num_col=8, num_row=7)
    
    parser.update_point()
    parser.get_center_point("robot")
    parser.get_center_point("box")
    
    [[xi, yi]] = parser.find_index_on_puzzle("robot")
    print('robot x_idx {} y_idx {}'.format(xi, yi))
    
    list_box_idx = parser.find_index_on_puzzle("box")
    for [xi, yi] in list_box_idx:
        print('box x_idx {} y_idx {}'.format(xi, yi))