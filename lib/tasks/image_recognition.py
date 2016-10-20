import cv2
import numpy as np
import sys

img_path = sys.argv[1]
app_path = sys.argv[2]
contour  = sys.argv[3]

def face_detect(path):
    img = cv2.imread(path)
    cascade = cv2.CascadeClassifier(str(app_path) + "/lib/tasks/haarcascade_frontalface_alt.xml")
    eye_cascade = cv2.CascadeClassifier(str(app_path) + "/lib/tasks/haarcascade_eye.xml")
    face_rect = cascade.detectMultiScale(img, 1.1, 1, cv2.cv.CV_HAAR_SCALE_IMAGE, (10,10))
    eye_rect = cascade.detectMultiScale(img, 1.1, 1, cv2.cv.CV_HAAR_SCALE_IMAGE, (10,10))
    if len(face_rect) < 1: print("face is not detected")

    if len(face_rect) == 0:
        return [], img

    face_rect[:, 2:] += face_rect[:, :2]
    return face_rect, img

def box(face_rect, img):
    img_height, img_width = img.shape[:2]

    # x, y - coordinate left top box coner
    # w, y - coordinate right top box coner
    # h, y - coordinate left bottom box coner
    for x, y, w, h in [np.array(face_rect.tolist()[0])]:
        head_height = h - y
        head_width    = w - x
        body_width    = int(round(head_width*2.33))
        x_face_center = x + head_width/2
        left_padding  = int(round(x_face_center - (head_height*1.2))) #int(round(body_width/1.6))
#        left_padding = (img_width - body_width)/2

#        print(head_width, body_width, left_padding)

        body_rect = (left_padding, h, body_width, (img_height-h))

    return body_rect, head_width, head_height, img_height, img_width


face_rect, img = face_detect(str(img_path))
body_rect, head_width, head_height, img_height, img_width = box(face_rect, img)

bgdModel = np.zeros((1,65), np.float64)
fgdModel = np.zeros((1,65), np.float64)

mask = np.zeros(img.shape[:2], np.uint8)

cv2.grabCut(img, mask, body_rect, bgdModel, fgdModel, 4, cv2.GC_INIT_WITH_RECT)
mask2 = np.where((mask==2)|(mask==0), 0, 1).astype('uint8')

img1 = img*mask2[:,:,np.newaxis]

background = img - img1
background[np.where((background > [0,0,0]).all(axis = 2))] = [0,255,0]


final = background + img1

all_colors = ['black', 'white', 'grey', 'red', 'orange', 'yellow', 'aqua', 'blue', 'purple']

if contour == 'contour':
    cv2.imwrite(str(img_path), final)
    sys.exit()

def average_color(coordinates, img):
    color_array = []
    for y, x in coordinates:
        color_array.append(img[y,x])

    blue  = []
    green = []
    red   = []

    for b, g, r in color_array:
        blue.append(b)
        green.append(g)
        red.append(r)

    average_blue  = (sum(blue)  / len(blue))  if len(blue) != 0 else 0
    average_green = (sum(green) / len(green)) if len(green) != 0 else 0
    average_red   = (sum(red)   / len(red))   if len(red) != 0 else 0

    return [average_blue, average_green, average_red]

def colorizer(y_top, y_bot, width, img):

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    BLACK  = []
    WHITE  = []
    GREY   = []
    RED    = []
    ORANGE = []
    YELLOW = []
    GREEN  = []
    AQUA   = []
    BLUE   = []
    PURPLE = []

    for y in range(y_top, y_bot):
        for x in range(width):
            H = hsv[y, x][0]
            S = hsv[y, x][1]
            V = hsv[y, x][2]

            if (V < 75):
                BLACK.append([y,x])
            elif (V > 190 and S < 27):
                WHITE.append([y,x])
            elif (S < 53 and V < 185):
                GREY.append([y,x])
            else:
                if (H < 7):
                    RED.append([y,x])
                elif (H < 25):
                    ORANGE.append([y,x])
                elif (H < 34):
                    YELLOW.append([y,x])
                elif (H < 73):
                    GREEN.append([y,x])
                elif (H < 102):
                    AQUA.append([y,x])
                elif (H < 140):
                    BLUE.append([y,x])
                elif (H < 170):
                    PURPLE.append([y,x])
                else:                          # full circle
                    RED.append([y,x])          # back to Red


    average_black  = average_color(BLACK,  img)
    average_white  = average_color(WHITE,  img)
    average_grey   = average_color(GREY,   img)
    average_red    = average_color(RED,    img)
    average_orange = average_color(ORANGE, img)
    average_yellow = average_color(YELLOW, img)
    average_green  = average_color(GREEN,  img)
    average_aqua   = average_color(AQUA,   img)
    average_blue   = average_color(BLUE,   img)
    average_purple = average_color(PURPLE, img)


    size = len(BLACK)+len(WHITE)+len(GREY)+len(RED)+len(ORANGE)+len(YELLOW)+len(AQUA)+len(BLUE)+len(PURPLE) #+len(GREEN)

    colors = {
        'black':  [round((float(len(BLACK))/float(size))*100, 1),  len(BLACK),  average_black],
        'white':  [round((float(len(WHITE))/float(size))*100, 1),  len(WHITE),  average_white],
        'grey':   [round((float(len(GREY))/float(size))*100, 1),   len(GREY),   average_grey],
        'red':    [round((float(len(RED))/float(size))*100, 1),    len(RED),    average_red],
        'orange': [round((float(len(ORANGE))/float(size))*100, 1), len(ORANGE), average_orange],
        'yellow': [round((float(len(YELLOW))/float(size))*100, 1), len(YELLOW), average_yellow],
       # 'green':  [round((float(len(GREEN))/float(size))*100, 1),  len(GREEN),  average_green],
        'aqua':   [round((float(len(AQUA))/float(size))*100, 1),   len(AQUA),   average_aqua],
        'blue':   [round((float(len(BLUE))/float(size))*100, 1),   len(BLUE),   average_blue],
        'purple': [round((float(len(PURPLE))/float(size))*100, 1), len(PURPLE), average_purple]
    }

    sort_colors = sorted(colors.iteritems(), key=lambda (k,v): (v,k))[::-1]

    return sort_colors, colors

