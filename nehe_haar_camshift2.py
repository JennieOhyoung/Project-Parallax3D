import sys
import OpenGL
from OpenGL.GL import *
from OpenGL.GL.ARB import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import cv
import numpy as np
import time
#for lighting
from OpenGL.arrays import vbo
from OpenGLContext.arrays import *
from OpenGL.GL import shaders

from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()

FACE_CASCADE = cv.Load("haarcascade_frontalface_alt.xml")
        
""" Rendering Context with custom viewpoint and render. Note: will have slightly different results as OpenGLContext automatically enables lighting.
"""
class TestContext(BaseContext):
    haveCentroid = False
    selection = None
    hist = None

    def __init__(self):
        # print "GL is running!"
        self.last_face_centroid = (640, 360)
        self.capture = cv.CaptureFromCAM(0)
        
    def initGL(self, width, height):
        # This part only runs once, the setup of my surrounding. 
        glClearColor(0.0, 0.0, 0.0, 1.0) #rgba (alpha is transparency)
        glClearDepth(1.0) #depth buffer- constraint where closer pixle has higher priority when drawn. 
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # glShadeModel(GL_SMOOTH) 
        glViewport(0, 0, width, height) # setup viewport and perspective model. Specify the lower left corner of the viewport rectangle, in pixels with X and Y. width and height = glut window size.
        glMatrixMode(GL_PROJECTION) #Applies subsequent matrix operations to the projection matrix stack. Other stacks are modelview, texture, color
        # glLoadIdentity() #clears up previous mat


        gluPerspective(45.0, float(width)/float(height), 1.0, 500.0) #(angle, ratio, distance from viewer to near plane, distance from viewer to far plane. aka frustum perspective
        glMatrixMode(GL_MODELVIEW) #glMatrixMode sets the current matrix mode: modelview, projection, texture or color
        glDisable(GL_LIGHTING) # context automatically enables lighting to avoid a common class of new user errors where unlit geometry does not appear due to lack of light.
        #glEnable( GL_CULL_FACE ) #Prevents OpenGL from removing faces which face backward
        glEnable( GL_DEPTH_TEST )
        glDepthFunc( GL_LEQUAL )
    
    def render(self, mode=0):
        # print "RENDERING"
        # This is the part that loops over and over
        """Render the geometry for the scene."""
        # BaseContext.render(self,mode) <-- makes screen blank again
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # glutSolidSphere(0.75,20,20);
        # BaseContext.render
        
# draw ground
        glPushMatrix()
        glTranslatef(0.0,0.0,-100.0)
        glRotatef(96.0, 1.0, 0.0, 0.0)
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
        # glRotated(time.time()%(2.0)/1 * 360, 0,1,0)
        self.drawPyramid()
        glPopMatrix()

# draw pyramid2
        glPushMatrix()
        glTranslatef(0.6,0.0,-5.0)
        # glRotated(time.time()%(2.0)/1 * 360, 0,1,0)
        self.drawPyramid()
        glPopMatrix()

# draw pyramid3
        glPushMatrix()
        glTranslatef(-3, 0.0,-10.0)
        # glRotated(time.time()%(2.0)/1 * 360, 0,1,0)
        self.drawPyramid()
        glPopMatrix()
# draw pyramid4
        glPushMatrix()
        glTranslatef(-8, 0.0,-20.0)
        # glRotated(time.time()%(2.0)/1 * 360, 0,1,0)
        self.drawPyramid()
        glPopMatrix()


# draw pyramid5
        glPushMatrix()
        glTranslatef(5, 0.0,-8.0)
        # glRotated(time.time()%(2.0)/1 * 360, 0,1,0)
        self.drawPyramid()
        glPopMatrix()

# draw pyramid6
        glPushMatrix()
        glTranslatef(10, 0.0,-15.0)
        # glRotated(time.time()%(2.0)/1 * 360, 0,1,0)
        self.drawPyramid()
        glPopMatrix()

