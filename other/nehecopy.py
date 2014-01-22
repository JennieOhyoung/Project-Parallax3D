import sys

import cv
import numpy as np

import OpenGL
from OpenGL.GL import *
from OpenGL.GL.ARB import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import time

from OpenGL.arrays import vbo
from OpenGLContext.arrays import *
from OpenGL.GL import shaders

from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()


def is_rect_nonzero(r):
    (_,_,w,h) = r
    return (w > 0) and (h > 0)


# print instructions in terminal 
        # print( "Keys:\n"
        #     "    ESC - quit the program\n"
        #     "    b - switch to/from backprojection view\n"
        #     "To initialize tracking, drag across the object with the mouse\n" )


class TestContext(BaseContext):

    def __init__(self):
        print "GL is running!"
        self.capture = cv.CaptureFromCAM(0)
        cv.NamedWindow( "CamShiftDemo", cv.CV_WINDOW_NORMAL)
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

    def OnIdle( self, ):
        """Request refresh of the context whenever idle.
        track, get position, update camera, then redraw"""
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

# find centroid coordinate (x,y) and area (z)
                selection_centroid = track_box[0]
                global xposition
                xposition = selection_centroid[0]
                global yposition
                yposition = selection_centroid[1]
                width_height = track_box[1]


# writes output of coordinates to seed file if needed
                # with open('seed.txt', 'a') as f:
                #     value = (xposition, yposition)
                #     s = str(value) + '\n'
                #     f.write(s)
                #     # f.write('end_of_session')
                # f.close()

# print outs
                print "x: " + str(xposition)
                print "y: " + str(yposition)
                selection_area = width_height[0]*width_height[1]
                # print "The width is: " + str(width_height[0]) + " The height is: " + str(width_height[1])
                # print "centroid is: " + str(selection_centroid)
                # return "centroid is: " + str(selection_centroid)
                print "area: " + str(selection_area)
                # return "area is: " + str(selection_area)

            if not backproject_mode:
                cv.ShowImage( "CamShiftDemo", frame )
            else:
                cv.ShowImage( "CamShiftDemo", backproject)
            cv.ShowImage( "Histogram", self.hue_histogram_as_image(hist))

            c = cv.WaitKey(10)
            if c == 27: # escape key
                break
            elif c == ord("b"): # show backproject mode with "b" key
                backproject_mode = not backproject_mode

        self.triggerRedraw(1)        
        return 1

    def initGL(self, width, height):
        # This part only runs once, the setup of my surrounding. 
        glClearColor(0.0, 0.0, 0.0, 1.0) #rgba (alpha is transparency)
        glClearDepth(1.0) #depth buffer- constraint where closer pixle has higher priority when drawn. 
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # glShadeModel(GL_SMOOTH) 
        glViewport(0, 0, width, height) # setup viewport and perspective model. Specify the lower left corner of the viewport rectangle, in pixels with X and Y. width and height = glut window size.
        glMatrixMode(GL_PROJECTION) #Applies subsequent matrix operations to the projection matrix stack. Other stacks are modelview, texture, color
        glLoadIdentity() #clears up previous mat

# set up camera
        gluLookAt((xposition-640)/100, (yposition-360)/100, 0.0,
            0.0, 0.0,  -5.0,
            0.0, 1.0,  0.0)


        gluPerspective(45.0, float(width)/float(height), 1.0, 500.0) #(angle, ratio, distance from viewer to near plane, distance from viewer to far plane. aka frustum perspective
        glMatrixMode(GL_MODELVIEW) #glMatrixMode sets the current matrix mode: modelview, projection, texture or color
        glDisable(GL_LIGHTING) # context automatically enables lighting to avoid a common class of new user errors where unlit geometry does not appear due to lack of light.
        #glEnable( GL_CULL_FACE ) #Prevents OpenGL from removing faces which face backward
        glEnable( GL_DEPTH_TEST )
        glDepthFunc( GL_LEQUAL )

    # def OnIdle(self,):
    #     #Request refresh of the context whenever idle
    #     self.triggerRedraw(1)
    #     return 1

    def render(self, mode=0):
        print "render is printing"
        # This is the part that loops over and over
        """Render the geometry for the scene."""
        # BaseContext.render(self,mode) <-- makes screen blank again
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # glutSolidSphere(0.75,20,20);
        # BaseContext.render
        glLoadIdentity()
        
# draw ground
        glPushMatrix()
        glTranslatef(0.0,0.0,-100.0)
        glRotatef(91.0, 1.0, 0.0, 0.0)
        glColor3f(0.184314, 0.309804, 0.309804) #gray
        glBegin(GL_QUADS)
        glVertex3f(-100.0, 100.0, 0.0)
        glVertex3f( 100.0, 100.0, 0.0)
        glVertex3f( 100.0, -100.0, 0.0)
        glVertex3f(-100.0, -100.0, 0.0)
        glEnd()
        glPopMatrix()

# draw pyramid
        glPushMatrix()
        glTranslatef(-5.0,0.0,-50.0) #Moves the drawing origin z units into the screen and x units to the left
        glRotated(time.time()%(2.0)/1 * 360, 0,1,0)
        self.drawPyramid()
        glPopMatrix()

# draw pyramid2
        glPushMatrix()
        glTranslatef(0.6,0.0,-5.0)
        glRotated(time.time()%(2.0)/1 * 360, 0,1,0)
        self.drawPyramid()
        glPopMatrix()

# draw pyramid3
        glPushMatrix()
        glTranslatef(-3, 0.0,-10.0)
        glRotated(time.time()%(2.0)/1 * 360, 0,1,0)
        self.drawPyramid()
        glPopMatrix()

