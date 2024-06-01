import cv2
import json
from ultralytics import YOLO

rectangles = []
start_point = None
end_point = None
drawing = False
lane = 1


def display_rectangle(event, x, y, flags, param):
    global start_point, end_point, drawing, rectangles, lane

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)
        x1, y1 = min(start_point[0], end_point[0]), min(start_point[1], end_point[1])
        x2, y2 = max(start_point[0], end_point[0]), max(start_point[1], end_point[1])
        rectangles.append([x1, y1, x2, y2, f'{lane}'])
        lane+=1

def select_rectangles(image):
    global rectangles, start_point, end_point

    rectangles = []
    clone = image.copy()
    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", display_rectangle)

    while True:
        img = clone.copy()
        if start_point and end_point:
            cv2.rectangle(img, start_point, end_point, (128, 0, 0), 2)
        cv2.imshow("Image", img)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

    cv2.destroyAllWindows()
    return rectangles

def draw_rectangles(image, rectangles):
    fontFace = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1.0
    color = (255, 0, 0)  
    thickness = 2
    lineType = cv2.LINE_8
    for rect in rectangles:
        x1, y1, x2, y2, text = rect
        cv2.putText(image,text , (x1, y1-10), fontFace, fontScale, color, thickness, lineType)
        cv2.rectangle(image, (x1, y1), (x2, y2), (128, 0, 0), 2)
    return image

def is_center_in_rectangle(rectangles, item):
  box = item['box']  
  box_center_x = (box['x1'] + box['x2']) / 2
  box_center_y = (box['y1'] + box['y2']) / 2


  for rectangle in rectangles:
    rectangle_start_x, rectangle_start_y, rectangle_end_x, rectangle_end_y, lane = rectangle
    if (rectangle_start_x <= box_center_x <= rectangle_end_x and
        rectangle_start_y <= box_center_y <= rectangle_end_y):
      return lane

  return 'none'

# Пример использования
# image = cv2.imread("videos/testphoto.jpg")
# rects = select_rectangles(image)
# print("Selected rectangles:", rects)
# image_with_rects = draw_rectangles(image, rects)
# model = YOLO('traffic_analysis.pt')
# results = model.track(image_with_rects, persist=True)
# for object in results:
#             json_object = json.loads(object.tojson())
#             for item in json_object:
#                 item['lane'] = is_center_in_rectangle(rectangles, item)
#                 print(item)
 
# cv2.imshow("Image with Rectangles", image_with_rects)
# cv2.waitKey(0)
# cv2.destroyAllWindows()