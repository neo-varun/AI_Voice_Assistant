document.addEventListener("DOMContentLoaded", () => {
  const bigCircleElement = document.querySelector(".big-circle") || document.getElementById("bigCircle");
  
  if (bigCircleElement) {
    bigCircleElement.addEventListener("click", toggleVoiceRecording);
  }

  const optionsToggle = document.getElementById('options-toggle');
  const optionsContainer = document.getElementById('options-container');
  
  if (optionsToggle && optionsContainer) {
    optionsToggle.addEventListener('click', () => {
      optionsToggle.classList.toggle('active');
      const isHidden = optionsContainer.style.display === 'none';
      
      optionsContainer.style.display = isHidden ? 'flex' : 'none';
      
      if (isHidden) {
        setTimeout(() => optionsContainer.classList.add('visible'), 10);
      } else {
        optionsContainer.classList.remove('visible');
      }
    });
  }

  const whisperModels = [
    'whisper-large', 'whisper-medium', 'whisper-small', 'whisper-base', 'whisper-tiny'
  ];
  
  const sttModelSelect = document.getElementById('stt-model');
  const sttLanguageContainer = document.getElementById('stt-language-container');
  const sttLanguageSelect = document.getElementById('stt-language');
  const ttsModelSelect = document.getElementById('tts-model');
  const ttsGenderSelect = document.getElementById('tts-gender');
  
  sttModelSelect.selectedIndex = 0;
  if (sttLanguageSelect) sttLanguageSelect.selectedIndex = 0;
  ttsModelSelect.selectedIndex = 0;
  ttsGenderSelect.selectedIndex = 0;
  
  const languageMapping = {
    'en': 'en-US', 'ta': 'ta-IN', 'kn': 'kn-IN', 
    'te': 'te-IN', 'ml': 'ml-IN', 'hi': 'hi-IN'
  };
  
  function toggleLanguageDropdown() {
    const isWhisperModel = whisperModels.includes(sttModelSelect.value);
    sttLanguageContainer.style.display = isWhisperModel ? 'flex' : 'none';
    if (isWhisperModel) sttLanguageSelect.selectedIndex = 0;
  }
  
  function updateTTSLanguage(languageCode) {
    if (!languageCode || ttsModelSelect.selectedIndex !== 0) return;
    
    const ttsLanguage = languageMapping[languageCode] || 'en-US';
    
    Array.from(ttsModelSelect.options).forEach((option, idx) => {
      if (option.value === ttsLanguage) ttsModelSelect.selectedIndex = idx;
    });
  }
  
  if (sttLanguageSelect) {
    sttLanguageSelect.addEventListener('change', (e) => updateTTSLanguage(e.target.value));
  }
  
  toggleLanguageDropdown();
  sttModelSelect.addEventListener('change', toggleLanguageDropdown);

  let recording = false;
  let mediaRecorder;
  let audioChunks = [];
  let stream;

  function toggleVoiceRecording() {
    if (recording) {
      stopRecording();
    } else if (validateOptionSelections()) {
      startRecording();
    }
  }
  
  function validateOptionSelections() {
    const sttModel = sttModelSelect.value;
    const needsLanguage = whisperModels.includes(sttModel) && !document.getElementById("stt-language").value;
    
    if (!sttModel || !ttsModelSelect.value || !ttsGenderSelect.value) {
      alert("Please select all required options before recording");
      return false;
    }
    
    if (needsLanguage) {
      alert("Please select a speech recognition language before recording");
      return false;
    }
    
    return true;
  }

  function startRecording() {
    if (bigCircleElement) bigCircleElement.classList.add("recording");
    
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert("Your browser doesn't support audio recording. Please try a modern browser like Chrome or Firefox.");
      resetCircleAppearance();
      return;
    }
    
    navigator.mediaDevices.getUserMedia({audio: true})
      .then(audioStream => {
        stream = audioStream;
        
        let options;
        const preferredFormats = [
          'audio/webm;codecs=opus', 'audio/webm', 'audio/mp3', 'audio/wav'
        ];
        
        for (const format of preferredFormats) {
          if (MediaRecorder.isTypeSupported(format)) {
            options = { mimeType: format, audioBitsPerSecond: 128000 };
            break;
          }
        }
        
        try {
          mediaRecorder = new MediaRecorder(stream, options);
        } catch (e) {
          mediaRecorder = new MediaRecorder(stream);
        }
        
        audioChunks = [];
        recording = true;

        mediaRecorder.addEventListener("dataavailable", event => {
          audioChunks.push(event.data);
        });

        mediaRecorder.addEventListener("stop", () => {
          if (audioChunks.length === 0 || (audioChunks.length === 1 && audioChunks[0].size < 100)) {
            alert("No audio was captured. Please try speaking louder or check your microphone.");
            resetCircleAppearance();
            return;
          }
          
          const blobMimeType = mediaRecorder.mimeType || "audio/webm";
          const audioBlob = new Blob(audioChunks, { type: blobMimeType });
          
          sendVoiceToServer(audioBlob);
          
          if (stream) {
            stream.getTracks().forEach(track => track.stop());
          }
        });

        mediaRecorder.start(250);
      })
      .catch(() => {
        alert("Unable to access your microphone. Please check your browser permissions and try again.");
        resetCircleAppearance();
      });
  }

  function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      recording = false;
      mediaRecorder.stop();
      resetCircleAppearance();
    }
  }

  function resetCircleAppearance() {
    if (bigCircleElement) {
      bigCircleElement.classList.remove("recording");
    }
  }

  function sendVoiceToServer(audioBlob) {
    const formData = new FormData();
    const sttModel = sttModelSelect.value;
    
    let fileExtension = "webm";
    if (audioBlob.type.includes("mp3")) fileExtension = "mp3";
    else if (audioBlob.type.includes("wav")) fileExtension = "wav";
    
    formData.append("audio", audioBlob, `recording.${fileExtension}`);
    formData.append("stt_language", whisperModels.includes(sttModel) 
      ? document.getElementById("stt-language").value 
      : "en"
    );
    formData.append("stt_model", sttModel);
    formData.append("tts_model", ttsModelSelect.value);
    formData.append("tts_gender", ttsGenderSelect.value);
    
    fetch("/voice_agent", {
      method: "POST",
      body: formData
    })
    .then(response => response.ok ? response.json() : Promise.reject(`Server error: ${response.status}`))
    .then(data => data.error ? alert("Error: " + data.error) : playAudio(data.tts_audio))
    .catch(() => alert("Error communicating with the server. Please try again."));
  }

  function playAudio(base64Audio) {
    const audio = new Audio("data:audio/mp3;base64," + base64Audio);
    audio.play().catch(() => {
      alert("Error playing the response audio.");
    });
  }
});