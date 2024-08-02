document.addEventListener('DOMContentLoaded', function () {
    const uploadButton = document.querySelector('.uploadButton');
    const fileInput = document.getElementById('fileInput');
    const videoPreview = document.getElementById('videoPreviewer');
    const downloadSection = document.getElementById('downloadSection');
    const downloadButton = document.getElementById('downloadButton');
    const processingText = document.getElementById('processingText');
    const processingCat = document.querySelector('.processing img');
    const outputVideo = document.getElementById('outputVideo');

    // Upload button click opens file dialog
    uploadButton.addEventListener('click', function () {
        fileInput.click();
    });

    // Display selected video and show download section
    fileInput.addEventListener('change', function (event) {
        const file = event.target.files[0];
        if (file) {
            videoPreview.src = URL.createObjectURL(file);
            videoPreview.style.display = 'block';
            downloadSection.style.display = 'flex';  // Show download section
            startUpload(file);
        }
    });

    // Upload and process video
    function startUpload(file) {
        const formData = new FormData();
        formData.append('file', file);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/process', true);

        xhr.upload.addEventListener('progress', function (event) {
            if (event.lengthComputable) {
                const percentComplete = (event.loaded / event.total) * 100;
                processingText.textContent = `Uploading ${percentComplete.toFixed(0)}%`;
            }
        });

        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    // Change text to "Processing" and start polling for progress
                    processingText.textContent = 'Processing 0%';
                    processingCat.classList.add('rotating'); // Start rotating the cat image
                    checkProgress();
                }
            }
        };

        xhr.send(formData);
    }

    // Check progress of video processing
    function checkProgress() {
        const interval = setInterval(function () {
            const xhr = new XMLHttpRequest();
            xhr.open('GET', '/progress', true);

            xhr.onreadystatechange = function () {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        const response = JSON.parse(xhr.responseText);
                        const progress = response.progress;

                        processingText.textContent = `Processing ${progress.toFixed(0)}%`;

                        if (progress >= 100) {
                            clearInterval(interval);
                            processingText.textContent = 'Processing 100%';
                            processingCat.classList.remove('rotating'); // Stop rotating the cat image
                            downloadButton.style.display = 'block';
                            downloadButton.addEventListener('click', function () {
                                window.location.href = '/download';
                            });

                            // Fetch the processed video and display it
                            fetchProcessedVideo();
                        }
                    }
                }
            };

            xhr.send();
        }, 1000); // 1초마다 진행률을 확인합니다.
    }

    // Fetch the processed video and display it
    function fetchProcessedVideo() {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', '/download', true);
        xhr.responseType = 'blob';

        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    const blob = xhr.response;
                    const url = URL.createObjectURL(blob);
                    outputVideo.src = url;
                    outputVideo.style.display = 'block';
                }
            }
        };

        xhr.send();
    }
});
