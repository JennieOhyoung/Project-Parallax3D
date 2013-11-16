#!/usr/bin/env python

import cv
import cv2
import numpy as np

def is_rect_nonzero(r):
    (_,_,w,h) = r
    return (w > 0) and (h > 0)

class CamShiftDemo:

    def __init__(self):
        self.capture = cv.CaptureFromCAM(0)
        cv.NamedWindow( "CamShiftDemo", )
        cv.NamedWindow( "Histogram", 1 )
        cv.SetMouseCallback( "CamShiftDemo", self.on_mouse)

        # find middle of screen 
        frame = cv.QueryFrame(self.capture)
        self.midScreenX = (frame.width/2)
        self.midScreenY = (frame.height/2)
        self.midScreen = (self.midScreenX, self.midScreenY)
        print "This is the center of the screen: " + str(self.midScreen)

        self.drag_start = None      # Set to (x,y) when mouse starts drag
        self.track_window = None    # Set to rect when the mouse drag finishes

        # print( "Keys:\n"
        #     "    ESC - quit the program\n"
        #     "    b - switch to/from backprojection view\n"
        #     "To initialize tracking, drag across the object with the mouse\n" )

    def hue_histogram_as_image(self, hist):
        """ Returns a nice representation of a hue histogram """
        histimg_hsv = cv.CreateImage( (320,200), 8, 3)
        mybins = cv.CloneMatND(hist.bins)
        cv.Log(mybins, mybins)
        
        (_, hi, _, _) = cv.MinMaxLoc(mybins)
        cv.ConvertScale(mybins, mybins, 255. / hi)

        w,h = cv.GetSize(histimg_hsv)
        hdims = cv.GetDims(mybins)[0]
        for x in range(w):
            xh = (180 * x) / (w - 1)  # hue sweeps from 0-180 across the image
            val = int(mybins[int(hdims * x / w)] * h / 255)
            cv.Rectangle( histimg_hsv, (x, 0), (x, h-val), (xh,255,64), -1)
            cv.Rectangle( histimg_hsv, (x, h-val), (x, h), (xh,255,255), -1)

        histimg = cv.CreateImage( (320,200), 8, 3)
        cv.CvtColor(histimg_hsv, histimg, cv.CV_HSV2BGR)
        return histimg

    def on_mouse(self, event, x, y, flags, param):
        if event == cv.CV_EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
        if event == cv.CV_EVENT_LBUTTONUP:
            self.drag_start = None
            self.track_window = self.selection
        if self.drag_start:
            xmin = min(x, self.drag_start[0])
            ymin = min(y, self.drag_start[1])
            xmax = max(x, self.drag_start[0])
            ymax = max(y, self.drag_start[1])
            self.selection = (xmin, ymin, xmax - xmin, ymax - ymin)

    def run(self):
        hist = cv.CreateHist([180], cv.CV_HIST_ARRAY, [(0,180)], 1 )
        backproject_mode = False
        while True:
            frame = cv.QueryFrame(self.capture)

            # Convert to HSV and keep the hue
            hsv = cv.CreateImage(cv.GetSize(frame), 8, 3)
            cv.CvtColor(frame, hsv, cv.CV_BGR2HSV)
            self.hue = cv.CreateImage(cv.GetSize(frame), 8, 1)
            cv.Split(hsv, self.hue, None, None, None)

            # Compute back projection
            backproject = cv.CreateImage(cv.GetSize(frame), 8, 1)

            # Run the cam-shift
            cv.CalcArrBackProject( [self.hue], backproject, hist )
            if self.track_window and is_rect_nonzero(self.track_window):
                crit = ( cv.CV_TERMCRIT_EPS | cv.CV_TERMCRIT_ITER, 10, 1)
                (iters, (area, value, rect), track_box) = cv.CamShift(backproject, self.track_window, crit)
                self.track_window = rect

            # If mouse is pressed, highlight the current selected rectangle
            # and recompute the histogram

            if self.drag_start and is_rect_nonzero(self.selection):
                sub = cv.GetSubRect(frame, self.selection)
                save = cv.CloneMat(sub)
                cv.ConvertScale(frame, frame, 0.5)
                cv.Copy(save, sub)
                x,y,w,h = self.selection
                cv.Rectangle(frame, (x,y), (x+w,y+h), (0,0,255))

                sel = cv.GetSubRect(self.hue, self.selection )
                cv.CalcArrHist( [sel], hist, 0)
                (_, max_val, _, _) = cv.GetMinMaxHistValue( hist)
                if max_val != 0:
                    cv.ConvertScale(hist.bins, hist.bins, 255. / max_val)
            elif self.track_window and is_rect_nonzero(self.track_window):
                cv.EllipseBox(frame, track_box, cv.CV_RGB(255,0,0), 3, cv.CV_AA, 0 )

                # print track_box (center, size, angle)
                # cv.Circle(frame, frame.GetSize/2, 20, 3, 8, 0)
                # cv.Rectangle(frame, (x,y), (x+w,y+h), (0,0,255)

                #attempt 1
                # coordinates = cv.RotatedRect(track_box.center)
                # print coordinates

                #attempt 2
                # # calculating centroid (x,y) and area (z)
                # gray_frame = cv.CreateImage(cv.GetSize(frame), 8, 3)
                # copy_frame = cv.CreateImage(cv.GetSize(frame), 8, 3)
                # # cv.CvtColor(frame, hsv, cv.CV_BGR2HSV)   
                # cv.CvtColor(copy_frame, gray_frame, cv.CV_BGR2GRAY)
                # c = Contour(gray_frame, contour)
                # # # point_x = c.centroid[0]
                # # # point_y = c.centroid[1]
                # # # assuming user is 1ft away from center of projection, 
                # # # area of ellipse = math.pi * w/2 * h/2
                # # # z = c.area 
                # # # point_z = 
                # print "this should be the list of centroid coordinates"
                # print c.centroid
                # # # print c.

                #attempt 3
                # circle(frame,track_box.center,5,Scalar(0,255,0))
                # print track_box.center.x
                # print track_box.center.y

                center= track_box[0]
                width_height = track_box[1]
                print "centroid is: " + str(center)
                # print "width and height is: " + str(lower_right_corner)

            if not backproject_mode:
                cv.ShowImage( "CamShiftDemo", frame )
            else:
                cv.ShowImage( "CamShiftDemo", backproject)
            cv.ShowImage( "Histogram", self.hue_histogram_as_image(hist))

            c = cv.WaitKey(7)
            if c == 27:
                break
            elif c == ord("b"):
                backproject_mode = not backproject_mode






if __name__=="__main__":
    demo = CamShiftDemo()
    demo.run()