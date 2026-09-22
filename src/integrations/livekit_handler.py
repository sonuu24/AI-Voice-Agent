from livekit import rtc, api
from src.voice.stt import SpeechToText
from src.voice.tts import TextToSpeech
from src.agents.customer_service_agent import CustomerServiceAgent
import asyncio

class LiveKitVoiceHandler:
    def __init__(self):
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.agent = CustomerServiceAgent()
        self.room = None
    
    async def handle_call(self, room_name: str):
        """Handle incoming voice call"""
        # Connect to LiveKit room
        self.room = rtc.Room()
        
        # Set up callbacks
        self.room.on("track_subscribed", self.on_track_subscribed)
        
        # Connect
        await self.room.connect(
            settings.livekit_url,
            api.AccessToken()
                .with_identity("voice-agent")
                .with_name("Customer Service Agent")
                .with_grants(api.VideoGrants(
                    room_join=True,
                    room=room_name,
                ))
                .to_jwt()
        )
    
    async def on_track_subscribed(
        self,
        track: rtc.Track,
        publication: rtc.TrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        """Handle incoming audio track"""
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            audio_stream = rtc.AudioStream(track)
            
            async for frame in audio_stream:
                # Convert audio frame to bytes
                audio_data = frame.data.tobytes()
                
                # Transcribe
                transcript = await self.stt.transcribe_audio(audio_data)
                
                if transcript:
                    print(f"User said: {transcript}")
                    
                    # Get agent response
                    response = self.agent.run(transcript)
                    print(f"Agent responds: {response}")
                    
                    # Convert to speech
                    audio_response = self.tts.synthesize(response)
                    
                    # Stream back to room
                    if audio_response:
                        await self.publish_audio(audio_response)
    
    async def publish_audio(self, audio_data: bytes):
        """Publish audio response to room"""
        # Create audio track and publish
        source = rtc.AudioSource(24000, 1)
        track = rtc.LocalAudioTrack.create_audio_track("agent-voice", source)
        
        await self.room.local_participant.publish_track(track)
        await source.capture_frame(audio_data)