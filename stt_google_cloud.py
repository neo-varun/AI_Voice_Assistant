import io
from google.cloud import speech

speech_client = speech.SpeechClient()

LANGUAGE_MAPPING = {
    'en': 'en-IN',    # English (India)
    'ta': 'ta-IN',    # Tamil (India)
    'kn': 'kn-IN',    # Kannada (India)
    'te': 'te-IN',    # Telugu (India)
    'ml': 'ml-IN',    # Malayalam (India)
    'hi': 'hi-IN',    # Hindi (India)
}

def google_cloud_transcribe(audio_data, language="en"):
    
    try:
        google_language = LANGUAGE_MAPPING.get(language, 'en-IN')
        
        if hasattr(audio_data, 'seek'):
            audio_data.seek(0)
            audio_bytes = audio_data.getvalue() if isinstance(audio_data, io.BytesIO) else audio_data
        else:
            audio_bytes = audio_data
        
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            language_code=google_language,
            enable_automatic_punctuation=True,
            sample_rate_hertz=48000,
        )
        
        response = speech_client.recognize(
            config=config, 
            audio=speech.RecognitionAudio(content=audio_bytes)
        )
        
        transcripts = [result.alternatives[0].transcript for result in response.results]
        full_transcript = " ".join(transcripts)
        
        return full_transcript
    
    except Exception as e:
        return f"Error: Google Cloud transcription failed: {str(e)}" 