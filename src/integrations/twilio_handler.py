import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Form, Response
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from src.agents.customer_service_agent import CustomerServiceAgent
from src.voice.tts import TextToSpeech
from src.voice.stt import SpeechToText
from config.settings import settings
from typing import Optional
from datetime import datetime
import json
from pathlib import Path
import requests

app = FastAPI(title="Voice Agent API")

# Initialize Twilio client
twilio_client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

# Initialize agent and voice components
agent = CustomerServiceAgent()
tts = TextToSpeech()

# Lazy load STT (Whisper is heavy - only load when needed)
stt = None

def get_stt():
    """Lazy load Speech-to-Text model"""
    global stt
    if stt is None:
        print("Loading Whisper STT model...")
        stt = SpeechToText(model_size="base")
    return stt

# Create recordings directory
RECORDINGS_DIR = Path("data/recordings")
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

# Store conversation state (in production, use Redis/database)
conversations = {}


def download_recording(recording_url: str, call_sid: str) -> Optional[str]:
    """Download recording from Twilio and save locally"""
    try:
        # Add .mp3 extension to get audio format
        audio_url = f"{recording_url}.mp3"
        
        # Download the recording with Twilio auth
        response = requests.get(
            audio_url,
            auth=(settings.twilio_account_sid, settings.twilio_auth_token)
        )
        
        if response.status_code == 200:
            # Save to local file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = RECORDINGS_DIR / f"{timestamp}_{call_sid}.mp3"
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"💾 Downloaded recording to: {filename}")
            return str(filename)
        else:
            print(f"❌ Failed to download recording: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error downloading recording: {e}")
        return None


