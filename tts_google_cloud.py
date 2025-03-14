import base64
import logging
from google.cloud import texttospeech

logging.basicConfig(level=logging.INFO)

# Initialize the Text-to-Speech client
try:
    tts_client = texttospeech.TextToSpeechClient()
    logging.info("Google Cloud TTS client initialized successfully")
except Exception as e:
    error_msg = f"Error initializing Google TTS client: {str(e)}"
    logging.error(error_msg)
    tts_client = None

# Define available voices for each language using specific Google Cloud voices
# Each language has exactly one male and one female voice selected from Google Cloud documentation
LANGUAGE_VOICES = {
    'en-US': ['en-US-Chirp3-HD-Orus', 'en-US-Chirp3-HD-Aoede'],  # Male (O), Female (M)
    'ta-IN': ['ta-IN-Chirp3-HD-Puck', 'ta-IN-Chirp3-HD-Aoede'],  # Male (B), Female (A)
    'kn-IN': ['kn-IN-Chirp3-HD-Fenrir', 'kn-IN-Chirp3-HD-Leda'],  # Male (A), Female (Standard-A)
    'te-IN': ['te-IN-Chirp3-HD-Orus', 'te-IN-Chirp3-HD-Leda'],  # Male (B), Female (A)
    'ml-IN': ['ml-IN-Chirp3-HD-Orus', 'ml-IN-Chirp3-HD-Aoede'],  # Male (B), Female (A)
    'hi-IN': ['hi-IN-Chirp3-HD-Fenrir', 'hi-IN-Chirp3-HD-Aoede'],  # Male (B), Female (A)
}

# Map gender to indexes in the voice arrays
GENDER_INDICES = {
    'MALE': 0,
    'FEMALE': 1
}

def select_voice_by_gender(language_code, gender):
    """
    Select an appropriate voice based on language and gender preference.
    
    Args:
        language_code (str): Language code in format 'en-US'
        gender (str): Preferred gender - 'MALE' or 'FEMALE'
    
    Returns:
        str: Voice name that matches the criteria
    """
    if not language_code:
        logging.warning("Empty language code provided. Falling back to en-US.")
        language_code = 'en-US'
        
    if language_code not in LANGUAGE_VOICES:
        logging.warning(f"Language '{language_code}' not supported. Falling back to en-US.")
        language_code = 'en-US'
    
    # Get available voices for the language
    available_voices = LANGUAGE_VOICES[language_code]
    
    # Select voice based on gender
    if gender in GENDER_INDICES:
        return available_voices[GENDER_INDICES[gender]]
    else:
        # Default to male voice if gender not recognized
        logging.warning(f"Gender '{gender}' not supported. Falling back to MALE.")
        return available_voices[GENDER_INDICES['MALE']]

def text_to_speech(text, language_code="en-US", gender="MALE"):
    """
    Convert text to speech using Google Cloud Text-to-Speech API.
    
    Args:
        text (str): The text to convert to speech
        language_code (str): Language code for the voice (e.g., 'en-US', 'ta-IN')
        gender (str): Voice gender preference ('MALE' or 'FEMALE')
    
    Returns:
        str: Base64-encoded audio content or error message
    """
    try:
        # Input validation
        if not text or text.strip() == "":
            return "Error: Empty text provided for speech synthesis"
            
        if not tts_client:
            return "Error: Google TTS client not initialized. Check your Google Cloud credentials."
        
        logging.info(f"Converting text to speech with language: {language_code}, gender: {gender}")
        
        # Select voice based on language and gender
        voice_name = select_voice_by_gender(language_code, gender)
        logging.info(f"Selected voice: {voice_name} for language: {language_code}, gender: {gender}")
        
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Configure the voice
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name
        )

        # Select the audio file type and high-quality settings
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,  # Normal speed
            pitch=0.0,  # Default pitch
            volume_gain_db=0.0  # Default volume
        )

        # Perform the text-to-speech request 
        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        # Check if response has audio content
        if not response or not response.audio_content:
            return "Error: No audio content received from Google TTS"

        # Convert binary audio content to base64 for web playback
        audio_content_b64 = base64.b64encode(response.audio_content).decode('utf-8')
        
        if not audio_content_b64:
            return "Error: Failed to encode audio content"
            
        # Return the base64 encoded audio
        return audio_content_b64
        
    except Exception as e:
        error_msg = f"Error generating speech: {str(e)}"
        logging.error(error_msg)
        
        # Special case handling for common errors
        if "Voice " in str(e) and " not found" in str(e):
            return "Error: Selected voice is not available. Please try a different language or gender."
        
        if "Invalid recognition result" in str(e):
            return "Error: Invalid text content for speech synthesis."
            
        if "Exceeds maximum character limit" in str(e):
            return "Error: Text is too long for speech synthesis. Please use shorter text."
        
        return error_msg