# draw pyramid7
        glPushMatrix()
        glTranslatef(-10, 0.0,-3.0)
        # glRotated(time.time()%(2.0)/1 * 360, 0,1,0)
        self.drawPyramid()
        glPopMatrix()


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

    def update(self):
        """ 1. captureImage
            2. if I don't have a centroid or if camshift no longer knows where the face is, 
                2.1 find centroid/bounding rect with Haar
                2.2 (re-)initialize camshift with the centroid/bounding rect extracted using Haar
            3. use camshift to update camera"""
        # 1. capture image
        img = get_image_from_camera(self.capture)

        # 2. check to see if we have a face centroid already
        if not self.haveCentroid:
            print "searching for face"
            # 2.1 use Haar
            roi_selection = detect_faces(img)
            if roi_selection != None:
                #print roi_selection
                # use roi_selection to see camshift
                self.selection, self.hist = setup_camshift(roi_selection, img)
                self.haveCentroid = True
        else:
            print "using found face"
            # 2.2 run camshift on the thing we think we have
            face_centroid_camshift, self.selection = compute_camshift_centroids(img, self.selection, self.hist)
            print face_centroid_camshift
            if face_centroid_camshift is None or self.selection is None:
                self.haveCentroid = False
            else:
                self.update_camera(face_centroid_camshift)

        # face_centroid = detect_faces(img)
        
        # if not face_centroid:
        #     print "no face detected"
        #     face_centroid = self.last_face_centroid
        """
        roi_selection = detect_faces(img) #2.1 run haar to find roi
        selection, hist = setup_camshift(roi_selection, img) #2.2 run camshift
        face_centroid_camshift = compute_camshift_centroids(img, selection, hist)
        self.update_camera(face_centroid_camshift)

        if roi_selection == None or face_centroid_camshift == None:
            roi_selection = detect_faces(img) #2.1 run haar to find roi
            selection, hist = setup_camshift(roi_selection, img) #2.2 run camshift
            face_centroid_camshift = compute_camshift_centroids(img, selection, hist)
        # else:
            self.update_camera(face_centroid_camshift)    
        """
        glutPostRedisplay()


    def update_camera(self, face_centroid_camshift):
        xposition = (face_centroid_camshift[0]-640)/float(2000)
        yposition = (face_centroid_camshift[1]-360)/float(2000)

        gluLookAt(xposition, yposition, 0.0,
            0.0, 0.0, -1.0,
            0.0, 1.0, 0.0)

        # print "x is: " + str(xposition) + "y is: " + str(yposition)


    def setup_window(self):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)#double buffered - draw buffer in background altogether when done. Smoother output than single buffer, display as you draw
        glutInitWindowSize(1280,810)
        glutInitWindowPosition(0, 0)
        window = glutCreateWindow("Simple Window")
        glutIdleFunc(self.update)
        glutDisplayFunc(self.render)
        self.initGL(1280,810)
        glutMainLoop()

def get_image_from_camera(capture):
    img = cv.QueryFrame(capture)
    return img

# returned face_centroid, now returns roi tuple in camshift
def detect_faces(img):

    image_scale = 2
    haar_scale = 1.1
    min_neighbors = 3
    haar_flags = 0
    min_size = (20,20)

    # Creating a grayscale image to do the calculation on
    grayscale = cv.CreateImage((img.width, img.height), 8, 1)
    cv.CvtColor(img, grayscale, cv.CV_BGR2GRAY)
    
    # scaling the image by the image_scale variable to speed up
    smallImage = cv.CreateImage(
            (
                cv.Round(img.width / image_scale),
                cv.Round(img.height / image_scale)
            ), 8 ,1)
    cv.Resize(grayscale, smallImage, cv.CV_INTER_LINEAR)
 
    # Enhances contrast in the image
    cv.EqualizeHist(smallImage, smallImage)
 
    # Detect the faces
    global faces
    faces = cv.HaarDetectObjects(
            smallImage, FACE_CASCADE, cv.CreateMemStorage(0),
            haar_scale, min_neighbors, haar_flags, min_size
        )

    if not faces:
        return None

    def compare_area(f1, f2):
        area1 = f1[0][2] * f1[0][3]
        area2 = f2[0][2] * f2[0][3]
        # print f1
        # print f2
        return area1 - area2

    sorted_faces = sorted(faces, cmp=compare_area)
    biggest_face = sorted_faces[-1]
    # face_centroid = get_centroid(biggest_face, image_scale)
    roi_selection = roi_points(biggest_face, image_scale) #pt1 pt2
    return roi_selection #tuple
    
# takes roi_selection from detect_faces and replaces on_mouse selection
# def camshift_track(roi_selection, img):
""" 
    setup_camshift:
        - is_rect_nonzero(r)
        - hue_histogram_as_image(hist)
        - making_selection(roi_selection)


    compute_camshift_centroid:
        - create_hist()
        - placeholder()
        - isolate_hue
        - compute_back_projection
        - recompute_histogram(roi_selection)
        - run_camshift
        - draw ellipse
        - find_centroid(track_box)
        - show_hist
"""
def is_rect_nonzero(rect):
    return (rect[2] > 0) and (rect[3] > 0)

