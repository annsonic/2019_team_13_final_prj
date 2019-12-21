import cv2
import sys
import numpy as np
import re
import os
base_dir = os.path.abspath(os.path.dirname(__file__))
import coordinates
import perspective_transform

class myCamera():
    def __init__(self, id=0):
        self.cam = cv2.VideoCapture(id)
        self.folder = os.path.join(base_dir, 'camera_data')
        
        if self.cam is None or not self.cam.isOpened():
            print('Warning: unable to open video source: ', id)
            sys.exit(1)
        # Disable autofocus
        self.cam.set(cv2.CAP_PROP_AUTOFOCUS, False)
        
        dict_hsv = {
            "light_green": (65, 25, 0),
            "dark_green": (80, 255, 170),
            "light_yellow": (15, 45, 0),
            "dark_yellow": (40, 255, 255),
            "light_cyan": (80, 10, 160),
            "dark_cyan": (120, 75, 255),
            "light_blue": (75, 70, 165),
            "dark_blue": (140, 170, 255),
            "light_red": (0, 60, 0),
            "dark_red": (20, 255, 175),
            "light_orange": (5, 150, 0),
            "dark_orange": (20, 255, 255),
            "light_white": (90, 0, 135),
            "dark_white": (110, 20, 255)
            }
        
        self.dict_role_hsv = {
            "wall": {
                "light": dict_hsv["light_green"],
                "dark": dict_hsv["dark_green"]
                },
            "box": {
                "light": dict_hsv["light_yellow"],
                "dark": dict_hsv["dark_yellow"]
                },
            "robot": {
                "light": dict_hsv["light_orange"],
                "dark": dict_hsv["dark_orange"]
                },
            }
        
        self.cam_mtx = np.zeros(1)
        self.dist = np.zeros(1)
        self.newcam_mtx = np.zeros(1)
        self.M = np.zeros(1)
        if os.path.isfile(self.folder + '/cam_mtx.npy'):
            self.cam_mtx = np.load(self.folder + '/cam_mtx.npy')
        if os.path.isfile(self.folder + '/dist.npy'):
            self.dist = np.load(self.folder + '/dist.npy')
        if os.path.isfile(self.folder + '/newcam_mtx.npy'):
            self.newcam_mtx = np.load(self.folder + '/newcam_mtx.npy')
        if os.path.isfile(self.folder + '/M.npy'):
            self.M = np.load(self.folder + '/M.npy')
        self.warped_w = 0
        self.warped_h = 0
            
    def camera_view(self, mode="calibration"):
        # mode = "calibration" or "monitoring"
        
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)
            img_counter = 0
        else:
            files = [filename for filename in os.listdir(self.folder) if filename.startswith(mode)]
            img_counter = len(files)
        
        while True:
            ret, frame = self.cam.read()
            
            if (len(self.cam_mtx)==3 and len(self.dist[0])==5 and len(self.newcam_mtx)==3):
                frame = self.undistort(frame)
                # print("Xinyi: using undistort")
            if len(self.M)==3:
                frame = self.bird_view(frame)
                # print("Xinyi: using bird_view")
            
            cv2.imshow(mode, frame)
            
            k = cv2.waitKey(1)
            # Exiting the window if 'q'/ESC is pressed on the keyboard. 
            if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
                break
            # SPACE pressed
            elif (k%256 == 32)or (mode=="monitoring"):
                img_name = os.path.join(self.folder, "{}_{}.png".format(mode, img_counter))
                
                wb = cv2.xphoto.createGrayworldWB()
                wb.setSaturationThreshold(0.95)
                frame = wb.balanceWhite(frame)
                
                cv2.imwrite(img_name, frame)
                print("{} written!".format(img_name))
                img_counter += 1
                
                if mode=="monitoring":
                    break
        cv2.destroyAllWindows()
    
    def load_img(self, nx, ny, objp, criteria):
        # Arrays to store object points and image points from all the images.
        objpoints = []  # 3d point in real world space
        imgpoints = []  # 2d points in image plane.
        
        images = [filename for filename in os.listdir(self.folder) if filename.startswith('calibration')]
        images = sorted(images, key=lambda x:float(re.findall("(\d+)",x)[0]))
        
        try:
            if not len(images) >= 20:
                raise ValueError
        except ValueError:
            print('Error! No enough captured chessboard images')
            sys.exit(1)

        win_name = "Verify"
        cv2.namedWindow(win_name, cv2.WND_PROP_AUTOSIZE)
        cv2.setWindowProperty(win_name, cv2.WND_PROP_AUTOSIZE, cv2.WINDOW_FULLSCREEN)

        print("getting images")
        for fname in images:
            img = cv2.imread(os.path.join(self.folder,fname))
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, (nx, ny), None)
            # If found, add object points, image points (after refining them)
            if ret == True:
                objpoints.append(objp)
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                imgpoints.append(corners)
                # Draw and display the corners
                cv2.drawChessboardCorners(img, (nx, ny), corners2, ret)
                cv2.imshow(win_name, img)
                cv2.waitKey(500)

        cv2.destroyAllWindows()

        return objpoints, imgpoints, gray
        
    def calibration(self):
        # prepare object points
        nx = 8  # number of inside corners in x
        ny = 6  # number of inside corners in y
        grid_w = 29  # unit: mm

        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((nx * ny, 3), np.float32)

        # add 29 to account for 29 mm per square in grid
        objp[:, :2] = np.mgrid[0:nx, 0:ny].T.reshape(-1, 2) * grid_w
        
        objpoints, imgpoints, gray = self.load_img(nx, ny, objp, criteria)

        print(">==> Starting calibration")
        ret, cam_mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, gray.shape[::-1], None, None)

        # print(ret)
        print("Camera Matrix")
        print(cam_mtx)
        np.save(self.folder + '/cam_mtx.npy', cam_mtx)

        print("Distortion Coeff")
        print(dist)
        np.save(self.folder + '/dist.npy', dist)

        print("r vecs")
        print(rvecs[2])

        print("t Vecs")
        print(tvecs[2])

        print(">==> Calibration ended")
        
        files = [filename for filename in os.listdir(self.folder) if filename.startswith('calibration_')]
        files = sorted(files, key=lambda x:float(re.findall("(\d+)",x)[0]))
        img_name = os.path.join(self.folder, files[-1])
        img1 = cv2.imread(img_name)
        h, w = img1.shape[:2]
        
        # if using Alpha 0, so we discard the black pixels from the distortion.  this helps make the entire region of interest is the full dimensions of the image (after undistort)
        # if using Alpha 1, we retain the black pixels, and obtain the region of interest as the valid pixels for the matrix.
        # i will use Apha 1, so that I don't have to run undistort.. and can just calculate my real world x,y
        newcam_mtx, roi = cv2.getOptimalNewCameraMatrix(cam_mtx, dist, (w, h), 1, (w, h))

        print("Region of Interest")
        print(roi)
        # np.save(self.folder + '/roi.npy', roi)

        print("New Camera Matrix")
        # print(newcam_mtx)
        np.save(self.folder + '/newcam_mtx.npy', newcam_mtx)
        print(np.load(self.folder + '/newcam_mtx.npy'))

    def undistort(self, img1, viz=False):
        undst = cv2.undistort(img1, self.cam_mtx, self.dist, None, self.newcam_mtx)
        
        if viz:
            cv2.imshow('raw', img1)
            cv2.imshow('undst', undst)
            k = cv2.waitKey(0)
            # Exiting the window if 'q'/ESC is pressed on the keyboard. 
            if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
                cv2.destroyAllWindows()
            
        return undst
        
    def color_filter(self, img, light, dark):
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_img, light, dark)
        segment = cv2.bitwise_and(img, img, mask=mask)
        return segment
        
    def get_perspective(self, img):
        # Target at wall
        segment = self.color_filter(img, 
            self.dict_role_hsv["wall"]["light"], 
            self.dict_role_hsv["wall"]["dark"])
        
        if np.sum(segment) == 0:
            raise ValueError("Xinyi: Can not detect color of wall in this image")
            sys.exit(1)
        if False:
            cv2.imshow('raw', img)
            cv2.imshow('seg', segment)
            # k = cv2.waitKey(0)
            # # Exiting the window if 'q'/ESC is pressed on the keyboard. 
            # if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
                # cv2.destroyAllWindows()
            
        # Filter out noisy shapes and smooth the edges
        # Note: kernel size is depend on the puzzle in image
        kernel = np.ones((10,10),np.uint8)
        segment = cv2.morphologyEx(segment, cv2.MORPH_OPEN, kernel)
        segment = cv2.morphologyEx(segment, cv2.MORPH_CLOSE, kernel)
        if False:
            cv2.imshow('filtered', segment)
            k = cv2.waitKey(0)
            # Exiting the window if 'q'/ESC is pressed on the keyboard. 
            if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
                cv2.destroyAllWindows()
                img_name = os.path.join(self.folder, "{}.png".format("filt"))
                cv2.imwrite(img_name, segment)
        # Get outermost contour
        list_contour, list_yolo_form = coordinates.get_rect(segment, bg='black', skew=True)
        
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
            
    def bird_view(self, img):
        warped = cv2.warpPerspective(img, self.M, (self.warped_w, self.warped_h))
        
        return warped


if __name__ == '__main__':
    cam = myCamera(id=0)
    # cam.camera_view(robot=False)
    
    # cam.calibration()
    # files = [filename for filename in os.listdir(cam.folder) if filename.startswith('frame_')]
    # img_name = os.path.join(cam.folder, files[-1])
    # img1 = cv2.imread(img_name)
    # cam.undistort(img1)
    
    fn = os.path.join(base_dir, 'map/2.png') # 'shapes.png'
    img = cv2.imread(fn)
    cam.get_perspective(img)