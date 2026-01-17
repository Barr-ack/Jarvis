"""
JARVIS AI Assistant - Main Entry Point
Orchestrates all modules and provides the core AI loop
"""

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import asyncio
import base64
import io
import os
import sys
import traceback
import json
import schedule
import websockets
import argparse
import threading
from dotenv import load_dotenv
import pyaudio
import PIL.Image
import cv2
import numpy as np
from PIL import ImageGrab

import google.genai as genai
print("GenAI module loaded successfully!")

# Import modularized components
from config_loader import load_config
from memory import (
    add_exchange_to_buffer, 
    save_session_memory, 
    get_all_memories, 
    get_relevant_memories
)

# Import function handlers
from handlers.file_operations import FileOperations
from handlers.system_control import SystemControl
from handlers.communication import Communication
from handlers.automation import Automation
from handlers.advanced_features import AdvancedFeatures
from handlers.input_control import InputControl
from handlers.pdf_handler import PDFHandler

# Load Environment Variables
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    sys.exit("Error: GEMINI_API_KEY not found. Please set it in your .env file.")
if not ELEVENLABS_API_KEY:
    sys.exit("Error: ELEVENLABS_API_KEY not found. Please check your .env file.")

# Configuration
config = load_config("config.json")
FORMAT = config.get("FORMAT", pyaudio.paInt16)
CHANNELS = config.get("CHANNELS", 1)
SEND_SAMPLE_RATE = config.get("SEND_SAMPLE_RATE", 16000)
RECEIVE_SAMPLE_RATE = config.get("RECEIVE_SAMPLE_RATE", 24000)
CHUNK_SIZE = config.get("CHUNK_SIZE", 1024)
MODEL = "gemini-live-2.5-flash-preview"
VOICE_ID = 'pFZP5JQG7iQjIQuC4Bku'
DEFAULT_MODE = "none"
MAX_OUTPUT_TOKENS = 100

pya = pyaudio.PyAudio()

