from flask import Flask, request, send_file, render_template, jsonify
import cv2
from ultralytics import YOLO
import os
from threading import Thread

app = Flask(__name__, static_folder='static')

# yolov8n 모델 로드
model = YOLO('/Users/skaigroove/WorkSpace/mosiac_module/models/best.pt')

# 전역 변수로 진행률을 저장합니다.
progress = 0

def process_video(file_path, output_path='static/uploads/output.mp4'):
    global progress
    cap = cv2.VideoCapture(file_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # XVID 코덱
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 코덱 설정
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
        progress_percent = (processed_frames / frame_count) * 100
        # 프로세싱 진행률 반올림
        progress = int(round(progress_percent, 0))

        print("progress: ", progress, "%, ", "frame_count: ", frame_count, ", processed_frames: ", processed_frames)

    cap.release()
    out.release()
    progress = 100  # 완료되면 100%로 설정
    print(f"Processing complete. Output saved to {output_path}")  # 출력 파일 경로 로그 출력
    print(f"File exists: {os.path.exists(output_path)}")  # 파일 존재 여부 확인
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

    # 비디오 처리 함수를 별도의 스레드에서 비동기로 실행
    thread = Thread(target=process_video, args=(file_path,))
    thread.start()

    return jsonify({'success': True}), 200  # 업로드 완료 후 즉시 200 상태 반환


@app.route('/progress', methods=['GET'])
def get_progress():
    global progress
    return jsonify({'progress': progress})


@app.route('/download', methods=['GET'])
def download_file():
    file_path = 'static/uploads/output.mp4'
    download = 'processed_video.mp4'
    if os.path.exists(file_path):
        print(f"Serving file from {file_path}")  # 파일 경로 로그 출력
        return send_file(file_path, as_attachment=True, mimetype='video/mp4', download_name=download)
    else:
        print(f"File not found: {file_path}")  # 파일이 없을 때 로그 출력
        return "File not found", 404


@app.route('/static/uploads/output.mp4', methods=['GET'])
def serve_video():
    file_path = 'static/uploads/output.mp4'
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='video/mp4')
    else:
        return "File not found", 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)
