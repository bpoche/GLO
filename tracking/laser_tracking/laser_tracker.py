#! /usr/bin/env python
import sys
import argparse
import cv2
import numpy
import numpy as np
import time
import pandas as pd
import os, errno
import glob

class LaserTracker(object):

    def __init__(self,file_loc="",first=0,last=None,delay=.01, cam_width=640, cam_height=480, hue_min=20, hue_max=160,
                 sat_min=100, sat_max=255, val_min=200, val_max=256,
                 display_thresholds=False,save_data=False,data_loc=None,save_images=True):
        """
        * ``cam_width`` x ``cam_height`` -- This should be the size of the
        image coming from the camera. Default is 640x480.

        HSV color space Threshold values for a RED laser pointer are determined
        by:

        * ``hue_min``, ``hue_max`` -- Min/Max allowed Hue values
        * ``sat_min``, ``sat_max`` -- Min/Max allowed Saturation values
        * ``val_min``, ``val_max`` -- Min/Max allowed pixel values

        If the dot from the laser pointer doesn't fall within these values, it
        will be ignored.

        * ``display_thresholds`` -- if True, additional windows will display
          values for threshold image channels.

        """
        self.file_loc = file_loc
        self.first = first
        self.last = last
        self.delay = delay
        self.cam_width = cam_width
        self.cam_height = cam_height
        self.hue_min = hue_min
        self.hue_max = hue_max
        self.sat_min = sat_min
        self.sat_max = sat_max
        self.val_min = val_min
        self.val_max = val_max
        self.display_thresholds = display_thresholds
        self.save_data = save_data
        self.data_loc = data_loc
        self.save_images = save_images
        self.capture = None  # camera capture device
        self.channels = {
            'hue': None,
            'saturation': None,
            'value': None,
            'laser': None,
        }

        self.previous_position = None
        self.radius= None
        self.trail = numpy.zeros((self.cam_height, self.cam_width, 3),
                                 numpy.uint8)
        #self.save_file_name = self.data_loc + self.file.split('100GOPRO/')[1].split('.MP4')[0] + '_'+str(self.first)+'_'+str(self.last) + '.csv'
        self.save_file_name=self.data_loc + '/'+ self.file_loc.rsplit('/')[-1].split('.')[0]+'.csv'
        self.font = font = cv2.FONT_HERSHEY_SIMPLEX
        
    def create_and_position_window(self, name, xpos, ypos):
        """Creates a named widow placing it on the screen at (xpos, ypos)."""
        # Create a window
        cv2.namedWindow(name)
        # Resize it to the size of the camera image
        cv2.resizeWindow(name, self.cam_width, self.cam_height)
        # Move to (xpos,ypos) on the screen
        cv2.moveWindow(name, xpos, ypos)

    def setup_camera_capture(self, device_num=0):
        """Perform camera setup for the device number (default device = 0).
        Returns a reference to the camera Capture object.

        """
#        try:
#            device = int(device_num)
#            sys.stdout.write("Using Camera Device: {0}\n".format(device))
#        except (IndexError, ValueError):
#            # assume we want the 1st device
#            device = 0
#            sys.stderr.write("Invalid Device. Using default device 0\n")

        # Try to start capturing frames
        #self.capture = cv2.VideoCapture(device)
        #self.capture = cv2.VideoCapture("D:/DCIM/100GOPRO/GOPR0132.MP4 ")
        print(self.file_loc)
        self.capture = cv2.VideoCapture(self.file_loc)
        if not self.capture.isOpened():
            sys.stderr.write("Faled to Open Capture device. Quitting.\n")
            sys.exit(1)

        # set the wanted image size from the camera
