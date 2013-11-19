import math
import sys
import cv
import cv2

class TestCamera:
    
    def __init__(self):
        print "init"

    def closeCamera(self):
        if self.camera is not None:
            self.camera.release()
            self.camera = None

    def openCamera(self):
        self.camera = cv.CaptureFromCAM(0)
        print "Camera " + ( "exists" if self.camera is not None else "not exists" )
        return self.camera is not None

    def getImage(self):
        if self.camera is None:
            return None
        return cv.QueryFrame( self.camera )

if __name__=="__main__":
    test = TestCamera()
    if not test.openCamera():
        sys.exit(-1)
    cv.NamedWindow( "TestCamera", 1 )
    while True:
        image = test.getImage()
        if image is None:
            break
        cv.ShowImage( "TestCamera", image )
        pass

    cv.DestroyAllWindows()
    test.closeCamera()
