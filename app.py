from io import BytesIO
from flask import Flask, request, jsonify, render_template
from stt_deepgram import deepgram_transcribe
from stt_google_cloud import google_cloud_transcribe
from stt_assemblyai import assemblyai_transcribe
from voice_agent_openai import voice_assistant_response
from tts_google_cloud import text_to_speech

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/voice_agent', methods=['POST'])
def voice_agent():
    audio_data = BytesIO(request.files['audio'].read())
    stt_provider = request.form.get('stt_provider', 'deepgram')
    stt_model = request.form.get('stt_model', '')
    stt_language = request.form.get('stt_language', 'en')
    tts_model = request.form.get('tts_model', 'en-US')
    tts_gender = request.form.get('tts_gender', 'MALE')
    
    output_language = {
        'en-US': 'en', 'ta-IN': 'ta', 'kn-IN': 'kn',
        'te-IN': 'te', 'ml-IN': 'ml', 'hi-IN': 'hi'
    }.get(tts_model, 'en')
    
    if stt_provider == 'google_cloud':
        transcription = google_cloud_transcribe(audio_data, language=stt_language)
    elif stt_provider == 'assemblyai':
        transcription = assemblyai_transcribe(audio_data, model=stt_model, language=stt_language)
    else:
        transcription = deepgram_transcribe(audio_data, model=stt_model, language='en')
    
    input_language = 'en' if stt_provider == 'deepgram' else stt_language
    llm_response = voice_assistant_response(
        transcription, 
        language=input_language,
        output_language=output_language
    )
    
    tts_audio = text_to_speech(
        llm_response, 
        language_code=tts_model, 
        gender=tts_gender
    )
    
    return jsonify({
        'transcription': transcription,
        'llm_response': llm_response,
        'tts_audio': tts_audio
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)