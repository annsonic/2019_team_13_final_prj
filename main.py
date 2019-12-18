import sys
import cv2
import os
base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'Vision'))
sys.path.append(os.path.join(base_dir, 'pySokoban'))
from Vision import coordinates
from pySokoban import sokoban

if __name__ == '__main__':
    # if len(sys.argv) > 1:
        # fn = sys.argv[1]
    # else:
        # fn = 'map/4.png' # 'shapes.png'
    # img2 = cv2.imread(fn)
    
    # coordinates.main(img2, merge_grid=False)
    sokoban.main()