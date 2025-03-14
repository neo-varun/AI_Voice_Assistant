import os
import logging
from deepgram import DeepgramClient, PrerecordedOptions
import io
import binascii
import tempfile

# Initialize the Deepgram SDK with API key
DEEPGRAM_API_KEY = os.environ.get('DEEPGRAM_API_KEY', '')

# Add a placeholder API key for testing - REPLACE THIS WITH YOUR ACTUAL KEY
if not DEEPGRAM_API_KEY:
    logging.error("Deepgram API key is missing from environment variables. Using placeholder for testing.")
    DEEPGRAM_API_KEY = "INSERT_YOUR_DEEPGRAM_API_KEY_HERE"
    
# Initialize Deepgram client
deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)

# Map of language codes to Deepgram language codes
LANGUAGE_MAPPING = {
    'en': 'en-US',    # English
    'ta': 'ta',       # Tamil
    'kn': 'kn',       # Kannada  
    'te': 'te',       # Telugu
    'ml': 'ml',       # Malayalam
    'hi': 'hi',       # Hindi
}

def inspect_audio_data(audio_data):
    """
    Helper function to inspect audio data and log details.
    """
    try:
        # Get size information
        if hasattr(audio_data, 'getbuffer'):
            size = len(audio_data.getbuffer())
        elif hasattr(audio_data, 'getvalue'):
            size = len(audio_data.getvalue())
        elif isinstance(audio_data, bytes):
            size = len(audio_data)
        else:
            size = 'unknown'
            
        logging.info(f"Audio data inspection - Size: {size} bytes")
        
        # If we have byte data, inspect the first few bytes for format identification
        sample_bytes = None
        if hasattr(audio_data, 'getvalue'):
            if audio_data.getvalue():
                sample_bytes = audio_data.getvalue()[:16]
        elif isinstance(audio_data, bytes):
            sample_bytes = audio_data[:16]
            
        if sample_bytes:
            hex_sample = binascii.hexlify(sample_bytes).decode('utf-8')
            logging.info(f"Audio data first 16 bytes: {hex_sample}")
            
            # Try to identify format based on magic numbers
            if hex_sample.startswith('1a45dfa3'):
                logging.info("Audio format appears to be WebM")
            elif hex_sample.startswith('52494646'):  # 'RIFF'
                logging.info("Audio format appears to be WAV")
            elif hex_sample.startswith('494433'):  # 'ID3'
                logging.info("Audio format appears to be MP3 with ID3 tag")
            elif hex_sample.startswith('fffb') or hex_sample.startswith('fff3'):
                logging.info("Audio format appears to be MP3")
            else:
                logging.info("Audio format could not be identified from header")
        
        return True
    except Exception as e:
        logging.error(f"Error inspecting audio data: {str(e)}")
        return False

