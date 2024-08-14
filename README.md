# Video File Mosiac Processing Web Application

## 개발 환경

- Flask
    - ver. 3.0.3
    

- Python
    - ver. 3.9

- Open-cv
    - ver. 3.9

- Ultraltics
    - ver. 8.2.70

- Torch
    - ver. 3.9

---

## Github

[GitHub - skaigroove/mosiac-video: Mosiac Video Web Service](https://github.com/skaigroove/mosiac-video)

---

## MockUp

![image.png](Video%20File%20Mosiac%20Processing%20Web%20Application%205f47d05a079846a8bb832718b2f5e809/image.png)

[MOSAIC CAT](https://www.figma.com/design/ZdM0QBoz7ZZPUrlghcbCmK/MOSAIC-CAT?node-id=0-1&t=mTSUuwZKPXusMsuQ-0)

---

## 기능

- `Upload Video` 를 누르면 모자이크 할 동영상 파일을 서버에 보낼 수 있음
- Upload하면 `Sample Video` 가  `View` 에 표시되고(회색) `모자이크 Processing` 에 들어감.
- Processing이 끝나면 `Download 버튼` 이 뜨고, `Output Video` 가 `View`에 표시되며(민트색) `파일을 미리 확인` 하고 `Download` 여부를 결정 할  수 있음

---

## 실행 환경 설정

### 1. Python Interpreter 설정

1. Configure Python Interpreter
    
    ![image.png](Video%20File%20Mosiac%20Processing%20Web%20Application%205f47d05a079846a8bb832718b2f5e809/image%201.png)
    
2. Conda Environment 생성
    
    ![image.png](Video%20File%20Mosiac%20Processing%20Web%20Application%205f47d05a079846a8bb832718b2f5e809/image%202.png)
    
- Python version =3.9
- Conda가 설치되어있지 않다면 anaconda부터 설치 → 안 되어있으면 Conda Excutable Path가 뜨지 않는 경우 발생

[Download Success | Anaconda](https://www.anaconda.com/download-success)

c.  (mosiac-video) 환경에서 실행되고 있는지 확인

![image.png](Video%20File%20Mosiac%20Processing%20Web%20Application%205f47d05a079846a8bb832718b2f5e809/image%203.png)

### 2. root directory에서 requirements.txt 실행하여 필요 모듈 설치

![image.png](Video%20File%20Mosiac%20Processing%20Web%20Application%205f47d05a079846a8bb832718b2f5e809/image%204.png)

```bash
pip install -r requirements.txt
```

![image.png](Video%20File%20Mosiac%20Processing%20Web%20Application%205f47d05a079846a8bb832718b2f5e809/image%205.png)

설치완료

### 3. apply_mosiac.py 파일 실행

![image.png](Video%20File%20Mosiac%20Processing%20Web%20Application%205f47d05a079846a8bb832718b2f5e809/image%206.png)

![image.png](Video%20File%20Mosiac%20Processing%20Web%20Application%205f47d05a079846a8bb832718b2f5e809/image%207.png)

---

## 디렉터리 구조

![Untitled](Video%20File%20Mosiac%20Processing%20Web%20Application%205f47d05a079846a8bb832718b2f5e809/Untitled.png)

## 코드

- `apply_mosiac.py`
    
    ```python
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
        fourcc = cv2.VideoWriter_fourcc(*'x264')  # 코덱 설정
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
    ```
    
- `index.html`
    
    ```html
    <!DOCTYPE html>
    <html lang="en">
    
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mosaic Cat</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    </head>
    
    <body>
    
    <div class="header">
        <p>MOSAIC CAT</p>
    </div>
    
    <div class="uploadContainer">
        <div class="text">
            <p>Simple convert</p>
            <p>to face mosaic.</p>
            <p>Upload your Video!</p>
        </div>
        <div class="uploadSection">
            <img id="lyingCat" src="{{ url_for('static', filename='images/lying_cat.png') }}" alt="cat">
            <div class="uploadButton">
                <p>Upload Video</p>
            </div>
            <input type="file" id="fileInput" name="file" accept="video/*" style="display: none;">
            <div class="uploadCaution">
                <p>Be careful with file sizes</p>
                <p>You can only upload files</p>
                <p>that are 100 MB or less</p>
            </div>
        </div>
    </div>
    <div class="videoContainer">
        <div class="sampleContainer">
            <div class="sample-video-wrapper">
                <video id="videoPreviewer" autoplay controls></video>
            </div>
            <div class="downloadSection" id="downloadSection" style="display: none;">
                <div class="processing">
                    <img class="processingCat" id="processingCat" src="{{ url_for('static', filename='images/surprised_cat.png') }}" alt="processingcat">
                    <p id="processingText">processing 0%</p>
                </div>
                <button id="downloadButton" class="downloadButton" style="display: none;">Download</button>
            </div>
        </div>
        <div class="outputContainer">
            <div class="output-video-wrapper">
                <video id="outputVideo" autoplay controls>
                    <source src="../static/uploads/output.mp4" type="video/mp4">
                </video>
            </div>
        </div>
    </div>
    
    <script src="{{ url_for('static', filename='script.js') }}"></script>
    </body>
    </html>
    
    ```
    
- `style.css`
    
    ```css
    body {
        font-family: Arial, sans-serif;
        background-color: #f0f0f0;
        color: #333;
        margin: auto;
        display: flex;
        flex-direction: column;
    }
    
    .header {
        margin: 0px 40px;
    }
    
    .header p {
        font-size: 2em;
    }
    
    .uploadContainer {
        display: flex;
        justify-content: space-between;
        margin: 20px 40px;
    }
    
    .uploadContainer .text {
        text-align: left;
        font-size: 4em;
        margin-bottom: 10px;
        display: inline-block;
    }
    
    .uploadContainer p {
        font-size: 1em;
        margin: 5px 0;
    }
    
    .uploadSection {
        flex-direction: column;
        display: inline-block;
        margin-top: 3em;
    }
    
    .uploadButton {
        background-color: #000;
        color: #fff;
        padding: 2em 3em;
        text-transform: uppercase;
        cursor: pointer;
    }
    
    .uploadSection img {
        position: absolute;
        width: 8em;
        height: 8em;
        left: 64.13em;
        top: 7.5em;
    }
    
    .uploadButton p {
        justify-content: center;
        font-size: 1.5em;
        text-align: center;
    }
    
    .uploadCaution {
        font-size: 1.2em;
        text-align: center;
    }
    
    .videoContainer {
        display: flex;
        justify-content: space-between;
        width: 100%;
    }
    
    .sampleContainer {
        margin: 1em 2em;
        padding: 20px;
    }
    
    .outputContainer {
        margin: 1em 2em;
        padding: 20px;
    }
    
    .sample-video-wrapper {
        flex: 1;
        display: inline-block;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        text-align: center;
    }
    
    .output-video-wrapper {
        flex: 1;
        display: inline-block;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        text-align: center;
    }
    
    .sample-video-wrapper video {
        max-width: 100%;
        height: 15em;
        display: flex;
        padding-bottom: 1.5em;
    }
    
    .output-video-wrapper video {
        max-width: 100%;
        height: 18em;
        display: flex;
    }
    
    .video-wrapper p {
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        color: #666;
        font-size: 1em;
    }
    
    .downloadSection {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        justify-content: center;
    }
    
    .processing {
        display: flex;
        align-items: center;
        margin-right: 20px;
    }
    
    .processing img {
        width: 3em;
        height: auto;
        margin-right: 2em;
    }
    
    .processing p {
        margin: 0;
        font-size: 1em;
    }
    
    .downloadButton {
        background-color: #000;
        color: #fff;
        border: none;
        font-size: 1em;
        cursor: pointer;
        text-transform: uppercase;
        padding: 1em 2em;
    }
    
    /* Rotation animation */
    .rotating {
        animation: rotate 2s linear infinite;
    }
    
    @keyframes rotate {
        from {
            transform: rotate(0deg);
        }
        to {
            transform: rotate(360deg);
        }
    }
    
    .fade-out {
        animation: fadeOut 1s forwards;
    }
    
    @keyframes fadeOut {
        from {
            opacity: 1;
        }
        to {
            opacity: 0;
        }
    }
    
    .fade-in {
        animation: fadeIn 1s forwards;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    ```
    
- `scripts.js`
    
    ```jsx
    document.addEventListener('DOMContentLoaded', function () {
        const uploadButton = document.querySelector('.uploadButton');
        const fileInput = document.getElementById('fileInput');
        const videoPreview = document.getElementById('videoPreviewer');
        const downloadSection = document.getElementById('downloadSection');
        const downloadButton = document.getElementById('downloadButton');
        const processingText = document.getElementById('processingText');
        const processingCat = document.getElementById('processingCat');
        const outputVideo = document.getElementById('outputVideo');
    
        uploadButton.addEventListener('click', function () {
            fileInput.click();
        });
    
        fileInput.addEventListener('change', function (event) {
            const file = event.target.files[0];
            if (file) {
                videoPreview.src = URL.createObjectURL(file);
                videoPreview.style.display = 'block';
                downloadSection.style.display = 'flex';
                startUpload(file);
            }
        });
    
        function startUpload(file) {
            const formData = new FormData();
            formData.append('file', file);
    
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/process', true);
    
            xhr.upload.addEventListener('progress', function (event) {
                if (event.lengthComputable) {
                    const percentComplete = (event.loaded / event.total) * 100;
                    console.log(`Uploading ${percentComplete.toFixed(0)}%`);
                    processingText.textContent = `Uploading ${percentComplete.toFixed(0)}%`;
                }
            });
    
            xhr.onreadystatechange = function () {
                console.log(`ReadyState: ${xhr.readyState}, Status: ${xhr.status}`);
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        console.log('Upload complete. Starting processing...');
                        processingText.textContent = 'Processing 0%';
                        processingCat.classList.add('rotating');
                        checkProgress();
                    } else {
                        console.error(`Upload failed with status ${xhr.status}: ${xhr.statusText}`);
                    }
                }
            };
    
            xhr.onerror = function() {
                console.error('Upload request failed.');
            };
    
            xhr.send(formData);
        }
    
        function checkProgress() {
            const interval = setInterval(function () {
                const xhr = new XMLHttpRequest();
                xhr.open('GET', '/progress', true);
    
                xhr.onreadystatechange = function () {
                    if (xhr.readyState === XMLHttpRequest.DONE) {
                        if (xhr.status === 200) {
                            const response = JSON.parse(xhr.responseText);
                            const progress = response.progress;
                            console.log(`Processing ${progress.toFixed(0)}%`);
                            processingText.textContent = `Processing ${progress.toFixed(0)}%`;
    
                            if (progress >= 100) {
                                clearInterval(interval);
                                processingText.textContent = 'Processing 100%';
                                processingCat.classList.remove('rotating');
                                processingText.classList.add('fade-out');
                                setTimeout(() => {
                                    processingText.style.display = 'none';
                                    downloadButton.classList.add('fade-in');
                                    downloadButton.style.display = 'block';
                                }, 1000);
    
                                downloadButton.addEventListener('click', function () {
                                    window.location.href = '/download'; // 파일 다운로드
                                });
    
                                displayProcessedVideo();
                            }
                        } else {
                            console.error(`Progress check failed with status ${xhr.status}: ${xhr.statusText}`);
                        }
                    }
                };
    
                xhr.onerror = function() {
                    console.error('Progress request failed.');
                };
    
                xhr.send();
            }, 1000);
        }
    
        function displayProcessedVideo() {
            const videoUrl = 'uploads/output.mp4'; // 서버의 비디오 파일 절대 경로
            console.log(`Setting video source to: ${videoUrl}`); // 로그 추가
            outputVideo.src = videoUrl;
            outputVideo.addEventListener('error', function(e) {
                console.error('Error loading video:', e);
            });
            outputVideo.addEventListener('canplay', function() {
                console.log('Video can play');
            });
            outputVideo.load(); // 비디오 로드 시도
            outputVideo.style.display = 'block';
            console.log('Video should now be visible'); // 로그 추가
        }
    });
    document.addEventListener('DOMContentLoaded', function () {
        const uploadButton = document.querySelector('.uploadButton');
        const fileInput = document.getElementById('fileInput');
        const videoPreview = document.getElementById('videoPreviewer');
        const downloadSection = document.getElementById('downloadSection');
        const downloadButton = document.getElementById('downloadButton');
        const processingText = document.getElementById('processingText');
        const processingCat = document.getElementById('processingCat');
        const outputVideo = document.getElementById('outputVideo');
    
        uploadButton.addEventListener('click', function () {
            fileInput.click();
        });
    
        fileInput.addEventListener('change', function (event) {
            const file = event.target.files[0];
            if (file) {
                videoPreview.src = URL.createObjectURL(file);
                videoPreview.style.display = 'block';
                downloadSection.style.display = 'flex';
                startUpload(file);
            }
        });
    
        function startUpload(file) {
            const formData = new FormData();
            formData.append('file', file);
    
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/process', true);
    
            xhr.upload.addEventListener('progress', function (event) {
                if (event.lengthComputable) {
                    const percentComplete = (event.loaded / event.total) * 100;
                    console.log(`Uploading ${percentComplete.toFixed(0)}%`);
                    processingText.textContent = `Uploading ${percentComplete.toFixed(0)}%`;
                }
            });
    
            xhr.onreadystatechange = function () {
                console.log(`ReadyState: ${xhr.readyState}, Status: ${xhr.status}`);
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        console.log('Upload complete. Starting processing...');
                        processingText.textContent = 'Processing 0%';
                        processingCat.classList.add('rotating');
                        checkProgress();
                    } else {
                        console.error(`Upload failed with status ${xhr.status}: ${xhr.statusText}`);
                    }
                }
            };
    
            xhr.onerror = function() {
                console.error('Upload request failed.');
            };
    
            xhr.send(formData);
        }
    
        function checkProgress() {
            const interval = setInterval(function () {
                const xhr = new XMLHttpRequest();
                xhr.open('GET', '/progress', true);
    
                xhr.onreadystatechange = function () {
                    if (xhr.readyState === XMLHttpRequest.DONE) {
                        if (xhr.status === 200) {
                            const response = JSON.parse(xhr.responseText);
                            const progress = response.progress;
                            console.log(`Processing ${progress.toFixed(0)}%`);
                            processingText.textContent = `Processing ${progress.toFixed(0)}%`;
    
                            if (progress >= 100) {
                                clearInterval(interval);
                                processingText.textContent = 'Processing 100%';
                                processingCat.classList.remove('rotating');
                                processingText.classList.add('fade-out');
                                setTimeout(() => {
                                    processingText.style.display = 'none';
                                    downloadButton.classList.add('fade-in');
                                    downloadButton.style.display = 'block';
                                }, 1000);
    
                                downloadButton.addEventListener('click', function () {
                                    window.location.href = '/download'; // 파일 다운로드
                                });
    
                                displayProcessedVideo();
                            }
                        } else {
                            console.error(`Progress check failed with status ${xhr.status}: ${xhr.statusText}`);
                        }
                    }
                };
    
                xhr.onerror = function() {
                    console.error('Progress request failed.');
                };
    
                xhr.send();
            }, 1000);
        }
    
        function displayProcessedVideo() {
            const videoUrl = 'uploads/output.mp4'; // 서버의 비디오 파일 절대 경로
            console.log(`Setting video source to: ${videoUrl}`); // 로그 추가
            outputVideo.src = videoUrl;
            outputVideo.addEventListener('error', function(e) {
                console.error('Error loading video:', e);
            });
            outputVideo.addEventListener('canplay', function() {
                console.log('Video can play');
            });
            outputVideo.load(); // 비디오 로드 시도
            outputVideo.style.display = 'block';
            console.log('Video should now be visible'); // 로그 추가
        }
    });
    ```
    
- `requirements.txt`
    
    ```jsx
    flask~=3.0.3
    opencv-python-headless
    torch
    torchvision
    ultralytics~=8.2.70
    ```
    
    패키지 설치 명령어
    
    ```bash
    pip install -r requirements.txt
    ```
    

---

## 모델 및 샘플

[https://www.dropbox.com/scl/fi/ouuaaifyuby2rsxxmtme4/best.pt?rlkey=r60jr4v8c7hofz59qcaumos7h&dl=0](https://www.dropbox.com/scl/fi/ouuaaifyuby2rsxxmtme4/best.pt?rlkey=r60jr4v8c7hofz59qcaumos7h&dl=0)

[https://www.dropbox.com/scl/fi/yx7ztsxwd737d29tw9r6f/sample_video.mp4?rlkey=blpa1qpkq7tbjj55bpeyavlsl&dl=0](https://www.dropbox.com/scl/fi/yx7ztsxwd737d29tw9r6f/sample_video.mp4?rlkey=blpa1qpkq7tbjj55bpeyavlsl&dl=0)

---

## 결과

![Untitled](Video%20File%20Mosiac%20Processing%20Web%20Application%205f47d05a079846a8bb832718b2f5e809/Untitled%201.png)

---

## Result

[https://www.youtube.com/watch?v=M9yvSEk_19Q](https://www.youtube.com/watch?v=M9yvSEk_19Q)