import os
import base64
import tempfile
import logging
from gtts import gTTS

def text_to_speech(text):
    """
    Convert text to speech using gTTS.
    
    Args:
        text (str): Text to be converted to speech
        
    Returns:
        str: Base64 encoded audio data
    """
    try:
        # Create a temporary file to save the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
            temp_audio_path = temp_audio.name
        
        # Convert text to speech
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(temp_audio_path)
        
        # Read the audio file and encode it as base64
        with open(temp_audio_path, 'rb') as audio_file:
            audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
        
        # Clean up the temporary file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        
        return audio_data
    
    except Exception as e:
        logging.error(f"Error in text_to_speech: {str(e)}")
        # Clean up the temporary file if it exists
        if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        raise
