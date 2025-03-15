document.addEventListener("DOMContentLoaded", () => {
  
  const bigCircle = document.getElementById("bigCircle");
  const optionsToggle = document.getElementById('options-toggle');
  const optionsContainer = document.getElementById('options-container');
  const sttModel = document.getElementById('stt-model');
  const sttLanguageContainer = document.getElementById('stt-language-container');
  const sttLanguage = document.getElementById('stt-language');
  const ttsModel = document.getElementById('tts-model');
  const ttsGender = document.getElementById('tts-gender');
  
  const supportLanguageSelectionModels = [
    'google_cloud-default', 
    'assemblyai-best', 
    'assemblyai-nano'
  ];
  
  let recording = false;
  let mediaRecorder;
  let audioChunks = [];
  let stream;

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
    const modelSelection = sttModel.value;
    const showLanguageDropdown = supportLanguageSelectionModels.includes(modelSelection);
    sttLanguageContainer.style.display = showLanguageDropdown ? 'flex' : 'none';
    
    if (!showLanguageDropdown && sttLanguage) {
      sttLanguage.value = 'en';
    }
  });
  
  sttLanguageContainer.style.display = 'none';
  
  function toggleVoiceRecording() {
    if (recording) {
      if (mediaRecorder && mediaRecorder.state !== "inactive") {
        recording = false;
        mediaRecorder.stop();
        bigCircle.classList.remove("recording");
      }
    } else if (sttModel.value && ttsModel.value && ttsGender.value && 
              (!supportLanguageSelectionModels.includes(sttModel.value) || sttLanguage.value)) {
      startRecording();
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
      new Audio("data:audio/mp3;base64," + data.tts_audio).play();
    });
  }
});