#        self.capture.set(
#            cv2.cv.CV_CAP_PROP_FRAME_WIDTH if cv2.__version__.startswith('2') else cv2.CAP_PROP_FRAME_WIDTH,
#            self.cam_width
#        )
#        self.capture.set(
#            cv2.cv.CV_CAP_PROP_FRAME_HEIGHT if cv2.__version__.startswith('2') else cv2.CAP_PROP_FRAME_HEIGHT,
#            self.cam_height
#        )
        return self.capture

    def handle_quit(self, delay=10):
        """Quit the program if the user presses "Esc" or "q"."""
        key = cv2.waitKey(delay)
        c = chr(key & 255)
        if c in ['c', 'C']:
            self.trail = numpy.zeros((self.cam_height, self.cam_width, 3),
                                     numpy.uint8)
        if c in ['q', 'Q', chr(27)]:
            sys.exit(0)

    def threshold_image(self, channel):
        if channel == "hue":
            minimum = self.hue_min
            maximum = self.hue_max
        elif channel == "saturation":
            minimum = self.sat_min
            maximum = self.sat_max
        elif channel == "value":
            minimum = self.val_min
            maximum = self.val_max

        (t, tmp) = cv2.threshold(
            self.channels[channel],  # src
            maximum,  # threshold value
            0,  # we dont care because of the selected type
            cv2.THRESH_TOZERO_INV  # t type
        )

        (t, self.channels[channel]) = cv2.threshold(
            tmp,  # src
            minimum,  # threshold value
            255,  # maxvalue
            cv2.THRESH_BINARY  # type
        )

        if channel == 'hue':
            # only works for filtering red color because the range for the hue
            # is split
            self.channels['hue'] = cv2.bitwise_not(self.channels['hue'])

    def track(self, frame, mask):
        """
        Track the position of the laser pointer.

        Code taken from
        http://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
        """
        x, y = None, None
        radius = None

        countours = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                     cv2.CHAIN_APPROX_SIMPLE)[-2]

        # only proceed if at least one contour was found
        if len(countours) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(countours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            moments = cv2.moments(c)
            if moments["m00"] > 0:
                center = int(moments["m10"] / moments["m00"]), \
                         int(moments["m01"] / moments["m00"])
            else:
                center = int(x), int(y)
            #print(x,y,radius)
            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame,
                cv2.circle(frame, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                # then update the ponter trail
                #if self.previous_position:
                 #   print(center)
                 #   cv2.line(self.trail, self.previous_position, center,
                 #            (255, 255, 255), 2)

        #cv2.add(self.trail, frame, frame)
        self.previous_position = x, y
        self.radius = radius


    def detect(self, frame):
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # split the video frame into color channels
        h, s, v = cv2.split(hsv_img)
        self.channels['hue'] = h
        self.channels['saturation'] = s
        self.channels['value'] = v

        # Threshold ranges of HSV components; storing the results in place
        self.threshold_image("hue")
        self.threshold_image("saturation")
        self.threshold_image("value")

        # Perform an AND on HSV components to identify the laser!
        self.channels['laser'] = cv2.bitwise_and(
            self.channels['hue'],
            self.channels['value']
        )
        self.channels['laser'] = cv2.bitwise_and(
            self.channels['saturation'],
            self.channels['laser']
        )

        # Merge the HSV components back together.
        hsv_image = cv2.merge([
            self.channels['hue'],
            self.channels['saturation'],
            self.channels['value'],
        ])

        self.track(frame, self.channels['laser'])

        return hsv_image

    def display(self, img, frame,frame_cnt):
        """Display the combined image and (optionally) all other image channels
        NOTE: default color space in OpenCV is BGR.
        """
        cv2.putText(frame,'frame = '+str(frame_cnt),(300,650), self.font, 1,(255,0,255),2,cv2.LINE_AA)
        cv2.putText(frame,'elapsed = '+str(round(self.capture.get(cv2.CAP_PROP_POS_MSEC),1))+' ms',(300,700), self.font, 1,(255,0,255),2,cv2.LINE_AA)
        
        frame_cnt_str=str(frame_cnt).rjust(5,'0')
        imgfile=self.save_file_name.rstrip('.csv')
        vid_name=imgfile.rsplit('/',1)[1]
        imgfolder=imgfile.rsplit('/',1)[0]+'/'+vid_name
        try:
            os.makedirs(imgfolder)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        if self.save_images==True:
            cv2.imwrite(imgfolder+'/'+vid_name+'_'+frame_cnt_str+'.png',frame)
        if frame_cnt % 10 == 0:
            cv2.imshow('RGB_VideoFrame', frame)
            cv2.imshow('LaserPointer', self.channels['laser'])
            if self.display_thresholds:
                cv2.imshow('Thresholded_HSV_Image', img)
                cv2.imshow('Hue', self.channels['hue'])
                cv2.imshow('Saturation', self.channels['saturation'])
                cv2.imshow('Value', self.channels['value'])

    def setup_windows(self):
        sys.stdout.write("Using OpenCV version: {0}\n".format(cv2.__version__))

        # create output windows
        self.create_and_position_window('LaserPointer', 0,400 )
        self.create_and_position_window('RGB_VideoFrame',
                                        0, 400+self.cam_height)
        if self.display_thresholds:
            self.create_and_position_window('Thresholded_HSV_Image', 10, 10)
            self.create_and_position_window('Hue', 20, 20)
            self.create_and_position_window('Saturation', 30, 30)
            self.create_and_position_window('Value', 40, 40)

    def run(self):
        # Set up window positions
        self.setup_windows()
        # Set up the camera capture
        self.setup_camera_capture()
        data = pd.DataFrame(columns=['time_elapsed','laser_cen_x','laser_cen_y','laser_radius','laser_on'])
        frame_cnt=0
        while True:
            # 1. capture the current image
            success, frame = self.capture.read()
            frame_cnt+=1
            if not success:  # no image captured... end the processing
                sys.stderr.write("Could not read camera frame. Quitting\n")
                return data
                sys.exit(1)
            if frame_cnt > self.first:
                if self.previous_position != None:
                    data.loc[frame_cnt] = [self.capture.get(cv2.CAP_PROP_POS_MSEC),
                                           self.previous_position[0],
                                           self.previous_position[1],
                                           self.radius,
                                           'True']
                if self.previous_position == None:
                    data.loc[frame_cnt] = [self.capture.get(cv2.CAP_PROP_POS_MSEC),
                                           np.nan,
                                           np.nan,
                                           np.nan,
                                           'False']
                hsv_image = self.detect(frame)
                self.display(hsv_image, frame,frame_cnt)
                self.handle_quit()
                time.sleep(self.delay)
               # input('frame = '+str(frame_cnt)+' press enter for next frame')
            if self.last != None:
                if frame_cnt > self.last:
                    sys.stderr.write("Reached last frame\n")
                    #input('press enter to exit\n>>>')
                    data.to_csv(self.save_file_name,index_label='frame')
                    return data                
                    sys.exit(1)
            elif self.last == None:
                if frame_cnt >= self.capture.get(cv2.CAP_PROP_FRAME_COUNT) - 1:
                    sys.stderr.write("Reached last frame\n")
                    #input('press enter to exit\n>>>')
                    data.to_csv(self.save_file_name,index_label='frame')
                    return data
                    sys.exit(1)
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Laser Tracker')
    parser.add_argument('-f', '--file_loc',
                        default="/tesla/data/ISM_VIDEO/GOPR0124.MP4",#None,#"D:/DCIM/100GOPRO/GOPR0132.MP4",
                        type=str,
                        help='Location of video file')
    parser.add_argument('-F', '--first',
                        default=0,
                        type=int,
                        help='First frame to capture')
    parser.add_argument('-L', '--last',
                        default=None,
                        type=int,
                        help='Last frame to capture')
    parser.add_argument('-D', '--delay',
                        default=.001,
                        type=float,
                        help='Number of seconds to wait between frames')
    parser.add_argument('-W', '--width',
                        default=1280,
                        type=int,
                        help='Camera Width')
    parser.add_argument('-H', '--height',
                        default=720,
                        type=int,
                        help='Camera Height')
    parser.add_argument('-u', '--huemin',
                        default=20,
                        type=int,
                        help='Hue Minimum Threshold')
    parser.add_argument('-U', '--huemax',
                        default=160,
                        type=int,
                        help='Hue Maximum Threshold')
    parser.add_argument('-s', '--satmin',
                        default=100,
                        type=int,
                        help='Saturation Minimum Threshold')
    parser.add_argument('-S', '--satmax',
                        default=255,
                        type=int,
                        help='Saturation Maximum Threshold')
    parser.add_argument('-v', '--valmin',
                        default=200,
                        type=int,
                        help='Value Minimum Threshold')
    parser.add_argument('-V', '--valmax',
                        default=255,
                        type=int,
                        help='Value Maximum Threshold')
    parser.add_argument('-t', '--display',
                        default='store_true',
                        help='Display Threshold Windows')
    parser.add_argument('-d', '--data_loc',
                        default="/tesla/data/ISM_VIDEO/",
                        help='Display Threshold Windows')
    parser.add_argument('-i', '--save_data',
                        default=True,
                        help='Save every frame as .png')
    params = parser.parse_args()
    
    mp4dir=params.file_loc.rsplit('/',1)[0]
    
    tracker = LaserTracker(
        file_loc=params.file_loc,
        first=params.first,
        last=params.last,
        delay=params.delay,
        cam_width=params.width,
        cam_height=params.height,
        hue_min=params.huemin,
        hue_max=params.huemax,
        sat_min=params.satmin,
        sat_max=params.satmax,
        val_min=params.valmin,
        val_max=params.valmax,
        display_thresholds=params.display,
        save_data=params.save_data,
        data_loc=params.data_loc,   #'C:/git_repos/GLO/tracking/ISM_testing/data/'
    )
    
    # Get list of mp4 dir
    mp4list=glob.glob(params.data_loc+'/'+'GOPR*.MP4')
    mp4list.sort()
    
    for tfile in mp4list:
        #get the csv file name
        rt_file=tfile.rsplit('/')[-1].rstrip('.mp4').rstrip('.MP')
        print('Woring on '+rt_file)
        if not os.path.isfile(mp4dir+'/'+rt_file+'.csv'):
            params.file_loc=tfile
            tracker = LaserTracker(
                    file_loc=params.file_loc,
                    first=params.first,
                    last=params.last,
                    delay=params.delay,
                    cam_width=params.width,
                    cam_height=params.height,
                    hue_min=params.huemin,
                    hue_max=params.huemax,
                    sat_min=params.satmin,
                    sat_max=params.satmax,
                    val_min=params.valmin,
                    val_max=params.valmax,
                    display_thresholds=params.display,
                    save_data=params.save_data,
                    data_loc=params.data_loc,   #'C:/git_repos/GLO/tracking/ISM_testing/data/'
                    )
            data = tracker.run()
        else:
            print('CSV already completed')