class AI_Core:
    """
    Main AI Core - Handles backend operations for JARVIS
    """
    def __init__(self, video_mode="none", model="gemini-live-2.5-flash-preview"):
        self.model = model
        self.config = config or {"response_modalities": ["TEXT"]}
        self.video_mode = video_mode
        self.is_running = True
        self.last_reply = ""
        
        # Initialize handler modules
        self.file_ops = FileOperations()
        self.system_ctrl = SystemControl()
        self.communication = Communication()
        self.automation = Automation()
        self.advanced = AdvancedFeatures()
        self.input_ctrl = InputControl()
        self.pdf_handler = PDFHandler()
        
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        
        self.text_input_queue = asyncio.Queue()
        self.memory_storage = []
        self.user_id = "Barrack"
        self.current_user_input = ""
        
        # Load memory context
        print("🧠 Loading memory context...")
        memory_context = get_all_memories(self.user_id)
        
        if memory_context:
            print(f"✅ Memory context loaded ({len(memory_context)} characters)")
            original_instruction = config.get("system_instruction", "")
            enhanced_instruction = f"""{original_instruction}

IMPORTANT - USER MEMORY CONTEXT:
You have access to previous conversations and learned information about this user.
Use this context naturally in your responses without explicitly mentioning "I remember from our previous conversation".

{memory_context}

When the user mentions something new about themselves, their preferences, or important information, 
make sure to acknowledge it naturally in conversation."""
            
            config["system_instruction"] = enhanced_instruction
        else:
            print("ℹ No previous memories found - starting fresh")
        
        # Setup tools configuration
        self._setup_tools()
        
        self.session = None
        self.audio_stream = None
        self.out_queue_gemini = asyncio.Queue(maxsize=20)
        self.response_queue_tts = asyncio.Queue()
        self.audio_in_queue_player = asyncio.Queue()
        self.latest_frame = None
        self.tasks = []
        self.loop = asyncio.new_event_loop()
        self.scheduler_running = True
        self._start_scheduler()
    
    def _setup_tools(self):
        """Setup all function declarations for Gemini"""
        from handlers.tool_declarations import get_all_tool_declarations
        
        tools = [
            {'google_search': {}}, 
            {'code_execution': {}}, 
            {"function_declarations": get_all_tool_declarations()}
        ]
        
        self.config = {
            "response_modalities": ["TEXT"],
            "system_instruction": config["system_instruction"],
            "tools": tools,
            "max_output_tokens": MAX_OUTPUT_TOKENS
        }
    
    def _start_scheduler(self):
        """Start the task scheduler in a separate thread"""
        def run_scheduler():
            while self.scheduler_running:
                schedule.run_pending()
                import time
                time.sleep(1)
        
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
    
    async def handle_function_call(self, fc):
        """Route function calls to appropriate handlers"""
        args = fc.args
        result = {}
        
        # File Operations
        if fc.name == "create_folder":
            result = self.file_ops.create_folder(args.get("folder_path"))
        elif fc.name == "create_file":
            result = self.file_ops.create_file(args.get("file_path"), args.get("content"))
        elif fc.name == "edit_file":
            result = self.file_ops.edit_file(args.get("file_path"), args.get("content"))
        elif fc.name == "list_files":
            result = self.file_ops.list_files(args.get("directory_path"))
        elif fc.name == "read_file":
            result = self.file_ops.read_file(args.get("file_path"))
        elif fc.name == "file_management":
            result = self.file_ops.file_management(
                args.get("operation"), args.get("source_path"),
                args.get("target_path"), args.get("search_pattern"),
                args.get("file_type")
            )
        elif fc.name == "archive_operations":
            result = self.file_ops.archive_operations(
                args.get("operation"), args.get("source_path"),
                args.get("target_path"), args.get("format", "zip")
            )
        
        # System Control
        elif fc.name == "open_application":
            result = self.system_ctrl.open_application(args.get("application_name"))
        elif fc.name == "open_website":
            result = self.system_ctrl.open_website(args.get("url"))
        elif fc.name == "system_control":
            result = self.system_ctrl.system_control(args.get("action"), args.get("value"))
        elif fc.name == "system_diagnostics":
            result = self.system_ctrl.system_diagnostics(args.get("operation"), args.get("detailed", False))
        
        # Communication
        elif fc.name == "send_email":
            result = self.communication.send_email(
                args.get("to_email"), args.get("subject"),
                args.get("body"), args.get("cc")
            )
        elif fc.name == "read_email":
            result = self.communication.read_email(
                args.get("count", 5), args.get("unread_only", True)
            )
        elif fc.name == "send_whatsapp":
            result = self.communication.send_whatsapp(
                args.get("phone_number"), args.get("message"), args.get("delay", 1)
            )
        elif fc.name == "send_instagram_message":
            result = self.communication.send_instagram_message(
                args.get("username"), args.get("message")
            )
        
        # Automation
        elif fc.name == "clipboard_operations":
            result = self.automation.clipboard_operations(args.get("operation"), args.get("text"))
        elif fc.name == "youtube_control":
            result = self.automation.youtube_control(args.get("search_query"), args.get("action"))
        elif fc.name == "video_mode":
            mode = args.get('mode', 'none')
            if mode in ["camera", "screen", "none"]:
                self.set_video_mode(mode)
                result = {"status": "success", "message": f"Video mode switched to {mode}"}
            else:
                result = {"status": "error", "message": f"Invalid mode: {mode}"}
        
        # Advanced Features
        elif fc.name == "news_weather":
            result = self.advanced.news_weather(
                args.get("type"), args.get("location"), args.get("category")
            )
        elif fc.name == "code_analysis":
            result = self.advanced.code_analysis(
                args.get("operation"), args.get("code_content"),
                args.get("language"), args.get("file_path")
            )
        elif fc.name == "github_operations":
            result = self.advanced.github_operations(
                args.get("operation"), args.get("repo_url"),
                args.get("local_path"), args.get("commit_message")
            )
        elif fc.name == "web_automation":
            result = self.advanced.web_automation(
                args.get("operation"), args.get("url"),
                args.get("form_data"), args.get("selector")
            )
        elif fc.name == "package_manager":
            result = self.advanced.package_manager(
                args.get("operation"), args.get("package_type"),
                args.get("package_name")
            )
        elif fc.name == "task_scheduler":
            result = self.advanced.task_scheduler(
                args.get("operation"), args.get("task_name"),
                args.get("datetime"), args.get("message")
            )
        
        # Input Control
        elif fc.name == "input_control_toggle":
            result = self.input_ctrl.input_control_toggle(args.get("enable"))
        elif fc.name == "mouse_control":
            result = self.input_ctrl.mouse_control(
                args.get("action"), args.get("x"), args.get("y"),
                args.get("direction"), args.get("amount")
            )
        elif fc.name == "keyboard_control":
            result = self.input_ctrl.keyboard_control(
                args.get("action"), args.get("text"),
                args.get("key"), args.get("keys")
            )
        elif fc.name == "screen_automation":
            result = self.input_ctrl.screen_automation(
                args.get("action"), args.get("image_path"),
                args.get("save_path"), args.get("region")
            )
        
        # PDF Handler
        elif fc.name == "read_pdf":
            result = self.pdf_handler.read_pdf(args.get("file_path"))
        elif fc.name == "extract_pdf_text":
            result = self.pdf_handler.extract_pdf_text(
                args.get("file_path"), args.get("page_range")
            )
        
        print(f"[{fc.name.upper()}] {result.get('message', 'Executed')}")
        return result
    
    def set_video_mode(self, mode):
        """Sets the video source."""
        if mode in ["camera", "screen", "none"]:
            old_mode = self.video_mode
            self.video_mode = mode
            print(f">>> [VIDEO] Switched from {old_mode} to {self.video_mode}")
            
            if mode == "none":
                self.latest_frame = None
                print(">>> [VIDEO] Video capture disabled")
            elif mode == "camera":
                print(">>> [VIDEO] Camera mode enabled - frames will be sent to Gemini")
            elif mode == "screen":
                print(">>> [VIDEO] Screen capture mode enabled - screenshots will be sent to Gemini")
        else:
            print(f">>> [VIDEO ERROR] Invalid mode: {mode}")
    
    async def send_frames_to_gemini(self):
        """Capture and send video frames to Gemini"""
        video_capture = None
        while self.is_running:
            await asyncio.sleep(1.0)
            if self.video_mode != "none":
                frame = None
                try:
                    if self.video_mode == "camera":
                        if video_capture is None: 
                            video_capture = await asyncio.to_thread(cv2.VideoCapture, 0)
                        if video_capture.isOpened():
                            ret, frame = await asyncio.to_thread(video_capture.read)
                            if not ret:
                                continue
                    elif self.video_mode == "screen":
                        if video_capture is not None:
                            await asyncio.to_thread(video_capture.release)
                            video_capture = None
                        screenshot = await asyncio.to_thread(ImageGrab.grab)
                        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    
                    if frame is not None:
                        self.latest_frame = frame
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        pil_img = PIL.Image.fromarray(frame_rgb)
                        pil_img.thumbnail([1024, 1024])
                        image_io = io.BytesIO()
                        pil_img.save(image_io, format="jpeg")
                        gemini_data = {
                            "mime_type": "image/jpeg", 
                            "data": base64.b64encode(image_io.getvalue()).decode()
                        }
                        await self.out_queue_gemini.put(gemini_data)
                        
                except Exception as e:
                    print(f">>> [ERROR] Video capture error: {e}")
                    if video_capture is not None:
                        await asyncio.to_thread(video_capture.release)
                        video_capture = None
        
        if video_capture is not None: 
            await asyncio.to_thread(video_capture.release)
    
    async def receive_text(self):
        """Main JARVIS receive loop with auto-reconnect"""
        retry_delay = 3
        
        while self.is_running:
            try:
                turn = self.session.receive()
                asyncio.create_task(self._keep_alive(turn))
                self.last_reply = ""
                
                async for chunk in turn:
                    if chunk.tool_call and chunk.tool_call.function_calls:
                        function_responses = []
                        for fc in chunk.tool_call.function_calls:
                            result = await self.handle_function_call(fc)
                            function_responses.append({
                                "id": fc.id, 
                                "name": fc.name, 
                                "response": result
                            })
                        await self.session.send_tool_response(function_responses=function_responses)
                        continue
                    
                    if chunk.text:
                        print(chunk.text, end='', flush=True)
                        self.last_reply += chunk.text
                        await self.response_queue_tts.put(chunk.text)
                
                if self.current_user_input and self.last_reply:
                    add_exchange_to_buffer(
                        self.user_id, 
                        self.current_user_input, 
                        self.last_reply
                    )
                    self.current_user_input = ""
                
                print("\n")
                await self.response_queue_tts.put(None)
                
            except websockets.exceptions.ConnectionClosedError as e:
                print(f">>> [WARNING] Gemini Live disconnected: {e}")
                print(f">>> [INFO] Reconnecting in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                continue
            except TimeoutError:
                print(">>> [WARNING] Connection timeout — retrying...")
                await asyncio.sleep(retry_delay)
                continue
            except Exception:
                if not self.is_running: break
                print(">>> [ERROR] Exception in receive_text loop:")
                traceback.print_exc()
                await asyncio.sleep(retry_delay)
                continue
    
    async def _keep_alive(self, turn):
        """Send keepalive to maintain connection"""
        try:
            while self.is_running:
                await asyncio.sleep(30)
        except Exception:
            pass
    
    async def listen_audio(self):
        """Listen to microphone audio"""
        mic_info = pya.get_default_input_device_info()
        self.audio_stream = pya.open(
            format=FORMAT, channels=CHANNELS, rate=SEND_SAMPLE_RATE, 
            input=True, input_device_index=mic_info["index"], 
            frames_per_buffer=CHUNK_SIZE
        )
        while self.is_running:
            data = await asyncio.to_thread(
                self.audio_stream.read, CHUNK_SIZE, exception_on_overflow=False
            )
            if not self.is_running: break
            await self.out_queue_gemini.put({"data": data, "mime_type": "audio/pcm"})
    
    async def send_realtime(self):
        """Send audio data to Gemini session"""
        while self.is_running:
            try:
                msg = await self.out_queue_gemini.get()
                if not self.is_running:
                    break
                
                if msg.get("mime_type") == "audio/pcm" and self.session:
                    await self.session.send(input=msg)
                
                self.out_queue_gemini.task_done()
            
            except Exception as e:
                print(f">>> [ERROR] send_realtime error: {e}")
                await asyncio.sleep(0.1)
    
    async def process_text_input_queue(self):
        """Process text input from queue"""
        while self.is_running:
            text = await self.text_input_queue.get()
            if text is None:
                self.text_input_queue.task_done()
                break
            self.current_user_input = text
            if self.session:
                for q in [self.response_queue_tts, self.audio_in_queue_player]:
                    while not q.empty(): 
                        q.get_nowait()
                await self.session.send_client_content(
                    turns=[{"role": "user", "parts": [{"text": text or "."}]}]
                )
            self.text_input_queue.task_done()
    
    async def tts(self):
        """Text-to-speech using ElevenLabs"""
        uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream-input?model_id=eleven_turbo_v2_5&output_format=pcm_24000"
        while self.is_running:
            text_chunk = await self.response_queue_tts.get()
            if text_chunk is None or not self.is_running:
                self.response_queue_tts.task_done()
                continue
            
            try:
                async with websockets.connect(uri) as websocket:
                    await websocket.send(json.dumps({
                        "text": " ", 
                        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}, 
                        "xi_api_key": ELEVENLABS_API_KEY
                    }))
                    
                    async def listen():
                        while self.is_running:
                            try:
                                message = await websocket.recv()
                                data = json.loads(message)
                                if data.get("audio"): 
                                    await self.audio_in_queue_player.put(
                                        base64.b64decode(data["audio"])
                                    )
                                elif data.get("isFinal"): 
                                    break
                            except websockets.exceptions.ConnectionClosed: 
                                break
                    
                    listen_task = asyncio.create_task(listen())
                    await websocket.send(json.dumps({"text": text_chunk + " "}))
                    self.response_queue_tts.task_done()
                    
                    while self.is_running:
                        text_chunk = await self.response_queue_tts.get()
                        if text_chunk is None:
                            await websocket.send(json.dumps({"text": ""}))
                            self.response_queue_tts.task_done()
                            break
                        await websocket.send(json.dumps({"text": text_chunk + " "}))
                        self.response_queue_tts.task_done()
                    
                    await listen_task
            except Exception as e: 
                print(f">>> [ERROR] TTS Error: {e}")
    
    async def play_audio(self):
        """Play audio output"""
        stream = await asyncio.to_thread(
            pya.open, format=pyaudio.paInt16, channels=CHANNELS, 
            rate=RECEIVE_SAMPLE_RATE, output=True
        )
        while self.is_running:
            bytestream = await self.audio_in_queue_player.get()
            if bytestream and self.is_running: 
                await asyncio.to_thread(stream.write, bytestream)
            self.audio_in_queue_player.task_done()
    
    def handle_user_text(self, text):
        """Handle text input from user"""
        if self.is_running and self.loop.is_running(): 
            asyncio.run_coroutine_threadsafe(
                self.text_input_queue.put(text), self.loop
            )
    
    async def main_task_runner(self, session):
        """Run all async tasks"""
        self.session = session
        self.tasks.extend([
            asyncio.create_task(self.send_frames_to_gemini()),
            asyncio.create_task(self.listen_audio()), 
            asyncio.create_task(self.send_realtime()),
            asyncio.create_task(self.receive_text()), 
            asyncio.create_task(self.tts()),
            asyncio.create_task(self.play_audio()), 
            asyncio.create_task(self.process_text_input_queue())
        ])
        await asyncio.gather(*self.tasks, return_exceptions=True)
    
    async def run(self):
        """Main run loop"""
        try:
            async with self.client.aio.live.connect(model=MODEL, config=self.config) as session:
                await self.main_task_runner(session)
        except asyncio.CancelledError: 
            print(f"\n>>> [INFO] AI Core run loop gracefully cancelled.")
        except Exception as e: 
            print(f"\n>>> [ERROR] AI Core run loop encountered an error: {type(e).__name__}: {e}")
        finally:
            if self.is_running: 
                self.stop()
    
    def start_event_loop(self):
        """Start the asyncio event loop"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.run())
    
    async def shutdown_async_tasks(self):
        """Shutdown all async tasks"""
        if self.text_input_queue: 
            await self.text_input_queue.put(None)
        for task in self.tasks: 
            task.cancel()
        await asyncio.sleep(0.1)
    
    def stop(self):
        """Stop the AI core"""
        if self.is_running and self.loop.is_running():
            print("\n>>> 🧠 Saving session memory...")
            try:
                save_session_memory(self.user_id)
                print(">>> ✅ Session memory saved successfully")
            except Exception as e:
                print(f">>> ⚠️ Error saving session memory: {e}")
            
            self.is_running = False
            self.scheduler_running = False
            future = asyncio.run_coroutine_threadsafe(self.shutdown_async_tasks(), self.loop)
            try: 
                future.result(timeout=5)
            except Exception as e: 
                print(f">>> [ERROR] Timeout or error during async shutdown: {e}")
        
        if self.audio_stream and self.audio_stream.is_active():
            self.audio_stream.stop_stream()
            self.audio_stream.close()


def console_input_handler(ai_core):
    """Handle console input in a separate thread"""
    print(">>> J.A.R.V.I.S. Console Assistant Started")
    print(">>> 🧠 Memory System: ACTIVE")
    print(">>> Commands available - Type 'help' for full list")
    print(">>> Type 'quit' or 'exit' to stop")
    print("-" * 50)
    
    while ai_core.is_running:
        try:
            user_input = input("> ").strip()
            if user_input.lower() in ['quit', 'exit']:
                print(">>> Shutting down JARVIS...")
                ai_core.stop()
                break
            elif user_input.lower() == 'memories':
                print("\n=== Retrieving Stored Memories ===")
                memories = get_all_memories(ai_core.user_id)
                print(memories)
                print("=" * 50 + "\n")
            elif user_input.lower() == 'cam':
                ai_core.set_video_mode("camera")
            elif user_input.lower() == 'screen':
                ai_core.set_video_mode("screen")
            elif user_input.lower() == 'off':
                ai_core.set_video_mode("none")
            elif user_input:
                print(f"User: {user_input}")
                print("JARVIS: ", end='', flush=True)
                ai_core.handle_user_text(user_input)
        
        except (EOFError, KeyboardInterrupt):
            print("\n>>> Shutting down JARVIS...")
            ai_core.stop()
            break
        except Exception as e:
            print(f">>> [ERROR] Input handler error: {e}")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--mode", type=str, default=DEFAULT_MODE, 
                        help="Video mode to start with", 
                        choices=["camera", "screen", "none"])
        args = parser.parse_args()
        
        ai_core = AI_Core(video_mode=args.mode)
        
        # Start the AI core in a separate thread
        backend_thread = threading.Thread(target=ai_core.start_event_loop)
        backend_thread.daemon = True
        backend_thread.start()
        
        # Handle console input in the main thread
        console_input_handler(ai_core)
        
    except KeyboardInterrupt:
        print(">>> [INFO] Application interrupted by user.")
    finally:
        pya.terminate()
        print(">>> [INFO] Application terminated.")