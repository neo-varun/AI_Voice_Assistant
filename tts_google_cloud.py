import base64
from google.cloud import texttospeech

tts_client = texttospeech.TextToSpeechClient()

LANGUAGE_VOICES = {
    'en-US': ['en-US-Chirp3-HD-Orus', 'en-US-Chirp3-HD-Aoede'],
    'ta-IN': ['ta-IN-Chirp3-HD-Puck', 'ta-IN-Chirp3-HD-Aoede'],
    'kn-IN': ['kn-IN-Chirp3-HD-Fenrir', 'kn-IN-Chirp3-HD-Leda'],
    'te-IN': ['te-IN-Chirp3-HD-Orus', 'te-IN-Chirp3-HD-Leda'],
    'ml-IN': ['ml-IN-Chirp3-HD-Orus', 'ml-IN-Chirp3-HD-Aoede'],
    'hi-IN': ['hi-IN-Chirp3-HD-Fenrir', 'hi-IN-Chirp3-HD-Aoede'],
}

GENDER_INDICES = {
    'MALE': 0,
    'FEMALE': 1
}

def text_to_speech(text, language_code="en-US", gender="MALE"):

    try:
        language_code = language_code if language_code in LANGUAGE_VOICES else "en-US"
        voice_index = GENDER_INDICES.get(gender, 0)
        voice_name = LANGUAGE_VOICES[language_code][voice_index]
        
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0,
            volume_gain_db=0.0
        )

        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        return base64.b64encode(response.audio_content).decode('utf-8')
    
    except Exception as e:
        return f"Error: Text-to-speech conversion failed: {str(e)}"