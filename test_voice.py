import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.voice.tts import TextToSpeech
from src.voice.stt import SpeechToText
from src.agents.customer_service_agent import CustomerServiceAgent

def test_tts():
    """Test Text-to-Speech"""
    print("\n" + "="*60)
    print("🔊 Testing Text-to-Speech (Google TTS)")
    print("="*60 + "\n")
    
    tts = TextToSpeech()
    
    text = "Hello! Welcome to our customer service. How can I help you today?"
    output_file = "test_output.mp3"
    
    print(f"📝 Text: '{text}'")
    audio = tts.synthesize(text, output_file)
    
    if audio:
        print(f"✅ Success! Audio saved to: {output_file}")
        print(f"📊 Audio size: {len(audio):,} bytes")
        print(f"▶️  Play the file to hear the output!")
    else:
        print("❌ Failed to generate audio")

def test_stt():
    """Test Speech-to-Text"""
    print("\n" + "="*60)
    print("🎙️ Testing Speech-to-Text (Whisper)")
    print("="*60 + "\n")
    
    stt = SpeechToText(model_size="base")
    
    # Check if test audio exists
    test_file = "test_output.mp3"
    if os.path.exists(test_file):
        print(f"📂 Transcribing: {test_file}")
        transcript = stt.transcribe_file(test_file)
        
        if transcript:
            print(f"\n✅ Transcription successful!")
            print(f"📝 Text: '{transcript}'")
        else:
            print("❌ Failed to transcribe")
    else:
        print(f"⚠️  Audio file not found: {test_file}")
        print("   Run test_tts() first to generate audio")

def test_full_conversation():
    """Test full voice conversation flow"""
    print("\n" + "="*60)
    print("🎙️ Testing Full Voice Conversation Flow")
    print("="*60 + "\n")
    
    # Initialize components
    agent = CustomerServiceAgent()
    tts = TextToSpeech()
    
    # Simulate customer query
    customer_query = "What is your return policy?"
    print(f"👤 Customer Query: {customer_query}")
    
    # Get agent response
    print("\n🤖 Agent processing...")
    response = agent.run(customer_query)
    print(f"🤖 Agent Response: {response}\n")
    
    # Convert response to speech
    print("🔊 Converting response to speech...")
    audio = tts.synthesize(response, "agent_response.mp3")
    
    if audio:
        print(f"✅ Voice response saved to: agent_response.mp3")
        print(f"📊 Audio size: {len(audio):,} bytes")
        print(f"▶️  Play this file to hear the agent's response!")
    else:
        print("❌ Failed to generate voice response")

def test_multilingual():
    """Test multiple languages"""
    print("\n" + "="*60)
    print("🌍 Testing Multiple Languages")
    print("="*60 + "\n")
    
    tests = [
        ("en", "Hello, how can I help you?"),
        ("es", "Hola, ¿cómo puedo ayudarte?"),
        ("fr", "Bonjour, comment puis-je vous aider?"),
        ("de", "Hallo, wie kann ich Ihnen helfen?")
    ]
    
    for lang, text in tests:
        print(f"\n🌐 Language: {lang}")
        print(f"📝 Text: {text}")
        
        tts = TextToSpeech(lang=lang)
        output = f"test_{lang}.mp3"
        audio = tts.synthesize(text, output)
        
        if audio:
            print(f"✅ Generated: {output}")
        else:
            print(f"❌ Failed: {lang}")

def main():
    print("\n" + "="*70)
    print("🎙️  VOICE AGENT TESTING SUITE (Whisper + Google TTS)")
    print("="*70)
    
    # Test TTS first
    test_tts()
    
    # Test STT (transcribe the TTS output)
    test_stt()
    
    # Test full conversation
    test_full_conversation()
    
    # Test multilingual (optional - uncomment to test)
    # test_multilingual()
    
    print("\n" + "="*70)
    print("✅ Testing Complete!")
    print("="*70)
    print("\n📂 Generated files:")
    print("   - test_output.mp3 (TTS test)")
    print("   - agent_response.mp3 (Full conversation)")
    print("\n▶️  Play these files to hear the results!\n")

if __name__ == "__main__":
    main()