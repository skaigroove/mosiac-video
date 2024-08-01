from flask import Flask, request, send_file, render_template
import cv2
from ultralytics import YOLO
import os

app = Flask(__name__)

# yolov8n 모델 로드
model = YOLO('/Users/skaigroove/WorkSpace/mosiac_module/models/best.pt')

def process_video(file_path, output_path='static/uploads/output.mp4'):
    cap = cv2.VideoCapture(file_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 코덱 설정
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 얼굴 인식 및 모자이크 처리
        results = model(frame)

        # 결과 구조를 출력하여 확인
        print(results)

        # 결과가 list인 경우에 대한 처리
        if isinstance(results, list):
            for result in results:
                boxes = result.boxes  # 또는 적절한 속성으로 접근
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    frame[y1:y2, x1:x2] = cv2.blur(frame[y1:y2, x1:x2], (23, 23))
        else:
            for box in results.xyxy[0]:
                x1, y1, x2, y2 = map(int, box[:4])
                frame[y1:y2, x1:x2] = cv2.blur(frame[y1:y2, x1:x2], (23, 23))

        out.write(frame)

    cap.release()
    out.release()
    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    file_path = f"static/uploads/{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)

    output_path = process_video(file_path)
    return send_file(output_path, as_attachment=True, mimetype='video/mp4', download_name='processed_video.mp4')

if __name__ == '__main__':
    app.run(debug=True, port=5000)