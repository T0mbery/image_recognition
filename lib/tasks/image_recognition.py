import sys
import cv2
import numpy as np

img_name             = sys.argv[1]
origin_img_path      = sys.argv[2]
recognition_img_path = sys.argv[3]

img = cv2.imread(str(origin_img_path), cv2.IMREAD_COLOR)
height, width = img.shape[:2]

img = cv2.resize(img, (640*width/height, 640)) 
mask = np.zeros(img.shape[:2], np.uint8)

bgdModel = np.zeros((1,65), np.float64)
fgdModel = np.zeros((1,65), np.float64)

rect = (100, 30, width/2, 600)

cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
mask2 = np.where((mask==2)|(mask==0), 0, 1).astype('uint8')
img = img*mask2[:,:,np.newaxis]

cv2.imwrite(str(recognition_img_path), img)

