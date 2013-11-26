import sys
import OpenGL
from OpenGL.GL import *
from OpenGL.GL.ARB import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import cv
import time
#for lighting
from OpenGL.arrays import vbo
from OpenGLContext.arrays import *
from OpenGL.GL import shaders

# from camshift import *

from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()

""" Rendering Context with custom viewpoint and render. Note: will have slightly different results as OpenGLContext automatically enables lighting.
"""
class TestContext(BaseContext):

    def __init__(self):
        print "GL is running!"
        self.centroid = (640, 360)

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
# eye at origin, reference point at -5z, direction of up vector at y (tilt)
        # print xposition
        # print yposition
        gluLookAt((self.centroid[0]-640)/100, (self.centroid[1]-360)/100, 0.0,
            0.0, 0.0, -1.0,
            0.0, 1.0, 0.0)
        # (centroid[0]-640)/100, (centroid[1]-360)/100


        gluPerspective(45.0, float(width)/float(height), 1.0, 500.0) #(angle, ratio, distance from viewer to near plane, distance from viewer to far plane. aka frustum perspective
        glMatrixMode(GL_MODELVIEW) #glMatrixMode sets the current matrix mode: modelview, projection, texture or color
        glDisable(GL_LIGHTING) # context automatically enables lighting to avoid a common class of new user errors where unlit geometry does not appear due to lack of light.
        #glEnable( GL_CULL_FACE ) #Prevents OpenGL from removing faces which face backward
        glEnable( GL_DEPTH_TEST )
        glDepthFunc( GL_LEQUAL )
    

    def render(self, mode=0):
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

    def update(self, img, faceCascade):
        # so that we display what's being rendered on the back buffer
        min_size = (20,20)
        image_scale = 2
        haar_scale = 1.1
        min_neighbors = 3
        haar_flags = 0
     
        # capture = cv.CaptureFromCAM(0)
        # faceCascade = cv.Load("haarcascade_frontalface_alt.xml")
        # img = cv.QueryFrame(capture)
        # image = update(img, faceCascade)


        # Allocate the temporary images
        grayscale = cv.CreateImage((image.width, image.height), 8, 1)
        smallImage = cv.CreateImage(
                (
                    cv.Round(image.width / image_scale),
                    cv.Round(image.height / image_scale)
                ), 8 ,1)
     
        # Convert color input image to grayscale
        cv.CvtColor(image, grayscale, cv.CV_BGR2GRAY)
     
        # Scale input image for faster processing
        cv.Resize(grayscale, smallImage, cv.CV_INTER_LINEAR)
     
        # Equalize the histogram
        cv.EqualizeHist(smallImage, smallImage)
     
        # Detect the faces
        faces = cv.HaarDetectObjects(
                smallImage, faceCascade, cv.CreateMemStorage(0),
                haar_scale, min_neighbors, haar_flags, min_size
            )
     
        # If faces are found
        if faces:
            for ((x, y, w, h), n) in faces:
                # the input to cv.HaarDetectObjects was resized, so scale the
                # bounding box of each face and convert it to two CvPoints
                pt1 = (int(x * image_scale), int(y * image_scale))
                pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))
                # cv.Rectangle(image, pt1, pt2, cv.RGB(255, 0, 0), 5, 8, 0)
                self.centroid = (int((x+(w/2)) * image_scale), int((y+(h/2)) * image_scale))
                # print centroid


        gluLookAt((self.centroid[0]-640)/100, (self.centroid[1]-360)/100, 0.0,
            0.0, 0.0, -1.0,
            0.0, 1.0, 0.0)

         
        # while (cv.WaitKey(15)==-1):
        # img = cv.QueryFrame(capture)
        # image = DetectFace(img, faceCascade)
        # cv.ShowImage("face detection test", image)

        glutPostRedisplay()

    def main(self):
        global window
        global image

        capture = cv.CaptureFromCAM(0)
        faceCascade = cv.Load("haarcascade_frontalface_alt.xml")
        img = cv.QueryFrame(capture)
        self.image = self.update(img, faceCascade)

        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)#double buffered - draw buffer in background altogether when done. Smoother output than single buffer, display as you draw
        glutInitWindowSize(1280,810)
        glutInitWindowPosition(0, 0)
        window = glutCreateWindow("Simple Window")
        glutIdleFunc(self.update)
        glutDisplayFunc(self.render)
        self.initGL(1280,810)
        glutMainLoop() #infinite loop until program quits


if __name__ == "__main__":
    TestContext().main()


