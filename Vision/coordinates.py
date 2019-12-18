#
# https://www.geeksforgeeks.org/find-co-ordinates-of-contours-using-opencv-python/

import numpy as np 
import cv2
import imutils
import sys
from scipy import stats


def approx2_rect(img2, bg='black'):

    # Reading same image in another  
    # variable and converting to gray scale. 
    img = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
      
    # Converting image to a binary image 
    # ( black and white only image). 
    if bg == 'white':
        th = cv2.THRESH_BINARY_INV
    else:
        th = cv2.THRESH_BINARY
    _, threshold = cv2.threshold(img, 0, 255, th+cv2.THRESH_OTSU)
    
    # Detecting contours in image. 
    contours = cv2.findContours(threshold, cv2.RETR_EXTERNAL, 
                                   cv2.CHAIN_APPROX_SIMPLE) 
    cnts = imutils.grab_contours(contours)
    
    list_contour = []
    list_yolo_form = []
    # Filter out small contours
    for cnt in cnts :
        if cv2.contourArea(cnt) < 100:
            continue
    
        # Filter out line segments
        approx = cv2.approxPolyDP(cnt, 
            epsilon=0.01*cv2.arcLength(cnt, True), closed=True) 
        if (len(approx)<3):
            continue
        
        x, y, w, h = cv2.boundingRect(approx)
        p1 = np.matrix([[x, y]])
        p2 = np.matrix([[x + w, y]])
        p3 = np.matrix([[x, y + h]])
        p4 = np.matrix([[x + w, y + h]])
        xc = x + w/2.0
        yc = y + h/2.0
        # if rotated
        # rect = cv2.minAreaRect(cnt)
        # box = cv2.cv.BoxPoints(rect)
        
        # list_contour.append(approx)
        list_contour.append(np.array([p1, p2, p3, p4]))
        list_yolo_form.append(np.array([xc, yc, w, h]))
    # print(len(list_contour))
    
    return list_contour, list_yolo_form
    
def visualize_contour(img2, list_contour):  
    font = cv2.FONT_HERSHEY_COMPLEX 
    
    # Going through every contours found in the image. 
    for approx in list_contour :
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
                string = str(x) + " " + str(y)  
      
                if(i == 0): 
                    # text on topmost co-ordinate. 
                    cv2.putText(img2, "Arrow tip", (x, y), 
                                    font, 0.5, (255, 0, 0))  
                else: 
                    # text on remaining co-ordinates. 
                    cv2.putText(img2, string, (x, y),  
                              font, 0.5, (0, 255, 0))  
            i = i + 1
      
    # Showing the final image. 
    cv2.namedWindow('contours', cv2.WINDOW_KEEPRATIO)
    cv2.imshow('contours', img2)  
      
    # Exiting the window if 'q' is pressed on the keyboard. 
    if cv2.waitKey(0) & 0xFF == ord('q'):  
        cv2.destroyAllWindows() 

def find_index_on_puzzle(x, y, lat, long):
    # lat=np.linspace(15,30,61)
    # long=np.linspace(91,102,45)
    
    xi=np.searchsorted(lat,x)
    yi=np.searchsorted(long,y)
    
    # TODO: compare the values of lat[thisLat] and lat[thisLat+1]
    if 0< xi < len(lat):
        xi = list(lat).index(min((lat[xi-1], lat[xi]), key=lambda t: abs(x-t)))
    else:
        xi -= 1
    if 0< yi < len(long):
        yi = list(long).index(min((long[yi-1], long[yi]), key=lambda t: abs(y-t)))
    else:
        yi -= 1
    print(xi, yi)
    return xi, yi
    
def get_rect(img2, bg='black'):  
    list_contour, list_yolo_form = approx2_rect(img2, bg)
    
    visualize_contour(img2, list_contour)
    
    arr_yolo_form = np.array(list_yolo_form)
    # grids are always squares so it doesn't care if you get width or height
    common_width = stats.mode(arr_yolo_form[:][:,2])[0][0]
    # print(common_width)
    
    return list_contour, list_yolo_form
    
def color_filter(img, light, dark):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_img, light, dark)
    segment = cv2.bitwise_and(img, img, mask=mask)
    return segment
    
def main(img2, merge_grid=False):
    dict_hsv = {
    "light_green": (45, 0, 50),
    "dark_green": (80, 100, 165),
    "light_yellow": (20, 190, 150),
    "dark_yellow": (90, 255, 255),
    "light_orange": (5, 50, 150),
    "dark_orange": (20, 255, 255),
    "light_white": (60, 0, 100),
    "dark_white": (179, 255, 255)
    }
    
    # Target at green grids
    segment = color_filter(img2, dict_hsv["light_green"], dict_hsv["dark_green"])
    
    # Following are grid-wise
    if not merge_grid:
        # Sharpen gaps
        kernel = np.ones((2,2),np.uint8)
        erosion = cv2.erode(segment, kernel, iterations = 10)
        dilate = cv2.dilate(erosion,kernel,iterations = 10)
        list_contour, list_yolo_form = get_rect(dilate, bg='black')
        
        if len(list_contour) == 0:
            raise ValueError('Error to detect rectangles.')
            sys.exit(1)
        lat = np.zeros(8)
        long = np.zeros(7)
        for i, rect in enumerate(list_contour[0:8]):
            lat[i] = list(list_contour[i][0][0])[0]
        lat = np.flip(lat)
        
        i = 0
        for rect in list_contour:
            x = list(rect[0][0])[0]
            xi=np.searchsorted(lat,x)
            if xi == 0:
                long[i] = list(rect[0][0])[1]
                i += 1
        long = np.flip(long)
        
        find_index_on_puzzle(108, 195, lat, long)
    
    # Following are a whole
    else:
        kernel = np.ones((2,2),np.uint8)
        dilate = cv2.dilate(segment,kernel,iterations = 10)
        erosion = cv2.erode(dilate, kernel, iterations = 10)
        list_contour, list_yolo_form = get_rect(erosion, bg='black')
        

    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        fn = sys.argv[1]
    else:
        fn = 'map/3.png' # 'shapes.png'
    img2 = cv2.imread(fn)
    
    main(img2, merge_grid=False)
    