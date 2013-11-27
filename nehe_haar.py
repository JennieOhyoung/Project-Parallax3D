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

FACE_CASCADE = cv.Load("haarcascade_frontalface_alt.xml")
        
""" Rendering Context with custom viewpoint and render. Note: will have slightly different results as OpenGLContext automatically enables lighting.
"""
class TestContext(BaseContext):

    def __init__(self):
        print "GL is running!"
        self.last_face_centroid = (0, 0)
        self.capture = cv.CaptureFromCAM(0)
        
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
        # gluLookAt((self.centroid[0]-640)/100, (self.centroid[1]-360)/100, 0.0,
            # 0.0, 0.0, -1.0,
            # 0.0, 1.0, 0.0)
        # (centroid[0]-640)/100, (centroid[1]-360)/100


        gluPerspective(45.0, float(width)/float(height), 1.0, 500.0) #(angle, ratio, distance from viewer to near plane, distance from viewer to far plane. aka frustum perspective
        glMatrixMode(GL_MODELVIEW) #glMatrixMode sets the current matrix mode: modelview, projection, texture or color
        glDisable(GL_LIGHTING) # context automatically enables lighting to avoid a common class of new user errors where unlit geometry does not appear due to lack of light.
        #glEnable( GL_CULL_FACE ) #Prevents OpenGL from removing faces which face backward
        glEnable( GL_DEPTH_TEST )
        glDepthFunc( GL_LEQUAL )
    

    def render(self, mode=0):
        print "RENDERING"
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
        # Get the image from the camera
        img = get_image_from_camera(self.capture)
        print "Got an image!"
        # Detect face position
        face_centroid = detect_faces(img)
        # print "Found a face!", face_centroid
        
        if not face_centroid:
            face_centroid = self.last_face_centroid
        
        self.last_face_centroid = face_centroid


        # Update camera
        self.update_camera(face_centroid)
        print "Uhhh... updated camera?"

        # Redraw
        glutPostRedisplay()
        print "It redrew.. maybe?"


    def update_camera(self, centroid):
        gluLookAt((centroid[0]-640)/100, (centroid[1]-360)/100, 0.0,
            0.0, 0.0, -1.0,
            0.0, 1.0, 0.0)

    def get_camera_image(self):
        return cv.QueryFrame(self.capture);

    def setup_window(self):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)#double buffered - draw buffer in background altogether when done. Smoother output than single buffer, display as you draw
        glutInitWindowSize(1280,810)
        glutInitWindowPosition(0, 0)
        window = glutCreateWindow("Simple Window")
        glutIdleFunc(self.update)
        glutDisplayFunc(self.render)
        self.initGL(1280,810)


def main():
    context = TestContext()
    context.setup_window()
    # img = cv.QueryFrame(capture)
    # self.image = self.update(img, faceCascade)
    glutMainLoop() #infinite loop until program quits


def get_image_from_camera(capture):
    img = cv.QueryFrame(capture)
    return img

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
    faces = cv.HaarDetectObjects(
            smallImage, FACE_CASCADE, cv.CreateMemStorage(0),
            haar_scale, min_neighbors, haar_flags, min_size
        )

    if not faces:
        return None

    def compare_area(f1, f2):
        area1 = f1[0][2] * f1[0][3]
        area2 = f2[0][2] * f2[0][3]
        return area1 - area2

    sorted_faces = sorted(faces, cmp=compare_area)
    biggest_face = sorted_faces[-1]
    face_centroid = get_centroid(biggest_face, image_scale)

    return face_centroid
    

def get_centroid(face, image_scale):
    ((x, y, w, h), n) = face

    pt1 = (int(x * image_scale), int(y * image_scale))
    pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))

    centroid = (int((x+(w/2)) * image_scale), int((y+(h/2)) * image_scale))
    return centroid


if __name__ == "__main__":
    main()
    # TestContext().main()


