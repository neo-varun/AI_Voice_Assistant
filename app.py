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
        
        # Check if audio data is empty or too small
        audio_size = len(audio_data.getvalue())
        logging.info(f"Received audio size: {audio_size} bytes")
        
        if audio_size < 1000:  # Less than 1KB is likely too small
            return jsonify({'error': 'Audio recording is too short or empty. Please try speaking more clearly and for longer.'}), 400
        
        # Get selected model options from form data
        stt_model = request.form.get('stt_model', '')
        stt_language = request.form.get('stt_language', 'en')
        tts_model = request.form.get('tts_model', 'en-US')  # Default to US English
        tts_gender = request.form.get('tts_gender', 'MALE')
        
        # Validate required parameters
        if not stt_model:
            return jsonify({'error': 'No speech recognition model selected'}), 400
            
        if not tts_model:
            tts_model = 'en-US'  # Default if not provided
            logging.info(f"No TTS model provided, defaulting to {tts_model}")
            
        if not tts_gender or tts_gender not in ['MALE', 'FEMALE']:
            tts_gender = 'MALE'  # Default if not provided or invalid
            logging.info(f"No valid TTS gender provided, defaulting to {tts_gender}")
        
        logging.info(f"Using STT model: {stt_model}, Language: {stt_language}, TTS model: {tts_model}, Gender: {tts_gender}")
        
        # For Nova models, always use English
        if stt_model.startswith('nova-'):
            stt_language = 'en'
            logging.info(f"Nova model detected, forcing language to English")
        
        # Step 1: Transcribe audio using Deepgram with selected model
        # Reset the audio_data position
        audio_data.seek(0)
        transcription = transcribe_audio(audio_data, model=stt_model, language=stt_language)
        
        if not transcription:
            return jsonify({'error': 'Failed to transcribe audio. Please try speaking louder or longer.'}), 500
        
        if transcription.startswith("Error"):
            # Extract the specific error message after "Error: "
            error_message = transcription[transcription.find(":")+1:].strip()
            return jsonify({'error': f"Speech recognition failed: {error_message}"}), 500
            
        # If transcription is too short, it may be insufficient
        if len(transcription.split()) < 2:
            logging.warning(f"Transcription is very short: '{transcription}'")
            return jsonify({'error': 'Speech recognition produced very short output. Please try speaking more clearly and longer.'}), 400

        # Step 2: Determine output language
        # Map TTS language code (e.g., 'en-US') to language code for LLM (e.g., 'en')
        output_language = get_base_language_code(tts_model)
        
        logging.info(f"Input language: {stt_language}, Output language: {output_language}")
        
        # Step 3: Send transcript to Voice Agent API with language parameters
        llm_response = voice_assistant_response(
            transcription, 
            language=stt_language,
            output_language=output_language
        )
        
        if not llm_response:
            return jsonify({'error': 'Failed to generate AI response. Please try again.'}), 500
        
        if llm_response.startswith("Error"):
            # Extract the specific error message after "Error: "
            error_message = llm_response[llm_response.find(":")+1:].strip()
            return jsonify({'error': f"AI processing failed: {error_message}"}), 500

        # Step 4: Convert AI response to speech using Google TTS with output language
        tts_audio = text_to_speech(llm_response, language_code=tts_model, gender=tts_gender)
        
        if not tts_audio:
            return jsonify({'error': 'Failed to convert text to speech. Please try again.'}), 500
        
        if tts_audio.startswith("Error"):
            # Extract the specific error message after "Error: "
            error_message = tts_audio[tts_audio.find(":")+1:].strip()
            return jsonify({'error': f"Text-to-speech failed: {error_message}"}), 500

        return jsonify({
            'transcription': transcription,
            'llm_response': llm_response,
            'tts_audio': tts_audio
        })

    except Exception as e:
        logging.error("Error in /voice_agent: %s", e)
        return jsonify({"error": f"Voice agent processing failed: {str(e)}"}), 500

# Helper function to extract base language code from TTS language code
def get_base_language_code(tts_language_code):
    """
    Maps TTS language codes (e.g., 'en-US') to base language codes for LLM (e.g., 'en')
    """
    mapping = {
        'en-US': 'en',  # English (US)
        'ta-IN': 'ta',  # Tamil
        'kn-IN': 'kn',  # Kannada
        'te-IN': 'te',  # Telugu
        'ml-IN': 'ml',  # Malayalam
        'hi-IN': 'hi',  # Hindi
    }
    return mapping.get(tts_language_code, 'en')  # Default to 'en' if not found

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)