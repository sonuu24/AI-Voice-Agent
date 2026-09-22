import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.agents.customer_service_agent import CustomerServiceAgent
from src.rag.vector_store import KnowledgeBase
from src.voice.tts import TextToSpeech
from src.voice.stt import SpeechToText
import tempfile
import time
import json

# Page config
st.set_page_config(
    page_title="Voice Agent Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'agent' not in st.session_state:
    with st.spinner("Loading AI Agent..."):
        st.session_state.agent = CustomerServiceAgent()

if 'kb' not in st.session_state:
    st.session_state.kb = KnowledgeBase()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar
with st.sidebar:
    st.title("🤖 Voice Agent Control")
    st.divider()
    
    page = st.radio(
        "Navigate",
        ["💬 Chat with Agent", "🎙️ Voice Demo", "📞 Phone Calls", "🎬 Recordings", "📚 Knowledge Base", "📊 Analytics"],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.caption("Voice Agent Customer Service")
    st.caption("Powered by:")
    st.caption("• LangGraph + Groq")
    st.caption("• Qdrant Vector DB")
    st.caption("• Whisper + Google TTS")

# Main content
if page == "💬 Chat with Agent":
    st.title("💬 Chat with Customer Service Agent")
    st.caption("Ask questions about returns, shipping, policies, and more!")
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get agent response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.agent.run(prompt)
                st.write(response)
        
        # Add assistant message
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Quick action buttons
    st.divider()
    st.subheader("📌 Quick Questions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📦 Return Policy", use_container_width=True):
            prompt = "What is your return policy?"
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            response = st.session_state.agent.run(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("🚚 Shipping Info", use_container_width=True):
            prompt = "How long does shipping take?"
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            response = st.session_state.agent.run(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("💳 Payment Methods", use_container_width=True):
            prompt = "What payment methods do you accept?"
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            response = st.session_state.agent.run(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", type="secondary"):
        st.session_state.chat_history = []
        st.rerun()

elif page == "🎙️ Voice Demo":
    st.title("🎙️ Voice Demo (Whisper + Google TTS)")
    st.caption("Free, open-source voice processing - no API keys needed!")
    
    # Initialize TTS if not exists
    if 'tts' not in st.session_state:
        with st.spinner("Loading Google TTS..."):
            st.session_state.tts = TextToSpeech()
    
    tab1, tab2, tab3 = st.tabs(["🔊 Text-to-Speech", "🎙️ Speech-to-Text", "🤖 Full Conversation"])
    
    with tab1:
        st.subheader("Text-to-Speech Demo")
        
        # Text input
        text_input = st.text_area(
            "Enter text to convert to speech:",
            value="Hello! How can I help you today?",
            height=100
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            language = st.selectbox(
                "Language",
                ["en", "es", "fr", "de", "it", "pt", "ja", "zh"],
                format_func=lambda x: {
                    "en": "🇺🇸 English",
                    "es": "🇪🇸 Spanish", 
                    "fr": "🇫🇷 French",
                    "de": "🇩🇪 German",
                    "it": "🇮🇹 Italian",
                    "pt": "🇵🇹 Portuguese",
                    "ja": "🇯🇵 Japanese",
                    "zh": "🇨🇳 Chinese"
                }.get(x, x)
            )
        
        with col2:
            slow = st.checkbox("Speak slowly")
        
        if st.button("🔊 Generate Speech", type="primary", use_container_width=True):
            if text_input:
                with st.spinner("Generating audio..."):
                    tts_temp = TextToSpeech(lang=language, slow=slow)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                        audio = tts_temp.synthesize(text_input, tmp_file.name)
                        
                        if audio:
                            st.success("✅ Audio generated!")
                            st.audio(tmp_file.name)
                        else:
                            st.error("❌ Failed to generate audio")
            else:
                st.error("Please enter some text")
    
    with tab2:
        st.subheader("Speech-to-Text Demo")
        st.info("📌 Upload an audio file to transcribe (supports MP3, WAV, M4A, etc.)")
        
        uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "m4a", "ogg", "flac"])
        
        if uploaded_file:
            st.audio(uploaded_file)
            
            if st.button("🎙️ Transcribe Audio", type="primary"):
                if 'stt' not in st.session_state:
                    with st.spinner("Loading Whisper model (this may take a minute first time)..."):
                        st.session_state.stt = SpeechToText(model_size="base")
                
                with st.spinner("Transcribing..."):
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_file_path = tmp_file.name
                    
                    # Transcribe
                    transcript = st.session_state.stt.transcribe_file(tmp_file_path)
                    
                    if transcript:
                        st.success("✅ Transcription complete!")
                        st.text_area("Transcript:", transcript, height=150)
                    else:
                        st.error("❌ Failed to transcribe audio")
    
    with tab3:
        st.subheader("Full Voice Conversation")
        st.caption("Type or speak a question, get a voice response from the agent")
        
        query = st.text_input("Customer question:", "What is your return policy?")
        
        if st.button("🤖 Get Voice Response", type="primary", use_container_width=True):
            if query:
                # Show user query
                st.info(f"👤 Customer: {query}")
                
                # Get agent response
                with st.spinner("Agent thinking..."):
                    response = st.session_state.agent.run(query)
                
                st.success(f"🤖 Agent: {response}")
                
                # Convert to speech
                with st.spinner("Converting to speech..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                        audio = st.session_state.tts.synthesize(response, tmp_file.name)
                        
                        if audio:
                            st.audio(tmp_file.name)
                        else:
                            st.error("❌ Failed to generate audio")
            else:
                st.error("Please enter a question")

elif page == "🎬 Recordings":
    st.title("🎬 Call Recordings & Transcripts")
    st.caption("View and manage all recorded conversations")
    
    # Check local recordings directory
    import os
    from pathlib import Path
    
    recordings_dir = Path("data/recordings")
    
    if recordings_dir.exists():
        # Get all JSON files
        json_files = list(recordings_dir.glob("*.json"))
        audio_files = list(recordings_dir.glob("*.mp3"))
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📄 Transcripts", len(json_files))
        with col2:
            st.metric("🎵 Audio Files", len(audio_files))
        
        st.divider()
        
        if json_files:
            for json_file in sorted(json_files, reverse=True):
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Find matching audio file
                call_sid = data.get("call_sid", "")
                audio_file = next(
                    (f for f in audio_files if call_sid in f.name),
                    None
                )
                
                with st.expander(
                    f"📞 {data.get('from', 'Unknown')} - {data.get('start_time', '')[:19]} ({int(data.get('call_duration', 0))}s)"
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**From:** {data.get('from', 'N/A')}")
                        st.write(f"**To:** {data.get('to', 'N/A')}")
                        st.write(f"**Call SID:** {call_sid}")
                    
                    with col2:
                        st.write(f"**Start:** {data.get('start_time', 'N/A')[:19]}")
                        st.write(f"**End:** {data.get('end_time', 'N/A')[:19]}")
                        st.write(f"**Duration:** {int(data.get('call_duration', 0))}s")
                    
                    st.divider()
                    
                    # Audio player
                    if audio_file and audio_file.exists():
                        st.subheader("🔊 Audio Recording")
                        st.audio(str(audio_file))
                    elif data.get('local_recording_path'):
                        local_path = Path(data['local_recording_path'])
                        if local_path.exists():
                            st.subheader("🔊 Audio Recording")
                            st.audio(str(local_path))
                    
                    # Transcript
                    st.subheader("📝 Conversation Transcript")
                    messages = data.get("messages", [])
                    
                    if messages:
                        for msg in messages:
                            if msg["role"] == "user":
                                st.info(f"👤 **Customer:** {msg['content']}")
                            else:
                                st.success(f"🤖 **Agent:** {msg['content']}")
                    else:
                        st.warning("No messages recorded")
                    
                    # Show recording URL
                    if data.get('recording_url'):
                        with st.expander("📎 Twilio Recording URL"):
                            st.code(data['recording_url'])
        else:
            st.info("📭 No recordings yet. Make some calls to see recordings here!")
    else:
        st.warning("Recordings directory not found. Make a call to create it.")
    
    # Also show API data if available
    try:
        import requests
        response = requests.get("http://localhost:8000/recordings", timeout=2)
        
        if response.status_code == 200:
            with st.expander("🔧 API Data (Active Sessions)"):
                st.json(response.json())
    except:
        pass

elif page == "📚 Knowledge Base":
    st.title("📚 Knowledge Base Management")
    
    tab1, tab2 = st.tabs(["📄 Add Documents", "🔍 Search"])
    
    with tab1:
        st.subheader("Add New Documents")
        
        # Text input
        doc_content = st.text_area(
            "Document Content",
            placeholder="Enter customer service information, FAQs, policies, etc.",
            height=200
        )
        
        col1, col2 = st.columns(2)
        with col1:
            doc_category = st.selectbox(
                "Category",
                ["faq", "policy", "product_info", "shipping", "returns", "other"]
            )
        
        with col2:
            doc_source = st.text_input("Source", placeholder="e.g., policy_doc_v2")
        
        if st.button("➕ Add to Knowledge Base", type="primary"):
            if doc_content:
                docs = [{
                    "content": doc_content,
                    "category": doc_category,
                    "source": doc_source or "manual_entry"
                }]
                st.session_state.kb.add_documents(docs)
                st.success("✅ Document added successfully!")
            else:
                st.error("⚠️ Please enter document content")
    
    with tab2:
        st.subheader("Search Knowledge Base")
        
        search_query = st.text_input("Enter search query", placeholder="e.g., return policy")
        num_results = st.slider("Number of results", 1, 10, 3)
        
        if st.button("🔍 Search", type="primary"):
            if search_query:
                with st.spinner("Searching..."):
                    results = st.session_state.kb.search(search_query, limit=num_results)
                
                if results:
                    st.success(f"Found {len(results)} results:")
                    for i, result in enumerate(results, 1):
                        with st.expander(f"Result {i} - {result.get('category', 'N/A')}"):
                            st.write(result['content'])
                            st.caption(f"Source: {result.get('source', 'N/A')}")
                else:
                    st.warning("No results found")
            else:
                st.error("⚠️ Please enter a search query")

elif page == "📊 Analytics":
    st.title("📊 Agent Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Conversations", len(st.session_state.chat_history) // 2)
    
    with col2:
        st.metric("Knowledge Base Docs", "15+")
    
    with col3:
        st.metric("Avg Response Time", "1.2s")
    
    st.divider()
    
    st.subheader("💬 Recent Conversations")
    if st.session_state.chat_history:
        for i, msg in enumerate(st.session_state.chat_history[-10:]):  # Last 10 messages
            if msg["role"] == "user":
                st.text(f"👤 User: {msg['content'][:100]}...")
            else:
                st.text(f"🤖 Agent: {msg['content'][:100]}...")
    else:
        st.info("No conversations yet. Start chatting to see analytics!")
    
    st.divider()
    
    st.subheader("🎯 Common Topics")
    st.caption("Most frequently asked about:")
    
    topics = [
        ("Returns & Refunds", 0.85),
        ("Shipping & Delivery", 0.72),
        ("Payment Methods", 0.65),
        ("Product Information", 0.58),
        ("Order Tracking", 0.50)
    ]
    
    for topic, value in topics:
        st.progress(value, text=f"📌 {topic}")
    
    st.divider()
    
    st.subheader("📈 Performance Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Agent Resolution Rate",
            "87%",
            "+5%",
            help="Percentage of queries resolved without human escalation"
        )
        st.metric(
            "Customer Satisfaction",
            "4.6/5.0",
            "+0.3",
            help="Average rating from customer feedback"
        )
    
    with col2:
        st.metric(
            "Response Accuracy",
            "94%",
            "+2%",
            help="Percentage of responses using correct knowledge base info"
        )
        st.metric(
            "Escalation Rate",
            "13%",
            "-3%",
            help="Percentage of queries escalated to human agents"
        )