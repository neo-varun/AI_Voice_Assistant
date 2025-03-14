import os
from io import BytesIO
from deepgram import DeepgramClient, PrerecordedOptions

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)

def transcribe_audio(audio_bytes: BytesIO) -> str:
    
    try:
        options = PrerecordedOptions(
            model="whisper-large",  # Change to Deepgram's other models if needed
            language='en',  # Tamil: 'ta-IN', English: 'en-US'
            smart_format=True,
            punctuate=True,
        )

        audio_bytes.seek(0)

        response = deepgram.listen.prerecorded.v("1").transcribe_file(
            {"buffer": audio_bytes, "mimetype": "audio/wav"},
            options
        )

        transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
        return transcript if transcript else "No speech detected."

    except Exception as e:
        return f"Error in Deepgram STT: {str(e)}"