def transcribe_audio(audio_data, model="nova-2", language="en"):
    """
    Transcribe audio using Deepgram API with specified model and language.
    
    Args:
        audio_data: Audio data bytes or file-like object
        model: Deepgram model to use (nova-2, nova-3, whisper-*)
        language: Language code for transcription (en, ta, kn, te, ml, hi)
    
    Returns:
        str: Transcribed text or error message
    """
    try:
        # Check if API key is available
        if not DEEPGRAM_API_KEY or DEEPGRAM_API_KEY == "INSERT_YOUR_DEEPGRAM_API_KEY_HERE":
            return "Error: Deepgram API key is missing or using placeholder. Please set a valid API key."
            
        logging.info(f"Transcribing audio with {model} model, language: {language}")
        
        # Map the language code to Deepgram expected format if needed
        deepgram_language = LANGUAGE_MAPPING.get(language, 'en-US')
        
        # For Nova models, which only support English
        if model.startswith('nova-') and language != 'en':
            logging.warning(f"Nova models only support English. Forcing language to en-US.")
            deepgram_language = 'en-US'
            
        # Create options for the transcription
        options = PrerecordedOptions(
            model=model,
            smart_format=True,
            punctuate=True,
            language=deepgram_language
        )
            
        # Ensure we have valid audio data
        if audio_data is None:
            return "Error: No audio data provided"
            
        # Inspect audio data for troubleshooting
        logging.info("Inspecting audio data before transcription")
        inspect_audio_data(audio_data)
            
        # Reset audio_data position if it's a file-like object
        if hasattr(audio_data, 'seek'):
            audio_data.seek(0)
            
        # Convert to bytes if needed
        if isinstance(audio_data, io.BytesIO):
            audio_bytes = audio_data.getvalue()
        else:
            # If it's already bytes or another format
            audio_bytes = audio_data
            
        # Try a different approach - save to temp file and use that
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
            try:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
                
                logging.info(f"Audio saved to temporary file: {temp_file_path}")
                
                # Close file before opening in Deepgram
                temp_file.close()
                
                try:
                    logging.info(f"Attempting to transcribe from file using any format")
                    with open(temp_file_path, 'rb') as audio_file:
                        response = deepgram.transcription.prerecorded.transcribe_file(
                            audio_file,
                            options=options
                        )
                    logging.info("Successfully transcribed from file")
                except Exception as file_error:
                    logging.error(f"Failed to transcribe from file: {str(file_error)}")
                    
                    # If file transcription fails, fall back to the original buffer method
                    logging.info("Falling back to buffer transcription method")
                    try:
                        # Try all MIME types
                        for mime_type in ["audio/webm", "audio/wav", "audio/mpeg", "audio/ogg"]:
                            try:
                                logging.info(f"Trying with MIME type: {mime_type}")
                                response = deepgram.transcription.prerecorded.transcribe_buffer(
                                    buffer=audio_bytes,
                                    mimetype=mime_type,
                                    options=options
                                )
                                logging.info(f"Successfully transcribed with {mime_type}")
                                break
                            except Exception as mime_error:
                                logging.error(f"Failed with {mime_type}: {str(mime_error)}")
                        else:
                            # If all MIME types fail, raise exception
                            raise Exception("Failed to transcribe with any MIME type")
                    except Exception as buffer_error:
                        raise Exception(f"Both file and buffer transcription methods failed: {str(buffer_error)}")
            finally:
                # Clean up - remove the temp file
                try:
                    os.unlink(temp_file_path)
                    logging.info(f"Temporary file {temp_file_path} deleted")
                except Exception as e:
                    logging.warning(f"Could not delete temporary file {temp_file_path}: {str(e)}")

        # Check if response is None or empty
        if not response:
            return "Error: No response from Deepgram API"
            
        # Extract the transcript (with updated response format)
        if hasattr(response, 'results'):
            results = response.results
            if hasattr(results, 'channels') and results.channels:
                channels = results.channels
                if channels and len(channels) > 0:
                    alternatives = channels[0].alternatives
                    if alternatives and len(alternatives) > 0:
                        transcript_result = alternatives[0].transcript
                        
                        if transcript_result:
                            logging.info(f"Transcription successful: {transcript_result[:50]}...")
                            return transcript_result
                        else:
                            return "Error: No speech detected in the audio"
                    else:
                        return "Error: No transcription alternatives returned"
                else:
                    return "Error: No channels in transcription result"
            else:
                return "Error: Unexpected API response format from Deepgram"
        else:
            # Different response format - try to navigate it differently
            logging.info(f"Different response format detected: {type(response)}")
            try:
                # Try extracting the transcript using the new format
                transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
                if transcript:
                    return transcript
                else:
                    return "Error: Empty transcript returned"
            except (KeyError, IndexError) as e:
                logging.error(f"Failed to extract transcript from response: {str(e)}")
                return "Error: Could not extract transcript from Deepgram response"
            
    except Exception as e:
        error_msg = f"Error transcribing audio: {str(e)}"
        logging.error(error_msg)
        
        # Special handling for specific errors
        if str(e) == "0":
            logging.error("Deepgram '0' error detected. This usually means empty audio or format issues.")
            return "Error: Empty or too short audio recording. Please try speaking louder or longer."
            
        if "failed to decode" in str(e).lower():
            return "Error: Audio format not supported. Please try a different browser or microphone setup."
            
        if "too large" in str(e).lower():
            return "Error: Audio file too large for processing."
            
        return error_msg