def setup_camshift(roi_selection, img):

    hist = cv.CreateHist([180], cv.CV_HIST_ARRAY, [(0,180)], 1 )
    # backproject_mode = False

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

# making_selection 
    # print roi_selection[0]
    # print roi_selection[1]
    point1 = roi_selection[0]
    point2 = roi_selection[1]
    xmin = point1[0]
    ymin = point1[1]
    xmax = point2[0]
    ymax = point2[1]
    widthx = xmax-xmin
    heighty = ymax-ymin

    selection = (xmin, ymin, widthx, heighty)
    return selection, hist
# end of making_selection

def compute_camshift_centroids(img, selection, hist):
    # capture = cv.CaptureFromCAM(0)
    # frame = cv.QueryFrame(capture)

# isolate_hue
    # Convert to HSV and keep the hue
    hsv = cv.CreateImage(cv.GetSize(img), 8, 3)
    cv.CvtColor(img, hsv, cv.CV_BGR2HSV)
    hue = cv.CreateImage(cv.GetSize(img), 8, 1)
    cv.Split(hsv, hue, None, None, None)
# end isolate_hue


# Compute back projection
    backproject = cv.CreateImage(cv.GetSize(img), 8, 1)
# end compute back projection

# highlight the current selected rectangle and recompute the histogram
    # w = xmax - xmin
    # h = ymax - ymax
    # xmin,ymin,w,h = selection
    #cv.Rectangle(img, (selection[0],selection[1]), (selection[2], selection[3]), (0,0,255))
# end highlight

# Run the camshift
    cv.CalcArrBackProject( [hue], backproject, hist )
# end run camshift

# draw ellipse
    """"
    print "selection is" + str(selection)
    if selection:
    #and is_rect_nonzero(selection):
        # (iteration criteria, max, min)
        crit = ( cv.CV_TERMCRIT_EPS | cv.CV_TERMCRIT_ITER, 10, 1)
        (iters, (area, value, rect), track_box) = cv.CamShift(backproject, selection, crit)
        selection = rect

        # treats selection as independent array
        sel = cv.GetSubRect(hue, selection)
        # calculate histogram for array
        cv.CalcArrHist( [sel], hist, 0)
        (_, max_val, _, _) = cv.GetMinMaxHistValue( hist)
        if max_val != 0:
            #cv.ConvertScale(src, dst, scale=1.0, shift=0.0) 
            cv.ConvertScale(hist.bins, hist.bins, 255. / max_val)
    elif selection:
    """
    crit = ( cv.CV_TERMCRIT_EPS | cv.CV_TERMCRIT_ITER, 10, 1)
    (iters, (area, value, rect), track_box) = cv.CamShift(backproject, selection, crit)

   #and is_rect_nonzero(selection):
    #cv.EllipseBox(img, track_box, cv.CV_RGB(255,0,0), 3, cv.CV_AA, 0 )
# end draw ellipse

# find centroid coordinate (x,y) and area (z)
    selection_centroid = track_box[0]
    xposition = selection_centroid[0]
    yposition = selection_centroid[1]
    width_height = track_box[1]
    #print selection
    rect = (int(xposition - width_height[0] / float(2)), int(yposition - width_height[1] / float(2)), int(width_height[0]) , int(width_height[1]))
    #print rect
    # selection_area = width_height[0]*width_height[1]
    face_centroid_camshift = (xposition, yposition)
    if not is_rect_nonzero(rect):
        return None, None
    return face_centroid_camshift, rect
# end find centroid

# show hist
    # if backproject_mode:
        # cv.ShowImage( "CamShiftDemo", backproject)
        # cv.ShowImage( "Histogram", self.hue_histogram_as_image(hist))
# end show hist

    #return face_centroid_camshift


def roi_points(faces, image_scale):
    ((x, y, w, h), n) = faces

    pt1 = (int(x * image_scale), int(y * image_scale))
    pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))

    # centroid = (int((x+(w/2)) * image_scale), int((y+(h/2)) * image_scale))
    return pt1, pt2

def main():
    context = TestContext()
    context.setup_window()
    # img = cv.QueryFrame(capture)
    # self.image = self.update(img, faceCascade)
    glutMainLoop() #infinite loop until program quits

if __name__ == "__main__":
    main()
    # TestContext().main()


