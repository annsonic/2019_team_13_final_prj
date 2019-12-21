#
# https://www.geeksforgeeks.org/find-co-ordinates-of-contours-using-opencv-python/
# https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/

import numpy as np 
import cv2
import imutils
import sys
from scipy import stats
import os
base_dir = os.path.abspath(os.path.dirname(__file__))
  
    
def approx2_rect(img2, bg='black', skew=False):

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
        if cv2.contourArea(cnt) < 100:
            continue
    
        # Filter out line segments
        approx = cv2.approxPolyDP(cnt, 
            epsilon=0.01*cv2.arcLength(cnt, True), closed=True) 
        if (len(approx)<3):
            continue
        
        if not skew:
            x, y, w, h = cv2.boundingRect(approx)
            p1 = np.matrix([[x, y]])
            p2 = np.matrix([[x + w, y]])
            p3 = np.matrix([[x, y + h]])
            p4 = np.matrix([[x + w, y + h]])
            xc = x + w/2.0
            yc = y + h/2.0
        else:# if rotated
            a, b, c, d = approx
            
            p1 = np.matrix(a) # upper left
            p2 = np.matrix(b) # upper right
            p3 = np.matrix(c) # lower left
            p4 = np.matrix(d) # lower right
            
            # TODO: use momentum to calculate
            moment = cv2.moments(threshold)
            xc = moment["m10"] / moment["m00"]
            yc = moment["m01"] / moment["m00"]
            w = (np.linalg.norm(b-a)+np.linalg.norm(d-c))/2
            h = (np.linalg.norm(c-a)+np.linalg.norm(d-b))/2
            
        list_contour.append(np.array([p1, p2, p3, p4]).astype(int))
        list_yolo_form.append(np.array([xc, yc, w, h]).astype(int))
    # print(len(list_contour))
    if len(list_yolo_form) == 0:
        raise ValueError('Error to detect rectangles.')
        sys.exit(1)
    
    return list_contour, list_yolo_form
    
def visualize_contour(img2, list_contour, list_yolo_form):  
    font = cv2.FONT_HERSHEY_DUPLEX 
    
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
    # cv2.namedWindow('contours', cv2.WINDOW_NORMAL)
    cv2.imshow('contours', img2)  
      
    k = cv2.waitKey(0)
    # Exiting the window if 'q'/ESC is pressed on the keyboard. 
    if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
        cv2.destroyAllWindows()
        cv2.imwrite(img_name, segment)

def find_index_on_puzzle(x, y, lat, long):
    # lat=np.linspace(15,30,61)
    # long=np.linspace(91,102,45)
    
    xi=np.searchsorted(lat,x)
    yi=np.searchsorted(long,y)
    
    # TODO: compare the values of lat[thisLat] and lat[thisLat+1]
    if 0< xi < len(lat):
        xi = list(lat).index(min((lat[xi-1], lat[xi]), key=lambda t: abs(x-t)))
    # else:
        # xi -= 1
    if 0< yi < len(long):
        yi = list(long).index(min((long[yi-1], long[yi]), key=lambda t: abs(y-t)))
    # else:
        # yi -= 1
    print(xi-1, yi-1)
    return xi-1, yi-1
    
def get_rect(img2, bg='black', skew=False):  
    list_contour, list_yolo_form = approx2_rect(img2, bg, skew)
    
    if False:
        visualize_contour(img2, list_contour, list_yolo_form)
    
    arr_yolo_form = np.array(list_yolo_form)
    # grids are always squares so it doesn't care if you get width or height
    common_width = stats.mode(arr_yolo_form[:][:,2])[0][0]
    # print(common_width)
    
    return list_contour, list_yolo_form
    

    ####
def main(img2, merge_grid=False):
    
    # Following are grid-wise
    if not merge_grid:
        # Sharpen gaps
        kernel = np.ones((2,2),np.uint8)
        erosion = cv2.erode(img2, kernel, iterations = 10)
        dilate = cv2.dilate(erosion,kernel,iterations = 10)
        list_contour, list_yolo_form = get_rect(dilate, bg='black', mask=False)
        
        # Build list of boundary points
        lat = np.zeros(8+2)
        long = np.zeros(7+2)
        pt = list(list_yolo_form[0])
        lat[0] = pt[0] + pt[2]
        for i, rect in enumerate(list_yolo_form[0:8]):
            lat[i+1] = list(list_yolo_form[i])[0]
        pt = list(list_yolo_form[7])
        lat[-1] = pt[0] - pt[2]
        lat = np.flip(lat)
        
        pt = list(list_yolo_form[0])
        long[0] = pt[1] + pt[3]
        i = 1
        for rect in list_yolo_form:
            x = list(rect)[0]
            xi = np.searchsorted(lat,x)
            
            if xi == 1:
                long[i] = list(rect)[1]
                i += 1
        pt = list(list_yolo_form[-1])
        long[-1] = pt[1] - pt[3]
        long = np.flip(long)
        
        find_index_on_puzzle(549, 636, lat, long)
    
    # Following are a whole
    else:
        "Note: kernel size is depend on the puzzle in image"
        kernel = np.ones((50,50),np.uint8)
        # dilate = cv2.dilate(img2,kernel,iterations = 10)
        # erosion = cv2.erode(dilate, kernel, iterations = 10)
        # 
        closing = cv2.morphologyEx(img2, cv2.MORPH_CLOSE, kernel)
        opening = cv2.morphologyEx(img2, cv2.MORPH_OPEN, kernel)
        if True:
            cv2.imshow('erosion', opening)
            k = cv2.waitKey(0)
            # Exiting the window if 'q'/ESC is pressed on the keyboard. 
            if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
                cv2.destroyAllWindows()
        list_contour, list_yolo_form = get_rect(opening, bg='black', mask=True)
        
    return list_contour, list_yolo_form
    
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        fn = sys.argv[1]
    else:
        fn = os.path.join(base_dir, 'map/2.png') # 'shapes.png'
    img2 = cv2.imread(fn)
    
    main(img2, merge_grid=True)
    