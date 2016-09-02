import cv2
import numpy as np
import sys

img_path = sys.argv[1]
app_path = sys.argv[2]

def face_detect(path):
    img = cv2.imread(path)
    cascade = cv2.CascadeClassifier(str(app_path) + "/lib/tasks/haarcascade_frontalface_alt.xml")
    face_rect = cascade.detectMultiScale(img, 1.05, 1, cv2.cv.CV_HAAR_SCALE_IMAGE, (10,10))
    
    if len(face_rect) == 0:
        return [], img
    
    face_rect[:, 2:] += face_rect[:, :2]
    return face_rect, img

def box(face_rect, img):
    img_height, img_width = img.shape[:2]
    
    for x, y, w, h in [np.array(face_rect.tolist()[0])]:
      head_width   = w - x
      body_width   = int(round(head_width*2.33))
      left_padding = (img_width - body_width)/2
          
      body_rect = (left_padding, h, body_width, (img_height-y))
      
#    for x1, y1, x2, y2 in face_rect:
#      cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)
#      cv2.imwrite('detected.jpg', img);

    return body_rect

face_rect, img = face_detect(str(img_path))
body_rect = box(face_rect, img)

bgdModel = np.zeros((1,65), np.float64)
fgdModel = np.zeros((1,65), np.float64)

mask = np.zeros(img.shape[:2], np.uint8)

cv2.grabCut(img, mask, body_rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
mask2 = np.where((mask==2)|(mask==0), 0, 1).astype('uint8')
img = img*mask2[:,:,np.newaxis]

cv2.imwrite(str(img_path), img)



#-----------------------------------------------------------------------------------------



#from __future__ import print_function
#from imutils.object_detection import non_max_suppression
#from imutils import paths
#import numpy as np
#import argparse
#import imutils
#import cv2
#import sys
#
#img_path = sys.argv[1]
# 
## initialize the HOG descriptor/person detector
#hog = cv2.HOGDescriptor()
#hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
#
## loop over the image paths
## load the image and resize it to (1) reduce detection time
## and (2) improve detection accuracy
#image = cv2.imread(str(img_path))
#
## detect people in the image
#(rects, weights) = hog.detectMultiScale(image, winStride=(1, 1),
#	padding=(8, 8))
#
#
## apply non-maxima suppression to the bounding boxes using a
## fairly large overlap threshold to try to maintain overlapping
## boxes that are still people
#rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
#pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
# 
## draw the final bounding boxes
#for (xA, yA, xB, yB) in pick:
#	cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 4)
# 
## show the output images
#cv2.imwrite(str(img_path), image)
#
##------------------------------------------------------------------------------------------------------
#
##import sys
##import cv2
##import numpy as np
##
##img_path = sys.argv[1]
##
##img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
###height, width = img.shape[:2]
##
###img = cv2.resize(img, (640*width/height, 640)) 
##mask = np.zeros(img.shape[:2], np.uint8)
##
##bgdModel = np.zeros((1,65), np.float64)
##fgdModel = np.zeros((1,65), np.float64)
##
##rect = (10, 10, 70, 180)
##
##cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
##mask2 = np.where((mask==2)|(mask==0), 0, 1).astype('uint8')
##img = img*mask2[:,:,np.newaxis]
##
##cv2.imwrite(str(img_path), img)

