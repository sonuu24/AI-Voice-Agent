import whisper
from typing import Optional
import os

class SpeechToText:
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper STT
        
        Model sizes:
        - tiny: Fastest, lowest accuracy (~1GB RAM)
        - base: Fast, good accuracy (~1GB RAM) ← RECOMMENDED
        - small: Balanced (~2GB RAM)
        - medium: Better quality (~5GB RAM)
        - large: Best quality (~10GB RAM)
        """
        print(f"🎙️ Loading Whisper model ({model_size})...")
        self.model = whisper.load_model(model_size)
        print(f"✅ Whisper model loaded!")
    
    def transcribe_file(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio file to text"""
        try:
            print(f"Transcribing: {audio_file_path}")
            result = self.model.transcribe(audio_file_path)
            transcript = result["text"].strip()
            print(f"✅ Transcription: {transcript}")
            return transcript
        except Exception as e:
            print(f"❌ STT Error: {e}")
            return None
    
    def transcribe_bytes(self, audio_bytes: bytes, temp_file: str = "temp_audio.wav") -> Optional[str]:
        """Transcribe audio bytes to text"""
        try:
            # Save bytes to temporary file
            with open(temp_file, "wb") as f:
                f.write(audio_bytes)
            
            # Transcribe
            result = self.model.transcribe(temp_file)
            transcript = result["text"].strip()
            
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            print(f"✅ Transcription: {transcript}")
            return transcript
        except Exception as e:
            print(f"❌ STT Error: {e}")
            return None
    
    def transcribe_with_details(self, audio_file_path: str) -> Optional[dict]:
        """Transcribe with language detection and timestamps"""
        try:
            result = self.model.transcribe(audio_file_path)
            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", [])
            }
        except Exception as e:
            print(f"❌ STT Error: {e}")
            return None