# draw cube
        # glLoadIdentity()
        # glTranslatef(-5.0, 0.0,-20.0);
        # glRotated( time.time()%(1.0)/1 * -360, 1,0,0)
        # self.drawCube()

# draw 36 cubes
        # for i in range(-3, 3):
        #     for j in range(-3, 3):
        #         # glPushMatrix()
        #         glLoadIdentity()
        #         glTranslatef( i*1.0, 1, j*-1.0)
        #         self.drawCube()
                # glPopMatrix()


        # glBegin(GL_TRIANGLES) #Starts the (legacy) geometry generation mode
        # glColor3f(1,0,0)
        # glVertex3f( 0.0,  1.0, 0.0)
        # glColor3f(0,1,0)
        # glVertex3f(-1.0, -1.0, 0.0)
        # glColor3f(0,0,1)
        # glVertex3f( 1.0, -1.0, 0.0)
        # glEnd()
        # glTranslatef(3.0,0.0,0.0) #Moves the drawing origin again, cumulative change is now (1.5,0.0,6.0)

        # glLoadIdentity()
        # glTranslatef(1.5,0.0,-6.0)

        # glRotated( time.time()%(1.0)/1 * -360, 1,0,0)
        # # glColor3f(0.5, 0.5, 1.0)
        # glBegin(GL_QUADS)
        # glColor3f(1,0,0)
        # glVertex3f(-1.0,-1.0, 0.0)
        # glColor3f(0.5, 0.5, 1.0)
        # glVertex3f( 1.0,-1.0, 0.0)
        # glColor3f(0,1,0)
        # glVertex3f( 1.0, 1.0, 0.0)
        # glColor3f(0,0,1)
        # glVertex3f(-1.0, 1.0, 0.0)
        # glEnd();
        glutSwapBuffers()


    def drawPyramid(self):
        glBegin(GL_TRIANGLES);
        glColor3f(1.0,0.0,0.0)
        glVertex3f( 0.0, 1.0, 0.0)
        glColor3f(0.0,1.0,0.0)
        glVertex3f(-1.0,-1.0, 1.0)
        glColor3f(0.0,0.0,1.0)
        glVertex3f( 1.0,-1.0, 1.0)
        glColor3f(1.0,0.0,0.0)
        glVertex3f( 0.0, 1.0, 0.0)
        glColor3f(0.0,0.0,1.0)
        glVertex3f( 1.0,-1.0, 1.0);
        glColor3f(0.0,1.0,0.0);
        glVertex3f( 1.0,-1.0, -1.0);
        glColor3f(1.0,0.0,0.0);
        glVertex3f( 0.0, 1.0, 0.0);
        glColor3f(0.0,1.0,0.0);
        glVertex3f( 1.0,-1.0, -1.0);
        glColor3f(0.0,0.0,1.0);
        glVertex3f(-1.0,-1.0, -1.0);
        glColor3f(1.0,0.0,0.0);
        glVertex3f( 0.0, 1.0, 0.0);
        glColor3f(0.0,0.0,1.0);
        glVertex3f(-1.0,-1.0,-1.0);
        glColor3f(0.0,1.0,0.0);
        glVertex3f(-1.0,-1.0, 1.0);
        glEnd()

    # def drawCube(self):
    #     glBegin(GL_QUADS);
    #     glColor3f(0.0,1.0,0.0)
    #     glVertex3f( 1.0, 1.0,-1.0)
    #     glVertex3f(-1.0, 1.0,-1.0)
    #     glVertex3f(-1.0, 1.0, 1.0)
    #     glVertex3f( 1.0, 1.0, 1.0)
    #     glColor3f(1.0,0.5,0.0)
    #     glVertex3f( 1.0,-1.0, 1.0)
    #     glVertex3f(-1.0,-1.0, 1.0)
    #     glVertex3f(-1.0,-1.0,-1.0)
    #     glVertex3f( 1.0,-1.0,-1.0)
    #     glColor3f(1.0,0.0,0.0)
    #     glVertex3f( 1.0, 1.0, 1.0)
    #     glVertex3f(-1.0, 1.0, 1.0)
    #     glVertex3f(-1.0,-1.0, 1.0)
    #     glVertex3f( 1.0,-1.0, 1.0)
    #     glColor3f(1.0,1.0,0.0)
    #     glVertex3f( 1.0,-1.0,-1.0)
    #     glVertex3f(-1.0,-1.0,-1.0)
    #     glVertex3f(-1.0, 1.0,-1.0)
    #     glVertex3f( 1.0, 1.0,-1.0)
    #     glColor3f(0.0,0.0,1.0)
    #     glVertex3f(-1.0, 1.0, 1.0)
    #     glVertex3f(-1.0, 1.0,-1.0)
    #     glVertex3f(-1.0,-1.0,-1.0)
    #     glVertex3f(-1.0,-1.0, 1.0)
    #     glColor3f(1.0,0.0,1.0)
    #     glVertex3f( 1.0, 1.0,-1.0)
    #     glVertex3f( 1.0, 1.0, 1.0)
    #     glVertex3f( 1.0,-1.0, 1.0)
    #     glVertex3f( 1.0,-1.0,-1.0)
    #     glEnd()


    def update(self):
        # so that we display what's being rendered on the back buffer
        glutPostRedisplay()


    def main(self):
        global window
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH) #double buffered - draw buffer in background altogether when done. Smoother output than single buffer, display as you draw
        glutInitWindowSize(1280,810)
        glutInitWindowPosition(0, 0)
        window = glutCreateWindow("Simple Window")
        glutDisplayFunc(self.render) #
        glutIdleFunc(self.update)
        self.initGL(1280,810)
        glutMainLoop() #infinite loop until program quits


if __name__ == "__main__":
    # demo = CamShiftDemo()
    # demo.run()
    TestContext().main()
    # nehe = TestContext()
    # nehe.main()

