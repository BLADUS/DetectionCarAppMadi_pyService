from flask import Flask, request, jsonify
import cv2
from ultralytics import YOLO
import json
from pymongo import MongoClient
import numpy as np
from util.rectangles_road_lane import *
from util.util_methods import *

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client['MadiTracker']
collection = db['data']

model = YOLO('traffic_analysis.pt')

@app.route('/upload_video', methods=['POST'])
def upload_video():
    try:
        video_file = request.files['video']
        print("Получен файл видео:", video_file)  
    except Exception as e:
        print("Ошибка при получении файла видео:", e)
        return jsonify({"status": "error", "message": "Ошибка при получении файла видео"})
    video_path = f'videos/{video_file.filename}'
    video_file.save(video_path)
    video_capture = cv2.VideoCapture(video_path)

    frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    output_video_path = 'output/output_video.mp4'
    out = cv2.VideoWriter(output_video_path, fourcc, 30.0, (frame_width, frame_height))

    cap_number = 1
    success, frame = video_capture.read()
    if success:
        rectangles = select_rectangles(frame)

    while video_capture.isOpened():
        success, frame = video_capture.read(frame)
        if success:
            results = model.track(frame, persist=True)
            json_object = []
            for object in results:
                json_data = json.loads(object.tojson())
                for item in json_data:
                    item['lane'] = is_center_in_rectangle(rectangles, item)
                    item['cap_number'] = cap_number
                json_object.extend(json_data)

            if json_object:
                collection.insert_many(json_object)

            cap_number += 1
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

    return jsonify({"status": "success", "message": "Видео успешно обработано"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
