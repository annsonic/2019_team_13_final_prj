# https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
from __future__ import print_function
import datetime
from threading import Thread
import cv2
import imutils


class FPS:
    def __init__(self):
        # store the start time, end time, and total number of frames
        # that were examined between the start and end intervals
        self._start = None
        self._end = None
        self._numFrames = 0
 
    def start(self):
        # start the timer
        self._start = datetime.datetime.now()
        return self
 
    def stop(self):
        # stop the timer
        self._end = datetime.datetime.now()
 
    def update(self):
        # increment the total number of frames examined during the
        # start and end intervals
        self._numFrames += 1
 
    def elapsed(self):
        # return the total number of seconds between the start and
        # end interval
        return (self._end - self._start).total_seconds()
 
    def fps(self):
        # compute the (approximate) frames per second
        return self._numFrames / self.elapsed()
        

class WebcamVideoStream:
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src, cv2.CAP_DSHOW) 
        # solution to [ WARN:1] terminating async callback
        (self.grabbed, self.frame) = self.stream.read()
        
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
        
    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self
 
    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                self.stream.release()
                return
            
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()
 
    def read(self):
        # return the frame most recently read
        return self.frame
 
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


def test(cam_id=0):
    num_frames = 100
    display = 1
    
    print("[INFO] sampling THREADED frames from webcam...")
    vs = WebcamVideoStream(src=cam_id).start()
    fps = FPS().start()
    
    while True: #fps._numFrames < num_frames:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        frame = vs.read()
        frame = imutils.resize(frame, width=400)
        
        # check to see if the frame should be displayed to our screen
        if display > 0:
            cv2.imshow("Frame", frame)
            k = cv2.waitKey(1)
            
            if (k%256 == 27) or (k%256 == 81) or (k%256 == 113):  
                cv2.destroyAllWindows()
                break
        # update the FPS counter
        fps.update()
    
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    
    # do a bit of cleanup
    # cv2.destroyAllWindows()
    vs.stop()
    
if __name__ == '__main__':
    test()