import io
from deepgram import DeepgramClient, PrerecordedOptions
    
deepgram = DeepgramClient()

LANGUAGE_MAPPING = {
    'en': 'en-US',    # English
    'ta': 'ta',       # Tamil
    'kn': 'kn',       # Kannada  
    'te': 'te',       # Telugu
    'ml': 'ml',       # Malayalam
    'hi': 'hi',       # Hindi
}

def deepgram_transcribe(audio_data, model="nova-2", language="en"):

    try:
        deepgram_language = 'en-US' if model.startswith('nova-') else LANGUAGE_MAPPING.get(language, 'en-US')
        
        options = PrerecordedOptions(
            model=model,
            smart_format=True,
            punctuate=True,
            language=deepgram_language
        )
            
        if hasattr(audio_data, 'seek'):
            audio_data.seek(0)
            
        audio_bytes = audio_data.getvalue() if isinstance(audio_data, io.BytesIO) else audio_data
        
        payload = {'buffer': audio_bytes}
        response = deepgram.listen.rest.v("1").transcribe_file(payload, options)
        
        return response.results.channels[0].alternatives[0].transcript
    
    except Exception as e:
        return f"Error: Deepgram transcription failed: {str(e)}"