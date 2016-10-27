import cv2
import numpy as np
import sys
import math
import httplib, urllib, base64

img_path = sys.argv[1]
app_path = sys.argv[2]
contour  = sys.argv[3]
img_url  = sys.argv[4]
root_url = sys.argv[5]

full_img_url = root_url + img_url

all_colors = ['black', 'white', 'grey', 'red', 'orange', 'yellow', 'green', 'aqua', 'blue', 'purple']

headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '{bd979bf9355040f7a8358922aa951ac6}',
}

params = urllib.urlencode({
    # Request parameters
    'visualFeatures': 'Categories',
    'details': '{string}',
    'language': 'en',
})

try:
    conn = httplib.HTTPSConnection('api.projectoxford.ai')
    conn.request("POST", "/vision/v1.0/analyze?%s" % params, "{body}", headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))

def face_detect(path):
    img = cv2.imread(path)
    cascade = cv2.CascadeClassifier(str(app_path) + "/lib/tasks/haarcascade_frontalface_alt.xml")
    # eye_cascade = cv2.CascadeClassifier(str(app_path) + "/lib/tasks/haarcascade_eye.xml")
    face_rect = cascade.detectMultiScale(img, 1.1, 1, cv2.cv.CV_HAAR_SCALE_IMAGE, (10,10))
    # eye_rect = cascade.detectMultiScale(img, 1.1, 1, cv2.cv.CV_HAAR_SCALE_IMAGE, (10,10))
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

        body_rect     = (left_padding, h, body_width, (img_height-h))

    return body_rect, head_width, head_height, img_height, img_width


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

    average_blue  = (sum(blue)  / len(blue))  if len(blue)  != 0 else 0
    average_green = (sum(green) / len(green)) if len(green) != 0 else 0
    average_red   = (sum(red)   / len(red))   if len(red)   != 0 else 0

    return [average_blue, average_green, average_red]


def colorizer(y_top, y_bot, width, img, bg_color):

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    BLACK           = []
    WHITE           = []
    GREY            = []
    RED             = []
    ORANGE          = []
    YELLOW          = []
    GREEN           = []
    AQUA            = []
    BLUE            = []
    PURPLE          = []
    constant_colors = [BLACK, WHITE, GREY, RED, ORANGE, YELLOW, GREEN, AQUA, BLUE, PURPLE]

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

    size = 0
    for color_const in constant_colors:
        size += len(color_const)
    size -= len(eval(bg_color.upper())) if bg_color else 0

    #                 BLACK     WHITE         GREY         RED       ORANGE      YELLOW     GREEN      AQUA       BLUE       PURPLE
    b_g_r_colors = [[0,0,0],[255,255,255],[100,100,100],[0,0,255],[0,200,255],[0,255,255],[0,255,0],[255,255,0],[255,0,0],[255,0,200]]

    colors = {}
    for color_list in zip(all_colors, constant_colors, b_g_r_colors):
        # color_list[0] - color name, string
        # color_list[1] - color const, (BLACK), list
        # color_list[2] - b-g-r color
        colors.update({
            color_list[0]: [
                             round((float(len(color_list[1]))/float(size))*100, 1) if float(size) != 0 else 0, \
                             len(color_list[1]), \
                             average_color(color_list[1], img), \
                             color_list[2], \
                             [sum(i) for i in zip(*color_list[1])][0] / len(color_list[1]) if len(color_list[1]) != 0 else []
                           ]
                      })

    if bg_color:
        del(colors[bg_color.lower()])

    sort_colors = sorted(colors.iteritems(), key=lambda (k,v): (v,k))[::-1]

    return sort_colors, colors



face_rect, img = face_detect(str(img_path))
body_rect, head_width, head_height, img_height, img_width = box(face_rect, img)

bgdModel = np.zeros((1,65), np.float64)
fgdModel = np.zeros((1,65), np.float64)

mask = np.zeros(img.shape[:2], np.uint8)

cv2.grabCut(img, mask, body_rect, bgdModel, fgdModel, 4, cv2.GC_INIT_WITH_RECT)
mask2 = np.where((mask==2)|(mask==0), 0, 1).astype('uint8')

img1 = img*mask2[:,:,np.newaxis]

for x, y, w, h in [list(body_rect)]:
    img1_sort_colors, _ = colorizer(y, img_height, img_width, img1, 0)
    bg_color = img1_sort_colors[-1][0]
    bgr_bg_color = img1_sort_colors[-1][1][3]

background = img - img1
background[np.where((background > [0,0,0]).all(axis = 2))] = bgr_bg_color

final = background + img1


if contour == 'contour':
    cv2.imwrite(str(img_path), final)
    sys.exit()


def is_similar_color(comparable_color_name, benchmark_color_name):
    if (( math.fabs((comparable_color_name[0] - benchmark_color_name[0])) <= 15) and \
        ( math.fabs((comparable_color_name[1] - benchmark_color_name[1])) <= 15) and \
        ( math.fabs((comparable_color_name[2] - benchmark_color_name[2])) <= 15)):
        return True
    else:
        return False


def is_skin_color(color_b_g_r):
    skin_color = [140, 160, 210]
    if ((math.fabs((color_b_g_r[0] - skin_color[0])) <= 25) and \
        (math.fabs((color_b_g_r[1] - skin_color[1])) <= 25) and \
        (math.fabs((color_b_g_r[2] - skin_color[2])) <= 25)):
        return True
    else:
        return False


