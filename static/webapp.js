document.addEventListener("DOMContentLoaded", () => {
  const bigCircle = document.querySelector(".big-circle");
  // If class selector doesn't work, try the ID
  const bigCircleElement = bigCircle || document.getElementById("bigCircle");
  
  if (bigCircleElement) {
    bigCircleElement.addEventListener("click", () => {
      toggleVoiceRecording();
    });
  }

  // Setup options toggle functionality
  const optionsToggle = document.getElementById('options-toggle');
  const optionsContainer = document.getElementById('options-container');
  
  if (optionsToggle && optionsContainer) {
    optionsToggle.addEventListener('click', () => {
      optionsToggle.classList.toggle('active');
      if (optionsContainer.style.display === 'none') {
        optionsContainer.style.display = 'flex';
        // Allow the transition to start
        setTimeout(() => {
          optionsContainer.classList.add('visible');
        }, 10);
      } else {
        optionsContainer.classList.remove('visible');
        // Wait for transition to finish before hiding
        setTimeout(() => {
          optionsContainer.style.display = 'none';
        }, 300);
      }
    });
  }

  // Model language support configuration - only Whisper models should show language options
  const whisperModels = [
    'whisper-large',
    'whisper-medium',
    'whisper-small',
    'whisper-base',
    'whisper-tiny'
  ];
  
  // Language dropdown visibility toggling
  const sttModelSelect = document.getElementById('stt-model');
  const sttLanguageContainer = document.getElementById('stt-language-container');
  const sttLanguageSelect = document.getElementById('stt-language');
  const ttsModelSelect = document.getElementById('tts-model');
  
  // Make sure all dropdowns start with placeholder selected
  sttModelSelect.selectedIndex = 0;
  if (sttLanguageSelect) {
    sttLanguageSelect.selectedIndex = 0;
  }
  ttsModelSelect.selectedIndex = 0;
  document.getElementById('tts-gender').selectedIndex = 0;
  
  // Language mapping from STT language code to TTS language code
  const languageMapping = {
    'en': 'en-US',  // Now using US English as default
    'ta': 'ta-IN',  // Tamil
    'kn': 'kn-IN',  // Kannada
    'te': 'te-IN',  // Telugu
    'ml': 'ml-IN',  // Malayalam
    'hi': 'hi-IN'   // Hindi
  };

  // No more status container - removed
  
  function toggleLanguageDropdown() {
    const selectedModel = sttModelSelect.value;
    
    // Only show language dropdown for whisper models
    if (whisperModels.includes(selectedModel)) {
      // First make the language dropdown visible
      sttLanguageContainer.style.display = 'flex';
      
      // Always make sure the placeholder is selected when the dropdown becomes visible
      if (sttLanguageSelect) {
        sttLanguageSelect.selectedIndex = 0;
      }
    } else {
      // Hide language dropdown for non-Whisper models
      sttLanguageContainer.style.display = 'none';
    }
  }
  
  // Function to update TTS dropdown based on selected STT language
  function updateTTSLanguage(languageCode) {
    // Only update if the user has selected a language (not the placeholder)
    if (!languageCode || languageCode === '') {
      return;
    }
    
    // If user has explicitly chosen a TTS language already, respect their choice
    if (ttsModelSelect.selectedIndex !== 0) {
      return;
    }
    
    // Map the STT language code to TTS language code
    const ttsLanguage = languageMapping[languageCode] || 'en-US';
    
    // Find and select the matching option in TTS dropdown
    for (let i = 0; i < ttsModelSelect.options.length; i++) {
      if (ttsModelSelect.options[i].value === ttsLanguage) {
        ttsModelSelect.selectedIndex = i;
        break;
      }
    }
  }
  
  // Add event listener for STT language change to update TTS language
  if (sttLanguageSelect) {
    sttLanguageSelect.addEventListener('change', (e) => {
      updateTTSLanguage(e.target.value);
    });
  }
  
  // Initial check - dropdown should be hidden until a model is selected
  toggleLanguageDropdown();
  
  // Add event listener for model change
  sttModelSelect.addEventListener('change', toggleLanguageDropdown);

  let recording = false;
  let mediaRecorder;
  let audioChunks = [];
  let stream;

  function toggleVoiceRecording() {
    if (recording) {
      // Stop recording if already recording
      stopRecording();
    } else {
      // Validate all options are selected before recording
      if (validateOptionSelections()) {
        // Start recording if all options are selected
        startRecording();
      }
    }
  }
  
  // Add function to validate all required options are selected
  function validateOptionSelections() {
    // Get the selected values from dropdowns
    const sttModel = document.getElementById("stt-model").value;
    const ttsModel = document.getElementById("tts-model").value;
    const ttsGender = document.getElementById("tts-gender").value;
    
    // Check if all required dropdowns have values
    if (!sttModel) {
      alert("Please select a speech recognition model before recording");
      return false;
    }
    
    if (!ttsModel) {
      alert("Please select a text-to-speech voice before recording");
      return false;
    }
    
    if (!ttsGender) {
      alert("Please select a voice gender before recording");
      return false;
    }
    
    // If using a Whisper model, ensure language is selected
    if (whisperModels.includes(sttModel)) {
      const sttLanguage = document.getElementById("stt-language").value;
      if (!sttLanguage) {
        alert("Please select a speech recognition language before recording");
        return false;
      }
    }
    
    return true;
  }

  function startRecording() {
    console.log("Starting recording... Requesting microphone access");
    
    // Visual feedback when recording starts
    if (bigCircleElement) {
      // Add the recording class for rotation animation
      bigCircleElement.classList.add("recording");
    }
    
    // Check if mediaDevices is supported
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.error("MediaDevices API not supported in this browser");
      alert("Your browser doesn't support audio recording. Please try a modern browser like Chrome or Firefox.");
      resetCircleAppearance();
      return;
    }
    
    // Simple audio constraint
    const audioConstraints = {
      audio: true
    };
    
    navigator.mediaDevices.getUserMedia(audioConstraints)
      .then(audioStream => {
        console.log("Microphone access granted");
        stream = audioStream;
        
        // Get audio track settings for debugging
        const audioTrack = audioStream.getAudioTracks()[0];
        console.log("Audio track settings:", audioTrack.getSettings());
        
        // Configure MediaRecorder with options for better compatibility
        let options;
        
        // Try different audio formats in order of preference
        const preferredFormats = [
          'audio/webm;codecs=opus',  // Best quality but not all browsers support it
          'audio/webm',              // More widely supported
          'audio/mp3',               // Fallback
          'audio/wav'                // Last resort
        ];
        
        // Find first supported format
        for (const format of preferredFormats) {
          try {
            if (MediaRecorder.isTypeSupported(format)) {
              options = { 
                mimeType: format,
                audioBitsPerSecond: 128000
              };
              console.log(`Using audio format: ${format}`);
              break;
            }
          } catch (e) {
            console.warn(`Format ${format} not supported`);
          }
        }
        
        try {
          mediaRecorder = new MediaRecorder(stream, options);
          console.log("MediaRecorder initialized with options:", options);
        } catch (e) {
          // Fallback to default options if the specified format is not supported
          console.warn("Specified audio formats not supported, using default format:", e);
          mediaRecorder = new MediaRecorder(stream);
          console.log("Using default MediaRecorder format:", mediaRecorder.mimeType);
        }
        
        audioChunks = [];
        recording = true;

        mediaRecorder.addEventListener("dataavailable", event => {
          audioChunks.push(event.data);
          console.log("Audio data chunk received:", event.data.type, event.data.size, "bytes");
        });

        mediaRecorder.addEventListener("stop", () => {
          console.log("Recording stopped, processing audio");
          
          // Check if we have audio data
          if (audioChunks.length === 0 || (audioChunks.length === 1 && audioChunks[0].size < 100)) {
            console.error("No audio data captured or audio too short");
            alert("No audio was captured. Please try speaking louder or check your microphone.");
            resetCircleAppearance();
            return;
          }
          
          // Process the recording
          // Get the actual mime type from the recorder
          const blobMimeType = mediaRecorder.mimeType || "audio/webm";
          const audioBlob = new Blob(audioChunks, { type: blobMimeType });
          
          console.log("Created audio blob:", audioBlob.type, audioBlob.size, "bytes");
          
          // Debug: examine first few bytes of the blob to verify format
          const reader = new FileReader();
          reader.onload = function() {
            const arrayBuffer = reader.result;
            const bytes = new Uint8Array(arrayBuffer).subarray(0, 16);
            let hexString = '';
            bytes.forEach(byte => {
              hexString += byte.toString(16).padStart(2, '0');
            });
            console.log("First 16 bytes of audio blob:", hexString);
            
            // Now send the audio blob to the server
            sendVoiceToServer(audioBlob);
          };
          reader.readAsArrayBuffer(audioBlob);
          
          // Clean up
          if (stream) {
            stream.getTracks().forEach(track => track.stop());
          }
        });

        // Set a dataavailable event every 250ms for better streaming
        mediaRecorder.start(250);
        console.log("MediaRecorder started with interval: 250ms");
      })
      .catch(err => {
        console.error("Microphone access error:", err);
        alert("Unable to access your microphone. Please check your browser permissions and try again.");
        
        // Reset visual feedback on error
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
      // Remove the recording class to stop rotation
      bigCircleElement.classList.remove("recording");
    }
  }

  function sendVoiceToServer(audioBlob) {
    // Log audio details for debugging
    console.log("Sending audio to server:", audioBlob.type, audioBlob.size, "bytes");
    
    const formData = new FormData();
    
    // Use the correct filename extension based on mime type
    let filename = "recording.webm";
    if (audioBlob.type.includes("mp3")) {
      filename = "recording.mp3";
    } else if (audioBlob.type.includes("wav")) {
      filename = "recording.wav";
    }
    
    formData.append("audio", audioBlob, filename);
    console.log("Appended audio to FormData with filename:", filename);
    
    // Use the validation function - this is a safeguard in case something bypasses
    // the initial validation when recording started
    if (!validateOptionSelections()) {
      return;
    }
    
    // Get the selected values from dropdowns
    const sttModel = document.getElementById("stt-model").value;
    const ttsModel = document.getElementById("tts-model").value;
    const ttsGender = document.getElementById("tts-gender").value;
    
    // If using a Whisper model, add language to form data
    if (whisperModels.includes(sttModel)) {
      const sttLanguage = document.getElementById("stt-language").value;
      formData.append("stt_language", sttLanguage);
      console.log(`Using STT: ${sttModel}, Language: ${sttLanguage}, TTS: ${ttsModel}, Gender: ${ttsGender}`);
    } else {
      // For Nova models, always use English
      formData.append("stt_language", "en");
      console.log(`Using STT: ${sttModel}, Language: en, TTS: ${ttsModel}, Gender: ${ttsGender}`);
    }
    
    // Add the selected options to the form data
    formData.append("stt_model", sttModel);
    formData.append("tts_model", ttsModel);
    formData.append("tts_gender", ttsGender);
    
    // Show loading indicator
    document.getElementById("loading-indicator").style.display = "block";
    
    fetch("/voice_agent", {
      method: "POST",
      body: formData
    })
    .then(response => {
      // Hide loading indicator
      document.getElementById("loading-indicator").style.display = "none";
      
      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      return response.json();
    })
    .then(data => {
      if (data.error) {
        console.error("Server error:", data.error);
        alert("Error: " + data.error);
      } else {
        playAudio(data.tts_audio);
        
        // Display the transcription and response
        if (data.transcription) {
          document.getElementById("transcription").textContent = data.transcription;
        }
        
        if (data.llm_response) {
          document.getElementById("llm-response").textContent = data.llm_response;
        }
      }
    })
    .catch(error => {
      // Hide loading indicator
      document.getElementById("loading-indicator").style.display = "none";
      
      console.error("Error sending audio to server:", error);
      alert("Error communicating with the server. Please try again.");
    });
  }

  function playAudio(base64Audio) {
    // Create audio element to play the response
    const audio = new Audio("data:audio/mp3;base64," + base64Audio);
    audio.play()
      .catch(err => {
        console.error("Error playing audio:", err);
      });
  }
});