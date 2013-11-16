#!/usr/bin/env python

import cv
import numpy 

def is_rect_nonzero(r):
    (_,_,w,h) = r
    return (w > 0) and (h > 0)

class CamShiftDemo:

    def __init__(self):
        self.capture = cv.CaptureFromCAM(0)
        cv.NamedWindow( "CamShiftDemo", 1 )
        cv.NamedWindow( "Histogram", 1 )
        cv.SetMouseCallback( "CamShiftDemo", self.on_mouse)

        self.drag_start = None      # Set to (x,y) when mouse starts drag
        self.track_window = None    # Set to rect when the mouse drag finishes

        print( "Keys:\n"
            "    ESC - quit the program\n"
            "    b - switch to/from backprojection view\n"
            "To initialize tracking, drag across the object with the mouse\n" )

    def hue_histogram_as_image(self, hist):
        """ Returns a nice representation of a hue histogram """
        # cv.CreateImage(size, depth<-Bit depth of image elements, channels<-Number of channels per pixel)
        histimg_hsv = cv.CreateImage( (320,200), 8, 3)
        
        #cv.CloneMatND(mat <- input array) 
        mybins = cv.CloneMatND(hist.bins)
        # The function log calculates the natural logarithm of the absolute value of every element of the input array
        # cv.Log(src <- input array, dst <- output array)
        cv.Log(mybins, mybins)
        
        #The functions minMaxLoc find the minimum and maximum element values and their positions. 
        #The extremums are searched across the whole array or, if mask is not an empty array, in the specified array region.
        #The functions do not work with multi-channel arrays. 
        #cv.MinMaxLoc(arr, mask=None)-> (minVal, maxVal, minLoc, maxLoc)
        (_, hi, _, _) = cv.MinMaxLoc(mybins)
        #cv.Convertscale(source array, destination array, scale factor, value added to scaled source array)
        cv.ConvertScale(mybins, mybins, 255. / hi)
        # The function returns number of rows (CvSize::height) and number of columns (CvSize::width) of the input matrix or image. 
        #In the case of image the size of ROI is returned.
        w,h = cv.GetSize(histimg_hsv)
        #The function returns the array dimensionality and the array of dimension sizes. 
        #cv.GetDims(arr) -> (dim1, dim2, ...)
        hdims = cv.GetDims(mybins)[0]
        for x in range(w):
            xh = (180 * x) / (w - 1)  # hue sweeps from 0-180 across the image
            val = int(mybins[int(hdims * x / w)] * h / 255)
            cv.Rectangle( histimg_hsv, (x, 0), (x, h-val), (xh,255,64), -1)
            cv.Rectangle( histimg_hsv, (x, h-val), (x, h), (xh,255,255), -1)

        histimg = cv.CreateImage( (320,200), 8, 3)
        '''cv.CvtColor(src, dst, code) → None
            The function converts an input image from one color space to another. In case of a transformation to-from RGB color space, the order of the channels should be specified explicitly (RGB or BGR). Note that the default color format in OpenCV is often referred to as RGB but it is actually BGR.
        '''
        cv.CvtColor(histimg_hsv, histimg, cv.CV_HSV2BGR)
        return histimg

    def on_mouse(self, event, x, y, flags, param):
        #making selection with mouse event
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
        #cv.CreateHist(dims, type, ranges=None, uniform=1) → hist
        #The function creates a histogram of the specified size and returns a pointer to the created histogram. 
        #Type: Histogram representation format. CV_HIST_ARRAY means that the histogram data is represented as a multi-dimensional dense array CvMatND.
        hist = cv.CreateHist([180], cv.CV_HIST_ARRAY, [(0,180)], 1 )
        backproject_mode = False
        while True:
            # This is the most convenient method for reading video files or capturing data from decode and return the just grabbed frame. If no frames has been grabbed (camera has been disconnected, or there are no more frames in video file), the methods return false and the functions return NULL pointer.
            # cv.QueryFrame(capture) → image
            frame = cv.QueryFrame( self.capture )

            # Convert to HSV and keep the hue
            # cv.CreateImage(size, depth, channels) → image
            # channels <- Number of channels per pixel
            hsv = cv.CreateImage(cv.GetSize(frame), 8, 3)

            # converting back
            cv.CvtColor(frame, hsv, cv.CV_BGR2HSV)

            self.hue = cv.CreateImage(cv.GetSize(frame), 8, 1)
            # cv.Split(src, dst0, dst1, dst2, dst3) → None (action)
            # The functions split split a multi-channel array into separate single-channel arrays
            cv.Split(hsv, self.hue, None, None, None)

            # Compute back projection
            backproject = cv.CreateImage(cv.GetSize(frame), 8, 1)

            # Run the cam-shift
            # cv.CalcBackProject(image, backproject, hist) → None
            # backProject – Destination back projection array that is a single-channel array of the same size and depth as images[0] 
            cv.CalcArrBackProject( [self.hue], backproject, hist )
            if self.track_window and is_rect_nonzero(self.track_window):
                crit = ( cv.CV_TERMCRIT_EPS | cv.CV_TERMCRIT_ITER, 10, 1)
                (iters, (area, value, rect), track_box) = cv.CamShift(backproject, self.track_window, crit)
                self.track_window = rect

            # If mouse is pressed, highlight the current selected rectangle
            # and recompute the histogram

            if self.drag_start and is_rect_nonzero(self.selection):
                #The function returns header, corresponding to a specified rectangle of the input array. In other words, it allows the user to treat a rectangular part of input array as a stand-alone array. ROI is taken into account by the function so the sub-array of ROI is actually extracted.
                #cv.GetSubRect(arr, rect) → submat (Pointer to the resultant sub-array header)
                sub = cv.GetSubRect(frame, self.selection)
                #Creates a full copy of a matrix and returns a pointer to the copy. Note that the matrix copy is compacted, that is, it will not have gaps between rows.
                # cv.CloneMat(mat) → mat
                save = cv.CloneMat(sub)
                #cv.ConvertScale(src, dst, scale=1.0, shift=0.0) → None
                # The function has several different purposes, and thus has several different names. It copies one array to another with optional scaling, which is performed first, and/or optional type conversion
                cv.ConvertScale(frame, frame, 0.5)
                cv.Copy(save, sub)
                x,y,w,h = self.selection
                cv.Rectangle(frame, (x,y), (x+w,y+h), (255,255,255))

                # cv.GetSubRect(arr, rect) → submat
                # The function returns header, corresponding to a specified rectangle of the input array. In other words, it allows the user to treat a rectangular part of input array as a stand-alone array. ROI is taken into account by the function so the sub-array of ROI is actually extracted.
                sel = cv.GetSubRect(self.hue, self.selection )
                #The functions calcHist calculate the histogram of one or more arrays. The elements of a tuple used to increment a histogram bin are taken from the corresponding input arrays at the same location. The sample below shows how to compute a 2D Hue-Saturation histogram for a color image.
                # cv.CalcHist(image, hist, accumulate=0, mask=None) → None
                cv.CalcArrHist( [sel], hist, 0)

                #cv.GetMinMaxHistValue(hist)-> (min_value, max_value, min_idx, max_idx)
                # The function finds the minimum and maximum histogram bins and their positions. All of output arguments are optional. Among several extremas with the same value the ones with the minimum index (in the lexicographical order) are returned. In case of several maximums or minimums, the earliest in the lexicographical order (extrema locations) is returned.
                # min_value – Pointer to the minimum value of the histogram.
                # max_value – Pointer to the maximum value of the histogram.
                # min_idx – Pointer to the array of coordinates for the minimum.
                # max_idx – Pointer to the array of coordinates for the maximum
                (_, max_val, _, _) = cv.GetMinMaxHistValue( hist)
                if max_val != 0:
                    cv.ConvertScale(hist.bins, hist.bins, 255. / max_val)

            elif self.track_window and is_rect_nonzero(self.track_window):
                #cv.EllipseBox(img, box, color, thickness=1, lineType=8, shift=0) → None
                # The functions ellipse with less parameters draw an ellipse outline, a filled ellipse, an elliptic arc, or a filled ellipse sector. A piecewise-linear curve is used to approximate the elliptic arc boundary. If you need more control of the ellipse rendering, you can retrieve the curve using ellipse2Poly() and then render it with polylines() or fill it with fillPoly() . If you use the first variant of the function and want to draw the whole ellipse, not an arc, pass startAngle=0 and endAngle=360 . The figure below explains the meaning of the parameters.
                cv.EllipseBox( frame, track_box, cv.CV_RGB(255,0,0), 3, cv.CV_AA, 0 )

                #attempt 1:
                # convert image to grayscale, pick up contour and use conture c.centroid to get tuple (x,y)
                #attemt 2:
                # use track_box itself 
                c = Contour(frame, )

                # to track centroid, use moments -> dictionary, use keys to perform calculation ablove


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



"""
 # print coordinate of centroid
center_x = int(x+w/2)
center_y = int(y+h/2)
centroid = (center_x, center_y)
print centroid

"""
















