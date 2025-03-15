document.addEventListener("DOMContentLoaded", () => {
  
  const bigCircle = document.getElementById("bigCircle");
  const optionsToggle = document.getElementById('options-toggle');
  const optionsContainer = document.getElementById('options-container');
  const sttModel = document.getElementById('stt-model');
  const sttLanguageContainer = document.getElementById('stt-language-container');
  const sttLanguage = document.getElementById('stt-language');
  const ttsModel = document.getElementById('tts-model');
  const ttsGender = document.getElementById('tts-gender');
  const errorMessage = document.getElementById('errorMessage');
  const centerCircle = document.querySelector('.center-circle');
  
  const supportLanguageSelectionModels = [
    'google_cloud-default', 
    'assemblyai-best', 
    'assemblyai-nano'
  ];
  
  let recording = false;
  let mediaRecorder;
  let audioChunks = [];
  let stream;
  let errorTimeout;
  let currentRotation = 0;
  let animationFrame;
  let lastTimestamp = 0;
  let currentAudio = null;

  bigCircle.addEventListener("click", toggleVoiceRecording);
  
  optionsToggle.addEventListener('click', () => {
    optionsToggle.classList.toggle('active');
    optionsContainer.style.display = optionsContainer.style.display === 'none' ? 'flex' : 'none';
    
    if (optionsContainer.style.display === 'flex') {
      setTimeout(() => optionsContainer.classList.add('visible'), 10);
    } else {
      optionsContainer.classList.remove('visible');
    }
  });
  
  sttModel.addEventListener('change', () => {
    const showLanguageDropdown = supportLanguageSelectionModels.includes(sttModel.value);
    sttLanguageContainer.style.display = showLanguageDropdown ? 'flex' : 'none';
    
    if (!showLanguageDropdown && sttLanguage) {
      sttLanguage.value = 'en';
    }
  });
  
  sttLanguageContainer.style.display = 'none';
  
  function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
    
    if (errorTimeout) clearTimeout(errorTimeout);
    errorTimeout = setTimeout(() => errorMessage.classList.remove('show'), 3000);
  }
  
  function updateRotation(timestamp) {
    if (!lastTimestamp) lastTimestamp = timestamp;
    const elapsed = timestamp - lastTimestamp;
    
    currentRotation += (elapsed / 1000) * 45;
    if (currentRotation >= 360) currentRotation -= 360;
    
    centerCircle.style.transform = `translate(-50%, -50%) rotate(${currentRotation}deg)`;
    
    lastTimestamp = timestamp;
    
    if (recording) {
      animationFrame = requestAnimationFrame(updateRotation);
    }
  }
  
  function stopAudioPlayback() {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      currentAudio = null;
      return true;
    }
    return false;
  }
  
  function toggleVoiceRecording() {
    const wasPlayingAudio = stopAudioPlayback();
    
    if (recording) {
      if (mediaRecorder && mediaRecorder.state !== "inactive") {
        recording = false;
        mediaRecorder.stop();
        
        if (animationFrame) {
          cancelAnimationFrame(animationFrame);
          animationFrame = null;
        }
        
        bigCircle.classList.remove("recording");
      }
    } else if (wasPlayingAudio || (sttModel.value && ttsModel.value && ttsGender.value && 
              (!supportLanguageSelectionModels.includes(sttModel.value) || sttLanguage.value))) {
      startRecording();
    } else {
      showError("Please select language options before recording");
    }
  }

  function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(function(streamData) {
        stream = streamData;
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.addEventListener("dataavailable", event => {
          audioChunks.push(event.data);
        });
        
        mediaRecorder.addEventListener("stop", () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
          sendToServer(audioBlob);
          
          if (stream) {
            stream.getTracks().forEach(track => track.stop());
          }
        });
        
        mediaRecorder.start();
        recording = true;
        bigCircle.classList.add("recording");
        
        lastTimestamp = 0;
        animationFrame = requestAnimationFrame(updateRotation);
      });
  }
  
  function sendToServer(audioBlob) {
    const formData = new FormData();
    const [provider, model] = sttModel.value.split('-');
    
    formData.append("audio", audioBlob, "recording.webm");
    formData.append("stt_provider", provider);
    formData.append("stt_model", model);
    formData.append("stt_language", provider === 'deepgram' ? "en" : sttLanguage.value);
    formData.append("tts_model", ttsModel.value);
    formData.append("tts_gender", ttsGender.value);
    
    fetch("/voice_agent", {
      method: "POST",
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      currentAudio = new Audio("data:audio/mp3;base64," + data.tts_audio);
      currentAudio.addEventListener('ended', () => currentAudio = null);
      currentAudio.play();
    });
  }
});