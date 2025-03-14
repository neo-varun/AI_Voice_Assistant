from io import BytesIO
from flask import Flask, request, jsonify, render_template
from stt_deepgram import transcribe_audio
from voice_agent_openai import voice_assistant_response
from tts_google_cloud import text_to_speech
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/voice_agent', methods=['POST'])
def voice_agent():
    try:
        logging.info("Received request at /voice_agent")

        # Check for an audio file in request
        if 'audio' not in request.files or request.files['audio'].filename == '':
            return jsonify({'error': 'No valid audio file received'}), 400

        # Read audio file data
        audio_file = request.files['audio']
        audio_data = BytesIO(audio_file.read())

        # Step 1: Transcribe audio using Deepgram
        transcription = transcribe_audio(audio_data)
        if not transcription or transcription.startswith("Error"):
            return jsonify({'error': transcription or "Failed to transcribe audio"}), 500

        # Step 2: Send transcript to Voice Agent API
        llm_response = voice_assistant_response(transcription)
        if not llm_response or llm_response.startswith("Error"):
            return jsonify({'error': llm_response or "Failed to generate AI response"}), 500

        # Step 3: Convert AI response to speech using Google TTS
        tts_audio = text_to_speech(llm_response)
        if not tts_audio or tts_audio.startswith("Error"):
            return jsonify({'error': tts_audio or "Failed to convert text to speech"}), 500

        return jsonify({
            'transcription': transcription,
            'llm_response': llm_response,
            'tts_audio': tts_audio
        })

    except Exception as e:
        logging.error("Error in /voice_agent: %s", e)
        return jsonify({"error": f"Voice agent processing failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)