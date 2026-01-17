"""
JARVIS AI Assistant - Streamlit Frontend
Beautiful interactive interface for JARVIS
"""

import streamlit as st
import threading
import time
import asyncio
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd

# Import the AI Core
from main import AI_Core
from memory import get_all_memories, get_relevant_memories
from handlers.pdf_handler import PDFHandler

# Page configuration
st.set_page_config(
    page_title="J.A.R.V.I.S. AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #00d4ff;
        --secondary-color: #0066cc;
        --bg-dark: #0a0e27;
        --bg-card: #1a1f3a;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: #e0e0e0;
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    /* Card styling */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .stat-card h3 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .stat-card p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Chat message styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .jarvis-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Feature card */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .feature-card h4 {
        color: #667eea;
        margin-top: 0;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.2);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Status indicators */
    .status-active {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #00ff00;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .status-inactive {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #ff0000;
        border-radius: 50%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'ai_core' not in st.session_state:
    st.session_state.ai_core = None
    st.session_state.ai_thread = None
    st.session_state.is_running = False
    st.session_state.chat_history = []
    st.session_state.system_stats = {
        'messages_sent': 0,
        'commands_executed': 0,
        'uptime': 0,
        'memories_stored': 0
    }

def get_base64_image(image_path):
    """Convert image to base64 for embedding"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def start_jarvis(video_mode="none"):
    """Start JARVIS AI Core"""
    if not st.session_state.is_running:
        st.session_state.ai_core = AI_Core(video_mode=video_mode)
        st.session_state.ai_thread = threading.Thread(
            target=st.session_state.ai_core.start_event_loop
        )
        st.session_state.ai_thread.daemon = True
        st.session_state.ai_thread.start()
        st.session_state.is_running = True
        st.session_state.system_stats['uptime'] = time.time()
        return True
    return False

def stop_jarvis():
    """Stop JARVIS AI Core"""
    if st.session_state.is_running and st.session_state.ai_core:
        st.session_state.ai_core.stop()
        st.session_state.is_running = False
        return True
    return False

def send_message(message):
    """Send message to JARVIS"""
    if st.session_state.is_running and st.session_state.ai_core:
        st.session_state.ai_core.handle_user_text(message)
        st.session_state.chat_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now()
        })
        st.session_state.system_stats['messages_sent'] += 1
        return True
    return False

# Main App
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 J.A.R.V.I.S. AI Assistant</h1>
        <p>Just A Rather Very Intelligent System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Control Panel")
        
        # System Status
        st.subheader("System Status")
        status_icon = "🟢" if st.session_state.is_running else "🔴"
        status_text = "Active" if st.session_state.is_running else "Inactive"
        st.markdown(f"{status_icon} **Status:** {status_text}")
        
        if st.session_state.is_running:
            uptime = time.time() - st.session_state.system_stats['uptime']
            st.metric("Uptime", f"{int(uptime)} seconds")
        
        st.divider()
        
        # Control Buttons
        st.subheader("🎮 Controls")
        
        video_mode = st.selectbox(
            "Video Mode",
            ["none", "camera", "screen"],
            help="Select video input source"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ Start", use_container_width=True):
                if start_jarvis(video_mode):
                    st.success("JARVIS started!")
                    st.rerun()
                else:
                    st.error("JARVIS is already running")
        
        with col2:
            if st.button("⏹️ Stop", use_container_width=True):
                if stop_jarvis():
                    st.success("JARVIS stopped!")
                    st.rerun()
                else:
                    st.error("JARVIS is not running")
        
        st.divider()
        
        # Statistics
        st.subheader("📊 Statistics")
        st.metric("Messages Sent", st.session_state.system_stats['messages_sent'])
        st.metric("Commands Executed", st.session_state.system_stats['commands_executed'])
        
        st.divider()
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("📁 Open File Manager", use_container_width=True):
            send_message("open file explorer")
        
        if st.button("🌐 Open Browser", use_container_width=True):
            send_message("open chrome")
        
        if st.button("📧 Check Email", use_container_width=True):
            send_message("read my emails")
        
        if st.button("🌤️ Get Weather", use_container_width=True):
            send_message("what's the weather today")
        
        st.divider()
        
        # Memory Management
        st.subheader("🧠 Memory")
        
        if st.button("View Memories", use_container_width=True):
            memories = get_all_memories(st.session_state.ai_core.user_id if st.session_state.ai_core else "Barrack")
            if memories:
                st.text_area("Stored Memories", memories, height=200)
            else:
                st.info("No memories stored yet")
        
        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
            st.rerun()
    
    # Main Content Area
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 Chat", 
        "📊 Dashboard", 
        "📚 Features", 
        "📄 PDF Reader",
        "⚙️ Settings"
    ])
    
    # Chat Tab
    with tab1:
        st.header("💬 Chat with JARVIS")
        
        # Chat container
        chat_container = st.container(height=400)
        
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="user-message">
                        <strong>You:</strong> {message['content']}
                        <br><small>{message['timestamp'].strftime('%H:%M:%S')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="jarvis-message">
                        <strong>JARVIS:</strong> {message['content']}
                        <br><small>{message['timestamp'].strftime('%H:%M:%S')}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Message input
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Type your message here...",
                label_visibility="collapsed",
                key="user_input"
            )
        
        with col2:
            send_btn = st.button("Send", use_container_width=True)
        
        if send_btn and user_input:
            if send_message(user_input):
                st.rerun()
            else:
                st.error("JARVIS is not running. Please start it first.")
        
        # Voice input placeholder
        st.info("🎤 Voice input coming soon!")
    
    # Dashboard Tab
    with tab2:
        st.header("📊 System Dashboard")
        
        # Stats row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="stat-card">
                <h3>""" + str(st.session_state.system_stats['messages_sent']) + """</h3>
                <p>Messages Sent</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stat-card">
                <h3>""" + str(st.session_state.system_stats['commands_executed']) + """</h3>
                <p>Commands Executed</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            uptime = int(time.time() - st.session_state.system_stats['uptime']) if st.session_state.is_running else 0
            st.markdown("""
            <div class="stat-card">
                <h3>""" + str(uptime) + """s</h3>
                <p>Uptime</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="stat-card">
                <h3>""" + str(len(st.session_state.chat_history)) + """</h3>
                <p>Total Messages</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Activity Chart
        st.subheader("📈 Activity Over Time")
        
        if st.session_state.chat_history:
            df = pd.DataFrame([
                {
                    'time': msg['timestamp'].strftime('%H:%M:%S'),
                    'messages': 1
                }
                for msg in st.session_state.chat_history
            ])
            
            fig = px.line(
                df.groupby('time').sum().reset_index(),
                x='time',
                y='messages',
                title='Messages Over Time'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No activity data yet. Start chatting with JARVIS!")
    
    # Features Tab
    with tab3:
        st.header("📚 JARVIS Capabilities")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h4>📁 File Management</h4>
                <ul>
                    <li>Create, edit, and organize files</li>
                    <li>Search and manage directories</li>
                    <li>Archive and compress files</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card">
                <h4>💻 System Control</h4>
                <ul>
                    <li>Control volume and brightness</li>
                    <li>Manage applications</li>
                    <li>System diagnostics</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card">
                <h4>📧 Communication</h4>
                <ul>
                    <li>Send and read emails</li>
                    <li>WhatsApp messaging</li>
                    <li>Clipboard operations</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h4>🤖 Automation</h4>
                <ul>
                    <li>Mouse and keyboard control</li>
                    <li>Screen capture and automation</li>
                    <li>Web automation</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card">
                <h4>🔧 Advanced Features</h4>
                <ul>
                    <li>Code analysis and debugging</li>
                    <li>GitHub integration</li>
                    <li>Package management</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card">
                <h4>🌐 Web & Info</h4>
                <ul>
                    <li>Weather updates</li>
                    <li>News briefings</li>
                    <li>Web scraping</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # PDF Reader Tab
    with tab4:
        st.header("📄 PDF Document Reader")
        
        uploaded_file = st.file_uploader(
            "Upload a PDF file",
            type=['pdf'],
            help="Upload a PDF document for JARVIS to read and analyze"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"✅ Uploaded: {uploaded_file.name}")
            
            # Extract text
            pdf_handler = PDFHandler()
            result = pdf_handler.extract_pdf_text(temp_path)
            
            if result['status'] == 'success':
                st.subheader("📖 Extracted Content")
                st.text_area(
                    "PDF Content",
                    result['text'],
                    height=300,
                    label_visibility="collapsed"
                )
                
                # Ask questions about PDF
                st.subheader("❓ Ask Questions About This PDF")
                pdf_question = st.text_input(
                    "Question",
                    placeholder="What is this document about?",
                    label_visibility="collapsed"
                )
                
                if st.button("Ask JARVIS"):
                    if st.session_state.is_running:
                        context_message = f"Here's the content from a PDF document:\n\n{result['text'][:2000]}...\n\nUser question: {pdf_question}"
                        send_message(context_message)
                        st.success("Question sent to JARVIS!")
                    else:
                        st.error("Please start JARVIS first")
            else:
                st.error(result['message'])
            
            # Clean up
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    # Settings Tab
    with tab5:
        st.header("⚙️ Settings")
        
        st.subheader("🎨 Appearance")
        theme = st.selectbox("Theme", ["Dark", "Light", "Auto"])
        
        st.subheader("🔊 Audio")
        enable_tts = st.checkbox("Enable Text-to-Speech", value=True)
        enable_stt = st.checkbox("Enable Speech-to-Text", value=True)
        
        st.subheader("🎥 Video")
        default_video_mode = st.selectbox(
            "Default Video Mode",
            ["none", "camera", "screen"]
        )
        
        st.subheader("🧠 Memory")
        st.slider("Memory Buffer Size", 10, 100, 50)
        
        if st.button("Save Settings"):
            st.success("Settings saved successfully!")
        
        st.divider()
        
        st.subheader("ℹ️ About")
        st.markdown("""
        **J.A.R.V.I.S. AI Assistant**
        
        Version: 2.0.0
        
        An advanced AI assistant powered by Google Gemini with:
        - Voice and text interaction
        - File and system management
        - Automation capabilities
        - Memory and learning
        - PDF document analysis
        
        Built with ❤️ using Streamlit and Python
        """)

if __name__ == "__main__":
    main()