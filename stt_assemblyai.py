import io
import os
import assemblyai as aai

aai.settings.api_key = os.environ.get("ASSEMBLY_API_KEY")

LANGUAGE_MAPPING = {
    'en': 'en_us',    # English (US)
    'ta': 'ta_in',    # Tamil (India)
    'kn': 'kn_in',    # Kannada (India)
    'te': 'te_in',    # Telugu (India)
    'ml': 'ml_in',    # Malayalam (India)
    'hi': 'hi_in',    # Hindi (India)
}

def assemblyai_transcribe(audio_data, model="best", language="en"):
    
    try:
        assemblyai_language = LANGUAGE_MAPPING.get(language, 'en_us')
        
        speech_model = aai.SpeechModel.best if model == "best" else aai.SpeechModel.nano
        
        config = aai.TranscriptionConfig(
            language_code=assemblyai_language,
            punctuate=True,
            format_text=True,
            speech_model=speech_model
        )
        
        transcriber = aai.Transcriber(config=config)
        
        if hasattr(audio_data, 'seek'):
            audio_data.seek(0)
            audio_bytes = audio_data.getvalue() if isinstance(audio_data, io.BytesIO) else audio_data
        else:
            audio_bytes = audio_data
            
        transcript = transcriber.transcribe(audio_bytes)
        
        return transcript.text
    
    except Exception as e:
        return f"Error: AssemblyAI transcription failed: {str(e)}" 