def save_conversation(call_sid: str, conversation_data: dict):
    """Save conversation to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = RECORDINGS_DIR / f"{timestamp}_{call_sid}.json"
    
    with open(filename, 'w') as f:
        json.dump(conversation_data, f, indent=2)
    
    print(f"💾 Saved conversation to: {filename}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Voice Agent API",
        "version": "1.0.0"
    }


@app.post("/incoming-call", response_class=PlainTextResponse)
async def handle_incoming_call(
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...)
):
    """Handle incoming phone call with recording"""
    
    print(f"📞 Incoming call from {From} (CallSid: {CallSid})")
    
    # Initialize conversation
    conversations[CallSid] = {
        "call_sid": CallSid,
        "from": From,
        "to": To,
        "start_time": datetime.now().isoformat(),
        "messages": [],
        "status": "in_progress"
    }
    
    # Create TwiML response
    response = VoiceResponse()
    
    # Greeting
    response.say(
        "Hello! Thank you for calling. I'm your AI customer service assistant. How can I help you today?",
        voice="Polly.Joanna"
    )
    
    # Gather user input with recording enabled
    gather = Gather(
        input='speech',
        action='/process-speech',
        method='POST',
        speech_timeout='auto',
        language='en-US'
    )
    
    response.append(gather)
    
    # Fallback if no input
    response.say("I didn't hear anything. Please try calling again.", voice="Polly.Joanna")
    response.hangup()
    
    return str(response)


@app.post("/process-speech", response_class=PlainTextResponse)
async def process_speech(
    CallSid: str = Form(...),
    SpeechResult: Optional[str] = Form(None),
    From: str = Form(...)
):
    """Process the customer's speech input"""
    
    print(f"🎤 Speech from {From}: {SpeechResult}")
    
    response = VoiceResponse()
    
    if SpeechResult:
        # Store customer message
        if CallSid in conversations:
            conversations[CallSid]["messages"].append({
                "role": "user",
                "content": SpeechResult,
                "timestamp": datetime.now().isoformat()
            })
        
        # Get agent response
        try:
            agent_response = agent.run(SpeechResult)
            print(f"🤖 Agent response: {agent_response}")
            
            # Store agent response
            if CallSid in conversations:
                conversations[CallSid]["messages"].append({
                    "role": "assistant",
                    "content": agent_response,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Say the response
            response.say(agent_response, voice="Polly.Joanna")
            
            # Ask if they need more help
            gather = Gather(
                input='speech',
                action='/process-speech',
                method='POST',
                speech_timeout='auto',
                language='en-US'
            )
            gather.say("Is there anything else I can help you with?", voice="Polly.Joanna")
            response.append(gather)
            
            # Fallback
            response.say("Thank you for calling. Have a great day!", voice="Polly.Joanna")
            response.hangup()
            
        except Exception as e:
            print(f"❌ Error processing request: {e}")
            response.say(
                "I'm sorry, I'm having trouble processing your request. Please try again or speak with a human agent.",
                voice="Polly.Joanna"
            )
            response.hangup()
    else:
        response.say("I didn't catch that. Could you please repeat?", voice="Polly.Joanna")
        
        # Try again
        gather = Gather(
            input='speech',
            action='/process-speech',
            method='POST',
            speech_timeout='auto'
        )
        response.append(gather)
        response.hangup()
    
    return str(response)


@app.post("/handle-recording")
async def handle_recording(
    CallSid: str = Form(...),
    RecordingUrl: str = Form(...),
    RecordingDuration: str = Form(...)
):
    """Handle the recording after call ends and download it locally"""
    
    print(f"🎬 Recording available for {CallSid}")
    print(f"   URL: {RecordingUrl}")
    print(f"   Duration: {RecordingDuration} seconds")
    
    if CallSid in conversations:
        conversations[CallSid]["recording_url"] = RecordingUrl
        conversations[CallSid]["recording_duration"] = RecordingDuration
        
        # Download the recording locally
        local_path = download_recording(RecordingUrl, CallSid)
        if local_path:
            conversations[CallSid]["local_recording_path"] = local_path
    
    return {"status": "ok"}


@app.post("/call-status")
async def call_status(
    CallSid: str = Form(...),
    CallStatus: str = Form(...)
):
    """Handle call status updates"""
    
    print(f"📊 Call {CallSid} status: {CallStatus}")
    
    # Save conversation when call ends
    if CallStatus == "completed" and CallSid in conversations:
        conversations[CallSid]["status"] = "completed"
        conversations[CallSid]["end_time"] = datetime.now().isoformat()
        
        # Calculate duration
        start = datetime.fromisoformat(conversations[CallSid]["start_time"])
        end = datetime.fromisoformat(conversations[CallSid]["end_time"])
        duration = (end - start).total_seconds()
        conversations[CallSid]["call_duration"] = duration
        
        # Save to file
        save_conversation(CallSid, conversations[CallSid])
        
        # Clean up from memory
        print(f"💾 Saved and cleaned up conversation {CallSid}")
        del conversations[CallSid]
    
    return {"status": "ok"}


@app.get("/conversations")
async def get_conversations():
    """Get active conversations (for debugging)"""
    return {
        "active_conversations": len(conversations),
        "conversations": conversations
    }


@app.get("/recordings")
async def get_recordings():
    """Get all saved recordings"""
    recordings = []
    
    for file in RECORDINGS_DIR.glob("*.json"):
        with open(file, 'r') as f:
            data = json.load(f)
            recordings.append({
                "filename": file.name,
                "call_sid": data.get("call_sid"),
                "from": data.get("from"),
                "start_time": data.get("start_time"),
                "duration": data.get("call_duration"),
                "message_count": len(data.get("messages", []))
            })
    
    return {
        "total_recordings": len(recordings),
        "recordings": sorted(recordings, key=lambda x: x["start_time"], reverse=True)
    }


@app.get("/recordings/{call_sid}")
async def get_recording_detail(call_sid: str):
    """Get detailed recording transcript"""
    
    # Find the file
    matching_files = list(RECORDINGS_DIR.glob(f"*_{call_sid}.json"))
    
    if not matching_files:
        return {"error": "Recording not found"}
    
    with open(matching_files[0], 'r') as f:
        data = json.load(f)
    
    # Generate formatted transcript
    transcript = []
    for msg in data.get("messages", []):
        role = "Customer" if msg["role"] == "user" else "Agent"
        transcript.append(f"{role}: {msg['content']}")
    
    return {
        "call_details": {
            "call_sid": data.get("call_sid"),
            "from": data.get("from"),
            "to": data.get("to"),
            "start_time": data.get("start_time"),
            "end_time": data.get("end_time"),
            "duration": data.get("call_duration"),
            "recording_url": data.get("recording_url")
        },
        "transcript": transcript,
        "messages": data.get("messages", [])
    }


@app.post("/make-outbound-call")
async def make_outbound_call(to_number: str, message: str):
    """Make an outbound call (for testing)"""
    
    try:
        call = twilio_client.calls.create(
            twiml=f'<Response><Say voice="Polly.Joanna">{message}</Say></Response>',
            to=to_number,
            from_=settings.twilio_phone_number,
            record=True  # Enable recording
        )
        
        return {
            "status": "success",
            "call_sid": call.sid,
            "to": to_number
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)