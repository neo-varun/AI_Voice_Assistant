from io import BytesIO
from flask import Flask, request, jsonify, render_template
from stt_deepgram import transcribe_audio
from voice_agent_openai import voice_assistant_response
from tts_google_cloud import text_to_speech

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/voice_agent', methods=['POST'])
def voice_agent():

    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file received'}), 400

        audio_data = BytesIO(request.files['audio'].read())
        stt_model = request.form.get('stt_model', '')
        stt_language = 'en' if stt_model.startswith('nova-') else request.form.get('stt_language', 'en')
        tts_model = request.form.get('tts_model', 'en-US')
        tts_gender = request.form.get('tts_gender', 'MALE')
        
        output_language = {
            'en-US': 'en', 'ta-IN': 'ta', 'kn-IN': 'kn',
            'te-IN': 'te', 'ml-IN': 'ml', 'hi-IN': 'hi'
        }.get(tts_model, 'en')
        
        transcription = transcribe_audio(audio_data, model=stt_model, language=stt_language)
        if transcription.startswith("Error"):
            return jsonify({'error': transcription}), 500
            
        llm_response = voice_assistant_response(
            transcription, 
            language=stt_language,
            output_language=output_language
        )
        if llm_response.startswith("Error"):
            return jsonify({'error': llm_response}), 500
            
        tts_audio = text_to_speech(llm_response, language_code=tts_model, gender=tts_gender)
        if tts_audio.startswith("Error"):
            return jsonify({'error': tts_audio}), 500

        return jsonify({
            'transcription': transcription,
            'llm_response': llm_response,
            'tts_audio': tts_audio
        })

    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)