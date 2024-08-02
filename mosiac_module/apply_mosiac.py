from flask import Flask, request, send_file, render_template, jsonify
import cv2
from ultralytics import YOLO
import os

app = Flask(__name__)

# yolov8n 모델 로드
model = YOLO('/Users/skaigroove/WorkSpace/mosiac_module/models/best.pt')

# 전역 변수로 진행률을 저장합니다.
progress = 0

def process_video(file_path, output_path='static/uploads/output.mp4'):
    global progress
    cap = cv2.VideoCapture(file_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 코덱 설정
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    processed_frames = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 얼굴 인식 및 모자이크 처리
        results = model(frame)

        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                frame[y1:y2, x1:x2] = cv2.blur(frame[y1:y2, x1:x2], (23, 23))

        out.write(frame)
        processed_frames += 1

        # 프로세싱 진행률 업데이트
        progress = (processed_frames / frame_count) * 100

    cap.release()
    out.release()
    progress = 100  # 완료되면 100%로 설정
    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    global progress
    progress = 0  # 프로세싱 시작 시 진행률 초기화
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    file_path = f"static/uploads/{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)

    output_path = process_video(file_path)
    return jsonify({'success': True})

@app.route('/progress', methods=['GET'])
def get_progress():
    global progress
    return jsonify({'progress': progress})

@app.route('/download', methods=['GET'])
def download_file():
    return send_file('static/uploads/output.mp4', as_attachment=True, mimetype='video/mp4', download_name='processed_video.mp4')

if __name__ == '__main__':
    app.run(debug=True, port=5000)