def bordering_color(img, y):

    bordering_colors = []
    top_border       = y - 10
    bottom_border    = y + 10

    sort_top_range, top_range = colorizer(top_border, y, img_width, img, bg_color)
    sort_bottom_range, bottom_range = colorizer(y, bottom_border, img_width, img, bg_color)

    colors = [item for item in all_colors if item not in bg_color]
    for color in colors:
        if top_range[color][0] != 0 and bottom_range[color][0] != 0 and (is_similar_color(top_range[color][2], bottom_range[color][2])):
            bordering_colors.append(color)

    return bordering_colors


def colors_for_skipping(img, y, top_colors, bottom_colors, side):

    skipping_colors = []

    if not bottom_colors:
        return skipping_colors

    bordering_colors = bordering_color(img, y)

    for b_color in bordering_colors:
        if ((side == 'top') and ((bottom_colors[b_color][1] / top_colors[b_color][1]) >= 4)) or \
            ((side == 'bottom') and (top_colors[b_color][1] / bottom_colors[b_color][1] >= 4)):
            skipping_colors.append(b_color)

    return skipping_colors


def is_continue_condition(img, y, top_colors, bottom_colors, color_name, side):

    if side == 'top':
        colors = top_colors
    else:
        colors = bottom_colors

    if colors[color_name][0] < 5.0 or \
        (color_name == 'red' and is_similar_color(colors[color_name][2], colors['orange'][2])) or \
        (color_name == 'orange' and is_skin_color(colors['orange'][2])) or \
        (color_name in colors_for_skipping(img, y, top_colors, bottom_colors, side)):
        return True
    else:
        return False

for x, y, w, h in [list(body_rect)]:


    height_till_belt   = int(round(head_height*2.9))
    height_till_shoes  = int(round(head_height*5.7))
    y_coordinate_belt  = y + height_till_belt
    y_coordinate_shoes = y + height_till_shoes

    # y - is bottom coordinate from face box
    if (img_height - y) < height_till_belt:
        sort_top, top = colorizer(y, img_height, img_width, final, bg_color)
        sort_bottom, bottom = 0, False
        sort_shoes = 0
    else:
        if (img_height - y) < height_till_shoes:
            sort_top, top = colorizer(y, y_coordinate_belt, img_width, final, bg_color)
            sort_bottom, bottom = colorizer(y_coordinate_belt, img_height, img_width, final, bg_color)
            sort_shoes, shoes = 0, False
        else:
            sort_top, top = colorizer(y, y_coordinate_belt, img_width, final, bg_color)
            sort_bottom, bottom = colorizer(y_coordinate_belt, y_coordinate_shoes, img_width, final, bg_color)
            sort_shoes, shoes = colorizer(y_coordinate_shoes, img_height, img_width, final, bg_color)

    padding_top = 28

    remain_color_top    = []
    remain_color_bottom = []
    remain_color_shoes  = []

    for color_obj in sort_top:

        cv2.line(img, (1, y), (img_width, y), (114, 255, 0), 1)
        cv2.line(img, (x, y), (x, img_height), (114, 255, 0), 1)
        cv2.line(img, (x+w, y), (x+w, img_height), (114, 255, 0), 1)

        k = color_obj[0]
        if is_continue_condition(final, y_coordinate_belt, top, bottom, k, 'top'):
            continue
        else:
            cv2.circle(img, (img_width-22, y+padding_top), 10, (180, 250, 255), -1)
            cv2.circle(img, (img_width-22, y+padding_top), 8, top[k][2], -1)
            remain_color_top.append({k: [{'%': top[k][0]}, {'avr-bgr': top[k][2]}, {'avr-y': top[k][4]}]})
            padding_top += 26

    if sort_bottom:
        padding_top = 24
        for color_obj in sort_bottom:

            cv2.line(img, (1, y_coordinate_belt), (img_width, y_coordinate_belt), (114, 255, 0), 1)

            k = color_obj[0]
            if is_continue_condition(final, y_coordinate_shoes, bottom, shoes, k, 'top') or \
                is_continue_condition(final, y_coordinate_belt, top, bottom, k, 'bottom'):
                continue
            else:
                cv2.circle(img, (img_width-22, y_coordinate_belt + padding_top), 10, (180, 250, 255), -1)
                cv2.circle(img, (img_width-22, y_coordinate_belt + padding_top), 8, bottom[k][2], -1)
                remain_color_bottom.append({k: [{'%': bottom[k][0]}, {'avr-bgr': bottom[k][2]}, {'avr-y': bottom[k][4]}]})
                padding_top += 26

    if sort_shoes:
        padding_top = 28
        for color_obj in sort_shoes:

            cv2.line(img, (1, y_coordinate_shoes), (img_width, y_coordinate_shoes), (114, 255, 0), 1)

            k = color_obj[0]
            if is_continue_condition(final, y_coordinate_shoes, bottom, shoes, k, 'bottom'):
                continue
            else:
                cv2.circle(img, (img_width-22, y_coordinate_shoes + padding_top), 10, (180, 250, 255), -1)
                cv2.circle(img, (img_width-22, y_coordinate_shoes + padding_top), 8, shoes[k][2], -1)
                remain_color_shoes.append({k: [{'%': shoes[k][0]}, {'avr-bgr': shoes[k][2]}, {'avr-y': shoes[k][4]}]})
                padding_top += 26

    for x1, y1, x2, y2 in [np.array(face_rect.tolist()[0])]:
        cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 1)

    cv2.imwrite(str(img_path), img)

data_response = {
    'TOP': remain_color_top,
    'BOTTOM': remain_color_bottom,
    'SHOES': remain_color_shoes
}
print data_response

#    file = open('/Users/tom/work/recognition-images/test11.txt', 'w')
#    file.write(str(top))
#    file.close()
