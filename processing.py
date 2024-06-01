import cv2
from ultralytics import YOLO
import json
from pymongo import MongoClient
from util.rectangles_road_lane import *  

client = MongoClient('localhost', 27017)
db = client['MadiTracker']
collection = db['data']

model = YOLO('traffic_analysis.pt')
video_name = 'traffic'
video_path = 'videos/'+video_name+'.mp4'
video_capture = cv2.VideoCapture(video_path)


frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

output_video_path = 'output/'+video_name+'output_video.mp4'
fourcc = cv2.VideoWriter_fourcc(*'XVID') 
out = cv2.VideoWriter(output_video_path, fourcc, 30.0, (frame_width, frame_height))
cap_number = 1

success, frame = video_capture.read()
if success:
    rectangles = select_rectangles(frame)
    
while video_capture.isOpened():
    success, frame = video_capture.read(frame)

    if success:
        results = model.track(frame, persist=True)
        for object in results:
            json_object = json.loads(object.tojson())
            for item in json_object:
                item['lane'] = is_center_in_rectangle(rectangles, item)
                item['cap_number'] = cap_number  
        if json_object and isinstance(json_object, list) and len(json_object) > 0:
            collection.insert_many(json_object)
        cap_number+=1
        annotated_frame = results[0].plot()
        annotated_frame = draw_rectangles(annotated_frame, rectangles)

        out.write(annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

video_capture.release()
out.release()
cv2.destroyAllWindows()