def is_similar_color(comparable_color_name, benchmark_color_name):
    if ((-15 <= (comparable_color_name[0] - benchmark_color_name[0]) <= 15) and (-15 <= (comparable_color_name[1] - benchmark_color_name[1]) <= 15) and (-15 <= (comparable_color_name[2] - benchmark_color_name[2]) <= 15)):
        return True
    else:
        return False
def is_skin_color(color_b_g_r):
    skin_color = [140, 160, 210]
    if ((-25 <= color_b_g_r[0] - skin_color[0] <= 25) and (-25 <= color_b_g_r[1] - skin_color[1] <= 25) and (-25 <= color_b_g_r[2] - skin_color[2] <= 25)):
        return True
    else:
        return False

def bordering_color(img, y):

    bordering_colors = []
    top_border       = y - 10
    bottom_border    = y + 10

    sort_top_range, top_range = colorizer(top_border, y, img_width, img)
    sort_bottom_range, bottom_range = colorizer(y, bottom_border, img_width, img)

    for color in all_colors:
        if is_similar_color(top_range[color][2], bottom_range[color][2]):
            bordering_colors.append(color)

    return bordering_colors

def is_continue_condition(colors, color_name):
    if colors[color_name][0] < 5.0 or \
        (color_name == 'red' and is_similar_color(colors[color_name][2], colors['orange'][2])) or \
        (color_name == 'orange' and is_skin_color(colors['orange'][2])) or \
        ():
        return True
    else:
        return False

for x, y, w, h in [list(body_rect)]:


    height_till_belt   = int(round(head_height*2.9))
    height_till_shoes  = int(round(head_height*6.8))

    y_coordinate_belt  = y + height_till_belt
    y_coordinate_shoes = y + height_till_shoes

    # y - is bottom coordinate from face box
    if (img_height - y) < height_till_belt:
        sort_top, top = colorizer(y, img_height, img_width, final)
        sort_bottom = 0
        sort_shoes = 0
    else:
        if (img_height - y) < height_till_shoes:
            sort_top, top = colorizer(y, y_coordinate_belt, img_width, final)
            sort_bottom, bottom = colorizer(y_coordinate_belt, img_height, img_width, final)
            sort_shoes = 0
        else:
            sort_top, top = colorizer(y, y_coordinate_belt, img_width, final)
            sort_bottom, bottom = colorizer(y_coordinate_belt, y_coordinate_shoes, img_width, final)
            sort_shoes, shoes = colorizer(y_coordinate_shoes, img_height, img_width, final)

    padding_top = 28

    for color_obj in sort_top:

        cv2.line(img, (1, y), (img_width, y), (114, 255, 0), 1)
        cv2.line(img, (x, y), (x, img_height), (114, 255, 0), 1)
        cv2.line(img, (x+w, y), (x+w, img_height), (114, 255, 0), 1)

        k = color_obj[0]
        if is_continue_condition(top, k):
            continue
        else:
            cv2.circle(img, (img_width-22, y+padding_top), 10, (180, 250, 255), -1)
            cv2.circle(img, (img_width-22, y+padding_top), 8, top[k][2], -1)
            padding_top += 26

    if sort_bottom:
        padding_top = 24
        for color_obj in sort_bottom:

            cv2.line(img, (1, y_coordinate_belt), (img_width, y_coordinate_belt), (114, 255, 0), 1)

            k = color_obj[0]
            if is_continue_condition(bottom, k):
                continue
            else:
                cv2.circle(img, (img_width-22, y_coordinate_belt + padding_top), 10, (180, 250, 255), -1)
                cv2.circle(img, (img_width-22, y_coordinate_belt + padding_top), 8, bottom[k][2], -1)
                padding_top += 26

    if sort_shoes:
        padding_top = 28
        for color_obj in sort_shoes:

            cv2.line(img, (1, y_coordinate_shoes), (img_width, y_coordinate_shoes), (114, 255, 0), 1)

            k = color_obj[0]
            if is_continue_condition(shoes, k):
                continue
            else:
                cv2.circle(img, (img_width-22, y_coordinate_shoes + padding_top), 10, (180, 250, 255), -1)
                cv2.circle(img, (img_width-22, y_coordinate_shoes + padding_top), 8, shoes[k][2], -1)
                padding_top += 26

    for x1, y1, x2, y2 in [np.array(face_rect.tolist()[0])]:
        cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 1)

    cv2.imwrite(str(img_path), img)

#    file = open('/Users/tom/work/recognition-images/test11.txt', 'w')
#    file.write(str(top))
#    file.close()
