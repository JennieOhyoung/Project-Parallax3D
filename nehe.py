import sys
import OpenGL
from OpenGL.GL import *
from OpenGL.GL.ARB import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()

""" Rendering Context with custom viewpoint and render. Note: will have slightly different results as OpenGLContext automatically enables lighting.
"""
class TestContext(BaseContext):
    # set initial camera position
    initialPosition = (0,0,0) 

    def __init__(self):
        print "hello"

    def initGL(self, width, height):
        # print("initGL " + repr(width) + ", " + repr(height))
        glClearColor(0.0, 0.0, 1.0, 0.0) #rgba (alpha is transparency)
        glClearDepth(0.0) #depth buffer- constraint where closer pixle has higher priority when drawn. 
        glViewport(0, 0, width, height) # setup viewport and perspective model
        glMatrixMode(GL_PROJECTION) #Applies subsequent matrix operations to the projection matrix stack. Other stacks are modelview, texture, color.
        glLoadIdentity() #clears up previous mat
        gluPerspective(45.0, float(width)/float(height), 1.0, 500.0) #(angle, ratio, distance from viewer to near plane, distance from viewer to far plane. aka frustum perspective
        glMatrixMode(GL_MODELVIEW) #glMatrixMode sets the current matrix mode: modelview, projection, texture or color

    def render(self, mode=0):
        """Render the geometry for the scene."""

        BaseContext.render(self,mode)
        glDisable(GL_LIGHTING) # context automatically enables lighting to avoid a common class of new user errors where unlit geometry does not appear due to lack of light.
        glDisable( GL_CULL_FACE ) #Prevents OpenGL from removing faces which face backward

        glTranslatef(-1.5,0.0,-6.0) #Moves the drawing origin 6 units into the screen and 1.5 units to the left
        glBegin(GL_TRIANGLES) #Starts the (legacy) geometry generation mode
        glColor3f(1,0,0)
        glVertex3f( 0.0,  1.0, 0.0)
        glColor3f(0,1,0)
        glVertex3f(-1.0, -1.0, 0.0)
        glColor3f(0,0,1)
        glVertex3f( 1.0, -1.0, 0.0)
        glEnd()
        glTranslatef(3.0,0.0,0.0) #Moves the drawing origin again, cumulative change is now (1.5,0.0,6.0)

        glColor3f(0.5, 0.5, 1.0)
        glBegin(GL_QUADS)
        glVertex3f(-1.0,-1.0, 0.0)
        glVertex3f( 1.0,-1.0, 0.0)
        glVertex3f( 1.0, 1.0, 0.0)
        glVertex3f(-1.0, 1.0, 0.0)
        glEnd();

    def main(self):
        global window
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH) #double buffered - draw buffer in background altogether when done. Smoother output than single buffer, display as you draw
        glutInitWindowSize(640, 480)
        glutInitWindowPosition(0, 0)
        window = glutCreateWindow("Simple Window")
        # glutDisplayFunc(self.render) #
        self.initGL(640,480)
        glutMainLoop() #infinite loop until program quits


if __name__ == "__main__":
    TestContext.main()
    # nehe = TestContext()
    # nehe.main()










