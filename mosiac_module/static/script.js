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
