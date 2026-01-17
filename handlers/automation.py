"""
Automation Handler
Handles automation tasks like clipboard, YouTube, video modes
"""

import webbrowser
import pyperclip
import pywhatkit as kit


class Automation:
    def __init__(self):
        pass
    
    def clipboard_operations(self, operation, text=None):
        """Handle clipboard operations"""
        try:
            if operation == "copy":
                if not text:
                    return {"status": "error", "message": "No text provided to copy."}
                pyperclip.copy(text)
                return {"status": "success", "message": "Text copied to clipboard."}
            
            elif operation == "paste":
                clipboard_content = pyperclip.paste()
                return {"status": "success", "message": "Clipboard content retrieved.", "content": clipboard_content}
            
            elif operation == "read":
                clipboard_content = pyperclip.paste()
                return {"status": "success", "message": f"Clipboard contains: {clipboard_content[:100]}...", "content": clipboard_content}
            
            else:
                return {"status": "error", "message": "Invalid clipboard operation."}
        except Exception as e:
            return {"status": "error", "message": f"Clipboard operation failed: {str(e)}"}
    
    def youtube_control(self, search_query, action):
        """Control YouTube operations"""
        try:
            if action == "search":
                search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                webbrowser.open(search_url)
                return {"status": "success", "message": f"Opened YouTube search for '{search_query}'."}
            
            elif action == "play_first":
                try:
                    kit.playonyt(search_query)
                    return {"status": "success", "message": f"Playing first YouTube result for '{search_query}'."}
                except:
                    search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                    webbrowser.open(search_url)
                    return {"status": "success", "message": f"Opened YouTube search for '{search_query}'."}
            
            elif action == "open_channel":
                channel_url = f"https://www.youtube.com/@{search_query}"
                webbrowser.open(channel_url)
                return {"status": "success", "message": f"Opened YouTube channel '{search_query}'."}
            
            else:
                return {"status": "error", "message": "Invalid YouTube action."}
        except Exception as e:
            return {"status": "error", "message": f"YouTube control failed: {str(e)}"}