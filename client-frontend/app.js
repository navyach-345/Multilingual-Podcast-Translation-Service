document.addEventListener("DOMContentLoaded", function () {
    const introMessage = document.querySelector(".intro-message");
    const uploadContainer = document.querySelector(".container");
    const fileUpload = document.getElementById("file-upload");
    const fileLabel = document.getElementById("file-label");
    const uploadBtn = document.getElementById("upload-btn");
    const sourceLanguage = document.getElementById("source-language");
    const targetLanguage = document.getElementById("target-language");
    const dialectOption = document.getElementById("dialect-option");
    const dialect = document.getElementById("dialect");
    const loadingIndicator = document.getElementById("loadingIndicator");
    const output = document.getElementById("output");
    const translatedText = document.getElementById("translated-text");
    const audioPlayer = document.getElementById("audioPlayer");
    const playPauseBtn = document.getElementById("playPauseBtn");
    const seekSlider = document.getElementById("seekSlider");
    const volumeSlider = document.getElementById("volumeSlider");
    const muteBtn = document.getElementById("muteBtn");
    const speedSelect = document.getElementById("playbackSpeed");
    const currentTimeSpan = document.getElementById("currentTime");
    const durationSpan = document.getElementById("duration");
    const downloadLink = document.getElementById("downloadLink");
    const resetContainer = document.querySelector(".reset-container");
    const resetBtn = document.getElementById("reset-btn");

    setTimeout(() => {
        introMessage.classList.add("show-message");
        setTimeout(() => {
            introMessage.classList.remove("show-message");
            setTimeout(() => {
                introMessage.style.display = "none";
                uploadContainer.style.display = "flex";
            }, 2000);
        }, 3000);
    }, 500);

    fileUpload.addEventListener("change", () => {
        if (fileUpload.files.length > 0) {
            fileLabel.textContent = "Uploaded";
            fileLabel.style.textAlign = "center";
            document.getElementById("options").classList.remove("hidden");
            uploadBtn.classList.remove("hidden");
        }
    });

    const languages = {
        "1": { name: "English", code: "en-US", dialects: ["en", "en-au", "en-uk", "en-us", "en-in"] },
        "2": { name: "Telugu", code: "te", dialects: ["te"] },
        "3": { name: "Hindi", code: "hi", dialects: ["hi"] },
        "4": { name: "Spanish", code: "es", dialects: ["es", "es-es", "es-us"] },
        "5": { name: "French", code: "fr-FR", dialects: ["fr-ca", "fr-fr"] },
        "6": { name: "German", code: "de", dialects: ["de"] },
        "7": { name: "Chinese (Mandarin)", code: "zh-CN", dialects: ["zh-cn", "zh-tw"] },
        "8": { name: "Japanese", code: "ja", dialects: ["ja"] },
        "9": { name: "Korean", code: "ko", dialects: ["ko"] },
        "10": { name: "Italian", code: "it", dialects: ["it"] },
        "11": { name: "Portuguese", code: "pt-PT", dialects: ["pt", "pt-br", "pt-pt"] },
        "12": { name: "Russian", code: "ru", dialects: ["ru"] },
        "13": { name: "Dutch", code: "nl", dialects: ["nl"] },
        "14": { name: "Arabic", code: "ar", dialects: ["ar"] },
    };

    Object.values(languages).forEach((lang) => {
        const option = document.createElement("option");
        option.value = lang.code;
        option.textContent = lang.name;
        sourceLanguage.appendChild(option.cloneNode(true));
        targetLanguage.appendChild(option.cloneNode(true));
    });

    targetLanguage.addEventListener("change", () => {
        const selectedCode = targetLanguage.value;
        const selectedLanguage = Object.values(languages).find(lang => lang.code === selectedCode);

        if (selectedLanguage && Array.isArray(selectedLanguage.dialects) && selectedLanguage.dialects.length > 1) {
            dialectOption.classList.remove("hidden");
            dialect.innerHTML = "";
            selectedLanguage.dialects.forEach(d => {
                const option = document.createElement("option");
                option.value = d;
                option.textContent = d;
                dialect.appendChild(option);
            });
        } else {
            dialectOption.classList.add("hidden");
        }
    });

    uploadBtn.addEventListener("click", async () => {
        const file = fileUpload.files[0];
        const sourceLang = sourceLanguage.value;
        let targetLang = targetLanguage.value;

        if (!dialectOption.classList.contains("hidden") && dialect.value) {
            targetLang = dialect.value;
        }

        if (!file || !sourceLang || !targetLang) {
            alert("Please complete all fields.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        formData.append("source_language", sourceLang);
        formData.append("target_language", targetLang);

        uploadContainer.style.display = "none";
        loadingIndicator.style.display = "flex";

        try {
            const response = await fetch("http://<Ingress_IP_Address>/translate", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Failed to process request.");
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            if (data.job_id) {
                const jobId = data.job_id;
                pollForResult(jobId);
            } else if (data.text && data.audio) {
                displayResults(data.text, data.audio);
            } else {
                throw new Error("Unexpected response format.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert(error.message);
            uploadContainer.style.display = "flex";
            loadingIndicator.style.display = "none";
        }
    });

    function pollForResult(jobId) {
        const maxWaitTime = 7 * 60 * 1000;
        const startTime = Date.now();

        const intervalId = setInterval(async () => {
            try {
                const resultResponse = await fetch(`http://<Ingress_IP_Address>/results/${jobId}`);
                const resultData = await resultResponse.json();
                if (resultResponse.ok && resultData.text && resultData.audio) {
                    clearInterval(intervalId);
                    displayResults(resultData.text, resultData.audio);
                    return;
                }

                if (resultResponse.status === 202) {
                    console.log("Results still processing...");
                }

                if (Date.now() - startTime > maxWaitTime) {
                    clearInterval(intervalId);
                    alert("The process is taking too long. Please try again later.");
                    loadingIndicator.style.display = "none";
                    uploadContainer.style.display = "flex";
                    return;
                }

            } catch (error) {
                console.error("Polling error:", error);
                clearInterval(intervalId);
                alert("An error occurred while retrieving results. Please try again.");
                loadingIndicator.style.display = "none";
                uploadContainer.style.display = "flex";
            }
        }, 5000);
    }

    function displayResults(encodedText, encodedAudio) {
        translatedText.textContent = decodeURIComponent(escape(window.atob(encodedText)));
        audioPlayer.src = `data:audio/mp3;base64,${encodedAudio}`;
        audioPlayer.load();

        if (downloadLink) {
            downloadLink.href = `data:audio/mp3;base64,${encodedAudio}`;
            downloadLink.download = "translated_audio.mp3";
        } else {
            console.error("Download button not found in the DOM.");
        }

        initializeAudioPlayer();

        loadingIndicator.style.display = "none";
        output.style.display = "flex";
        resetContainer.style.display = "block"; // Show Reset button
    }

    function initializeAudioPlayer() {
        playPauseBtn.addEventListener("click", () => {
            if (audioPlayer.paused) {
                audioPlayer.play();
                playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
            } else {
                audioPlayer.pause();
                playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
            }
        });

        audioPlayer.addEventListener("timeupdate", () => {
            if (!isNaN(audioPlayer.duration)) {
                const percent = (audioPlayer.currentTime / audioPlayer.duration) * 100;
                seekSlider.value = percent;
                currentTimeSpan.textContent = formatTime(audioPlayer.currentTime);
            }
        });

        seekSlider.addEventListener("input", () => {
            const time = (seekSlider.value / 100) * audioPlayer.duration;
            audioPlayer.currentTime = time;
        });

        volumeSlider.addEventListener("input", () => {
            audioPlayer.volume = volumeSlider.value;
            updateVolumeIcon();
        });

        muteBtn.addEventListener("click", () => {
            audioPlayer.muted = !audioPlayer.muted;
            updateVolumeIcon();
        });

        speedSelect.addEventListener("change", () => {
            audioPlayer.playbackRate = speedSelect.value;
        });

        audioPlayer.addEventListener("loadedmetadata", () => {
            durationSpan.textContent = formatTime(audioPlayer.duration || 0);
        });

        function formatTime(seconds) {
            if (isNaN(seconds)) return "0:00";
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = Math.floor(seconds % 60);
            return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        }

        function updateVolumeIcon() {
            const icon = muteBtn.querySelector("i");
            if (audioPlayer.muted || audioPlayer.volume === 0) {
                icon.className = "fas fa-volume-mute";
            } else if (audioPlayer.volume < 0.5) {
                icon.className = "fas fa-volume-down";
            } else {
                icon.className = "fas fa-volume-up";
            }
        }
    }

    resetBtn.addEventListener("click", () => {
        // Reset the UI to the initial state
        output.style.display = "none";
        resetContainer.style.display = "none";
        uploadContainer.style.display = "flex";
        translatedText.textContent = "";
        fileUpload.value = "";
        fileLabel.textContent = "Select an MP3 File";
        fileLabel.style.textAlign = "left";
        document.getElementById("options").classList.add("hidden");
        uploadBtn.classList.add("hidden");
        sourceLanguage.selectedIndex = 0;
        targetLanguage.selectedIndex = 0;
        dialectOption.classList.add("hidden");
    });
});
