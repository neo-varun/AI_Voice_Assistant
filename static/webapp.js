document.addEventListener("DOMContentLoaded", () => {
  const bigCircle = document.querySelector(".big-circle");
  // If class selector doesn't work, try the ID
  const bigCircleElement = bigCircle || document.getElementById("bigCircle");
  
  if (bigCircleElement) {
    bigCircleElement.addEventListener("click", () => {
      toggleVoiceRecording();
    });
  }

  let recording = false;
  let mediaRecorder;
  let audioChunks = [];
  let stream;

  function toggleVoiceRecording() {
    if (recording) {
      // Stop recording if already recording
      stopRecording();
    } else {
      // Start recording if not recording
      startRecording();
    }
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
    
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(audioStream => {
        console.log("Microphone access granted");
        stream = audioStream;
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        recording = true;

        mediaRecorder.addEventListener("dataavailable", event => {
          audioChunks.push(event.data);
        });

        mediaRecorder.addEventListener("stop", () => {
          console.log("Recording stopped, processing audio");
          // Process the recording
          const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
          sendVoiceToServer(audioBlob);
          
          // Clean up
          if (stream) {
            stream.getTracks().forEach(track => track.stop());
          }
        });

        mediaRecorder.start();
        console.log("MediaRecorder started");
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
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.webm");

    fetch("/voice_agent", {
      method: "POST",
      body: formData
    })
    .then(response => {
      if (!response.ok) throw new Error("Server error");
      return response.json();
    })
    .then(data => {
      if (data.error) {
        console.error("Server error:", data.error);
        alert("Error: " + data.error);
      } else {
        playAudio(data.tts_audio);
      }
    })
    .catch(err => {
      console.error("Error processing voice:", err);
      alert("Error processing your voice message. Please try again.");
    });
  }

  function playAudio(base64Audio) {
    const audio = new Audio("data:audio/mp3;base64," + base64Audio);
    audio.play();
  }
});