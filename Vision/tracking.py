import cv2
import sys
import numpy as np
import re
import os
import imutils
base_dir = os.path.abspath(os.path.dirname(__file__))
import camera

def test():
    cam = camera.myCamera(id=0)
    
    # # cam.camera_view()
    ret, frame = cam.cam.read()
    frame = cam.undistort(frame)
    
    # # cv2.imshow("Original", frame)
    # files = [filename for filename in os.listdir(cam.folder) if filename.startswith("2019")]
    # files = sorted(files, key=lambda x:float(re.findall("(\d+)",x)[0]))
    # img_name = os.path.join(cam.folder, files[-1])
    
    # cv2.imwrite(img_name, frame)
    
    # frame = cv2.imread(img_name)
    # # print("Step(3) Calculate perspective transformation matrix")
    # # cam.get_perspective(frame, area=26000)

    
    # if True:
        # print("\tThis is the transformed view sample:")
        # warped = cam.bird_view(frame)
        
        # cv2.imshow("Original", frame)
        # cv2.imshow("Warped", warped)
            
          
        # k = cv2.waitKey(0)
        # # Exiting the window if 'q'/ESC is pressed on the keyboard. 
        # if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
            # cv2.destroyAllWindows()
    
    warped = cam.bird_view(frame)
    ##########################################
    
    # extract the OpenCV version info
    (major, minor) = cv2.__version__.split(".")[:2]
    str_tracker = "csrt"
    # if we are using OpenCV 3.2 OR BEFORE, we can use a special factory
    # function to create our object tracker
    if int(major) == 3 and int(minor) < 3:
        tracker = cv2.Tracker_create(str_tracker.upper())
     
    # otherwise, for OpenCV 3.3 OR NEWER, we need to explicity call the
    # approrpiate object tracker constructor:
    else:
        # initialize a dictionary that maps strings to their corresponding
        # OpenCV object tracker implementations
        OPENCV_OBJECT_TRACKERS = {
            "csrt": cv2.TrackerCSRT_create,
            "kcf": cv2.TrackerKCF_create,
            "boosting": cv2.TrackerBoosting_create,
            "mil": cv2.TrackerMIL_create,
            "tld": cv2.TrackerTLD_create,
            "medianflow": cv2.TrackerMedianFlow_create,
            "mosse": cv2.TrackerMOSSE_create
        }
     
        # grab the appropriate object tracker using our dictionary of
        # OpenCV object tracker objects
        tracker = OPENCV_OBJECT_TRACKERS[str_tracker]()
 
    # initialize the bounding box coordinates of the object we are going
    # to track
    initBB = None
    
    # initialize the FPS throughput estimator
    fps = None
    
    # loop over frames from the video stream
    while True:
        # grab the current frame, then handle if we are using a
        # VideoStream or VideoCapture object
        ret, frame = cam.cam.read()
        
        # frame = cam.undistort(frame)
        # warped = cam.bird_view(frame)
        # frame = frame[1] if args.get("video", False) else frame
     
        # check to see if we have reached the end of the stream
        if frame is None:
            break
     
        # resize the frame (so we can process it faster) and grab the
        # frame dimensions
        frame = imutils.resize(frame, width=500)
        (H, W) = frame.shape[:2]
        
        # check to see if we are currently tracking an object
        if initBB is not None:
            # grab the new bounding box coordinates of the object
            (success, box) = tracker.update(frame)
     
            # check to see if the tracking was a success
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                    (0, 255, 0), 2)
     
            # update the FPS counter
            fps.update()
            fps.stop()
     
            # initialize the set of information we'll be displaying on
            # the frame
            info = [
                ("Tracker", str_tracker),
                ("Success", "Yes" if success else "No"),
                ("FPS", "{:.2f}".format(fps.fps())),
            ]
     
            # loop over the info tuples and draw them on our frame
            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
            print('here')
            
        # show the output frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
     
        # if the 's' key is selected, we are going to "select" a bounding
        # box to track
        if key == ord("s"):
            # select the bounding box of the object we want to track (make
            # sure you press ENTER or SPACE after selecting the ROI)
            initBB = cv2.selectROI("Frame", frame, fromCenter=False,
                showCrosshair=True)
     
            # start OpenCV object tracker using the supplied bounding box
            # coordinates, then start the FPS throughput estimator as well
            tracker.init(frame, initBB)
            fps = FPS().start()
        # if the `q` key was pressed, break from the loop
        elif (key%256 == 27) or (key%256 == 81) or (key%256 == 113):
            break
     
    # if we are using a webcam, release the pointer
    # if not args.get("video", False):
        # vs.stop()
     
    # # otherwise, release the file pointer
    # else:
        # vs.release()
    cam.stop()
    # close all windows
    cv2.destroyAllWindows()
            
    
test()