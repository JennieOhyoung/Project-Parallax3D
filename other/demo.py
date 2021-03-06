import OpenGL
from OpenGL.GL import *
from OpenGL.GL.ARB import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

#from gl_wrap import *

import sys

class DemoApplication:
	""" simple application that set's up an OpenGL (GLUT) window with FBO
		and update / draw routines
	"""
	xPos = 0.0;
	swag = True;
	
	""" Constructor
	"""
	def __init__(self):
		print("Hi there!")

	""" Initialize OpenGL features we want for the application
		@param width the width of the window
		@param height the height of the window
	"""
	def initGL(self, width, height):
		print("initGL " + repr(width) + ", " + repr(height))
		glClearColor(0.0, 0.0, 1.0, 0.0) #rbga (alpha is transparency)
		glClearDepth(0.0) #depth buffer- constraint where closer pixle has higher priority when drawn. 
		glShadeModel(GL_SMOOTH) 

		# setup viewport and perspective model
		glViewport(0, 0, width, height)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity() #clears up previous mat
		gluPerspective(45.0, float(width)/float(height), 1.0, 500.0)
		glMatrixMode(GL_MODELVIEW)

	""" Main update routine for the application
	"""
	def updateScene(self):
		# TODO: update the scene objects
		if self.swag == True:
			self.xPos += 0.01
			if self.xPos > 5.0:
				self.swag = False
		else:
			self.xPos -= 0.01
			if self.xPos < -5.0:
				self.swag = True

		glutPostRedisplay()
		#critical to set separate update and draw cycle. 

	""" Main draw routine for the application
	"""
	def drawScene(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()
		
		print "help"
		print self.xPos

		glPushMatrix()
		glTranslatef(self.xPos, 0.0, -10.0);
		glColor4f(0.0, 1.0, 0.0, 1.0)
		glBegin(GL_QUADS) #for every 4 vertex 
		glTexCoord2f(0.0, 0.0)
		glVertex3f(-1.0, -1.0, 0.0)
		glTexCoord2f(0.0, 1.0)
		glVertex3f(-1.0, 1.0, 0.0)
		glTexCoord2f(1.0, 1.0)
		glVertex3f(1.0, 1.0, 0.0)
		glTexCoord2f(1.0, 0.0)
		glVertex3f(1.0, -1.0, 0.0)
		glEnd()
		glPopMatrix()

		glutSwapBuffers()

	""" Application class entry point
	"""
	def main(self):
		global window
		glutInit(sys.argv)
		glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH) #double buffered - draw buffer in background altogether when done. Smoother output than single buffer, display as you draw
		glutInitWindowSize(640, 480)
		glutInitWindowPosition(0, 0)
		window = glutCreateWindow("Simple GLUT Window")
		glutIdleFunc(self.updateScene) #update every chance it gets
		glutDisplayFunc(self.drawScene) #
		self.initGL(640, 480)
		glutMainLoop() #infinite loop until program quits

# If this is the main application file, run the demo application
if __name__ == "__main__":
	demo = DemoApplication()
	demo.main()

