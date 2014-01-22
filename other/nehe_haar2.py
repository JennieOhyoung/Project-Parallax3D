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

from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()

FACE_CASCADE = cv.Load("haarcascade_frontalface_alt.xml")
        
""" Rendering Context with custom viewpoint and render. Note: will have slightly different results as OpenGLContext automatically enables lighting.
"""
class TestContext(BaseContext):
    xposition = 0.0
    yposition = 0.0
    zposition = 0.0
    last_face_centroid = (640, 360)

    def __init__(self):
        # print "GL is running!"
        self.capture = cv.CaptureFromCAM(0)
        
    def initGL(self, width, height):
        globAmb = [0.3, 0.3, 0.3, 1.0]
        lightAmb = [0.0, 0.0, 0.0, 1.0]
        lightDifAndSpec = [0.7, 0.7, 0.7, 1.0]
        # This part only runs once, the setup of my surrounding. 
        glClearColor(0.0, 0.0, 0.0, 1.0) #rgba (alpha is transparency)
        glClearDepth(1.0) #depth buffer- constraint where closer pixle has higher priority when drawn. 
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glShadeModel(GL_SMOOTH) 
        glViewport(0, 0, width, height) # setup viewport and perspective model. Specify the lower left corner of the viewport rectangle, in pixels with X and Y. width and height = glut window size.
        
        glMatrixMode(GL_PROJECTION) #Applies subsequent matrix operations to the projection matrix stack. Other stacks are modelview, texture, color
        glLoadIdentity() #clears up previous mat

        gluPerspective(45.0, float(width)/float(height), 1.0, 500.0) #(angle, ratio, distance from viewer to near plane, distance from viewer to far plane. aka frustum perspective
        
        glMatrixMode(GL_MODELVIEW) #glMatrixMode sets the current matrix mode: modelview, projection, texture or color
        
        # glLoadIdentity()
        glEnable(GL_LIGHTING)
        glLightfv(GL_LIGHT0, GL_AMBIENT, lightAmb)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightDifAndSpec)
        glLightfv(GL_LIGHT0, GL_SPECULAR, lightDifAndSpec)
        glEnable(GL_LIGHT0)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, globAmb)
        glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
        # glDisable(GL_LIGHTING) # context automatically enables lighting to avoid a common class of new user errors where unlit geometry does not appear due to lack of light.
        #glEnable( GL_CULL_FACE ) #Prevents OpenGL from removing faces which face backward
        glEnable( GL_DEPTH_TEST )
        glDepthFunc( GL_LEQUAL )
    

    def render(self, mode=0):
        # render_time = time.clock()
        # print "RENDERING"
        # This is the part that loops over and over
        """Render the geometry for the scene."""
        # BaseContext.render(self,mode) <-- makes screen blank again
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # glutSolidSphere(0.75,20,20);
        # BaseContext.render

        # setup the camera position
        glLoadIdentity();
        gluLookAt(self.xposition, self.yposition, 0.0,
            -self.xposition, -self.yposition, -10.0,
            0.0, 1.0, 0.0)

#lighting
        glPushMatrix()
        pos = [0, 20, 0, 1]
        direction = [0.0, -1.0, 0.0]
        spotAngle = 20
        glLightfv(GL_LIGHT0, GL_POSITION, pos)
        glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, spotAngle)
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, direction)
        glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 2)

        glPushMatrix();
        glDisable(GL_LIGHTING)
        glTranslate(pos[0], 0.5* pos[1], pos[2])
        glRotatef(-90.0, 1.0, 0.0, 0.0)
        glColor3f(1.0, 1.0, 1.0)
        PI = 3.141592
        glutWireCone(3.0 * np.tan( spotAngle/180.0 * PI ), pos[1], 10, 6)
        glEnable(GL_LIGHTING)
        glPopMatrix();



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

# draw pyramid6
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

        # print "render time is ", time.clock() - render_time

    # def Lights (self, mode = 0):
    #     """Setup the global (legacy) lights"""
    #     if self.lightsOn:
    #         glEnable( GL_LIGHTING )
    #         glEnable(GL_LIGHT1)
    #         glDisable(GL_LIGHT0)
    #     else:
    #         glDisable( GL_LIGHTING )
    #         glDisable(GL_LIGHT1)
    #         glDisable(GL_LIGHT0)

    def update(self):
        update_time = time.clock()
        # Get the image from the camera
        img = get_image_from_camera(self.capture)
        # print "Got image."
        # Detect face position
        face_centroid = detect_faces(img)
        # print "Found a face!", face_centroid
        
        if not face_centroid:
            print "no face detected"
            face_centroid = self.last_face_centroid
        
        # print face_centroid
        self.last_face_centroid = face_centroid
        # print self.centroid
        
        print "update time is ", time.clock() - update_time
        # centroid = get_centroid(faces, 2)
        # if not centroid:
        #     centroid = self.last_centroid
        # self.last_centroid = centroid

        # Update camera
        self.update_camera(face_centroid)
        # print "Uhhh... updated camera?"

        # Redraw
        
        # glutPostOverlayRedisplay()
        glutPostRedisplay()
        # print "Got redraw."

    #tic = True

    def update_camera(self, face_centroid):
        #camera_time = time.clock()
        # print "Updated camera."
        self.xposition = ((face_centroid[0]-640)/float(1280)) * 10.0
        self.yposition = ((face_centroid[1]-360)/float(720)) * 10.0
        print "x is: " + str(self.xposition)
        print "y is: " + str(self.yposition)

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

def detect_faces(img):
    image_scale = 3
    haar_scale = 1.1
    min_neighbors = 3
    haar_flags = 0
    min_size = (35,35)

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
    face_centroid = get_centroid(biggest_face, image_scale)

    return face_centroid
    

def get_centroid(faces, image_scale):
    ((x, y, w, h), n) = faces

    pt1 = (int(x * image_scale), int(y * image_scale))
    pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))

    centroid = (int((x+(w/2)) * image_scale), int((y+(h/2)) * image_scale))
    return centroid

def main():
    context = TestContext()
    context.setup_window()
    # img = cv.QueryFrame(capture)
    # self.image = self.update(img, faceCascade)
    glutMainLoop() #infinite loop until program quits

if __name__ == "__main__":
    main()
    # TestContext().main()


