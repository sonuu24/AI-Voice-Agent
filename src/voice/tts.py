from gtts import gTTS
from typing import Optional
import os

class TextToSpeech:
    def __init__(self, lang: str = "en", slow: bool = False):
        """
        Initialize Google TTS
        
        Args:
            lang: Language code (en, es, fr, de, etc.)
            slow: Speak slowly (useful for learning)
        """
        self.lang = lang
        self.slow = slow
        print(f"🔊 Google TTS initialized (lang: {lang})")
    
    def synthesize(self, text: str, output_path: str = None) -> Optional[bytes]:
        """Convert text to speech audio"""
        try:
            print(f"🔊 Synthesizing: {text[:50]}...")
            
            # Generate speech
            tts = gTTS(text=text, lang=self.lang, slow=self.slow)
            
            # Save to file or return bytes
            if output_path:
                tts.save(output_path)
                print(f"✅ Audio saved to: {output_path}")
                
                # Also read as bytes
                with open(output_path, "rb") as f:
                    audio_bytes = f.read()
                return audio_bytes
            else:
                # Save to temp file and read
                temp_file = "temp_tts.mp3"
                tts.save(temp_file)
                with open(temp_file, "rb") as f:
                    audio_bytes = f.read()
                os.remove(temp_file)
                return audio_bytes
                
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return None
    
    def synthesize_with_options(self, text: str, output_path: str, lang: str = None, slow: bool = None):
        """Synthesize with custom options"""
        try:
            lang = lang or self.lang
            slow = slow if slow is not None else self.slow
            
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(output_path)
            print(f"✅ Audio saved to: {output_path}")
            return True
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return False
    
    @staticmethod
    def get_available_languages():
        """Get list of supported languages"""
        from gtts.lang import tts_langs
        return tts_langs()