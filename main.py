import sys
import cv2
import os
import numpy as np
base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'Vision'))
sys.path.append(os.path.join(base_dir, 'pySokoban'))
from Vision import coordinates
from Vision import perspective_transform
from pySokoban import sokoban

if __name__ == '__main__':
    if len(sys.argv) > 1:
        fn = sys.argv[1]
    else:
        fn = 'map/2.png' # 'shapes.png'
    img2 = cv2.imread(fn)
    
    list_contour, list_yolo_form = coordinates.main(img2, merge_grid=True)
    
    pts = np.zeros(shape=(4,2))
    for idx, pt in np.ndenumerate(list_contour[0]):
        pts[idx[0]][idx[2]] = pt
    
    perspective_transform.main(img2, pts)
    
    # sokoban.main()