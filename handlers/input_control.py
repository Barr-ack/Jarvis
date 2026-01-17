"""
Input Control Handler
Handles mouse, keyboard, and screen automation
"""

import pyautogui
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
import time

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


class InputControl:
    def __init__(self):
        self.input_control_enabled = False
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
    
    def input_control_toggle(self, enable):
        """Enable or disable mouse and keyboard control"""
        try:
            self.input_control_enabled = enable
            status = "ENABLED" if enable else "DISABLED"
            
            if enable:
                screen_width, screen_height = pyautogui.size()
                message = f"🎮 Input control {status}. Screen size: {screen_width}x{screen_height}. Ready for mouse and keyboard commands."
            else:
                message = f"🎮 Input control {status}. Mouse and keyboard control is now locked."
            
            print(f"[INPUT CONTROL] {message}")
            return {"status": "success", "message": message, "enabled": enable}
            
        except Exception as e:
            return {"status": "error", "message": f"Input control toggle failed: {str(e)}"}
    
    def mouse_control(self, action, x=None, y=None, direction=None, amount=None):
        """Control mouse operations"""
        try:
            if not self.input_control_enabled:
                return {
                    "status": "error", 
                    "message": "⚠️ Mouse control is disabled. Say 'enable input control' first."
                }
            
            if action == "move":
                if x is None or y is None:
                    return {"status": "error", "message": "X and Y coordinates required for move"}
                
                pyautogui.moveTo(x, y, duration=0.5)
                return {"status": "success", "message": f"Moved mouse to ({x}, {y})"}
            
            elif action == "click":
                if x is not None and y is not None:
                    pyautogui.click(x, y)
                    return {"status": "success", "message": f"Clicked at ({x}, {y})"}
                else:
                    pyautogui.click()
                    return {"status": "success", "message": "Clicked at current position"}
            
            elif action == "double_click":
                if x is not None and y is not None:
                    pyautogui.doubleClick(x, y)
                    return {"status": "success", "message": f"Double-clicked at ({x}, {y})"}
                else:
                    pyautogui.doubleClick()
                    return {"status": "success", "message": "Double-clicked at current position"}
            
            elif action == "right_click":
                if x is not None and y is not None:
                    pyautogui.rightClick(x, y)
                    return {"status": "success", "message": f"Right-clicked at ({x}, {y})"}
                else:
                    pyautogui.rightClick()
                    return {"status": "success", "message": "Right-clicked at current position"}
            
            elif action == "drag":
                if x is None or y is None:
                    return {"status": "error", "message": "X and Y coordinates required for drag"}
                
                duration = (amount or 10) / 10
                pyautogui.drag(x, y, duration=duration)
                return {"status": "success", "message": f"Dragged to ({x}, {y})"}
            
            elif action == "scroll":
                if not direction:
                    return {"status": "error", "message": "Scroll direction required"}
                
                scroll_amount = amount or 3
                if direction.lower() == "up":
                    pyautogui.scroll(scroll_amount * 100)
                else:
                    pyautogui.scroll(-scroll_amount * 100)
                
                return {"status": "success", "message": f"Scrolled {direction} {scroll_amount} units"}
            
            elif action == "position":
                pos = pyautogui.position()
                return {
                    "status": "success", 
                    "message": f"Current mouse position: ({pos.x}, {pos.y})",
                    "position": {"x": pos.x, "y": pos.y}
                }
            
            else:
                return {"status": "error", "message": f"Invalid mouse action: {action}"}
                
        except Exception as e:
            return {"status": "error", "message": f"Mouse control failed: {str(e)}"}
    
    def keyboard_control(self, action, text=None, key=None, keys=None):
        """Control keyboard operations"""
        try:
            if not self.input_control_enabled:
                return {
                    "status": "error", 
                    "message": "⚠️ Keyboard control is disabled. Say 'enable input control' first."
                }
            
            if action == "type":
                if not text:
                    return {"status": "error", "message": "Text required for typing"}
                
                pyautogui.write(text, interval=0.05)
                return {"status": "success", "message": f"Typed: {text[:50]}..."}
            
            elif action == "press":
                if not key:
                    return {"status": "error", "message": "Key required for press action"}
                
                key_map = {
                    "enter": "enter", "return": "enter",
                    "tab": "tab",
                    "space": "space", "spacebar": "space",
                    "backspace": "backspace",
                    "delete": "delete", "del": "delete",
                    "escape": "esc", "esc": "esc",
                    "up": "up", "down": "down", "left": "left", "right": "right",
                    "home": "home", "end": "end",
                    "pageup": "pageup", "pagedown": "pagedown",
                    "ctrl": "ctrl", "control": "ctrl",
                    "alt": "alt",
                    "shift": "shift",
                    "win": "win", "windows": "win", "cmd": "command", "command": "command"
                }
                
                key_to_press = key_map.get(key.lower(), key.lower())
                pyautogui.press(key_to_press)
                return {"status": "success", "message": f"Pressed key: {key}"}
            
            elif action == "hotkey":
                if not keys:
                    return {"status": "error", "message": "Keys required for hotkey"}
                
                key_list = [k.strip().lower() for k in keys.split(',')]
                pyautogui.hotkey(*key_list)
                return {"status": "success", "message": f"Executed hotkey: {' + '.join(key_list)}"}
            
            elif action == "hold":
                if not key:
                    return {"status": "error", "message": "Key required for hold action"}
                
                pyautogui.keyDown(key.lower())
                return {"status": "success", "message": f"Holding key: {key}"}
            
            elif action == "release":
                if not key:
                    return {"status": "error", "message": "Key required for release action"}
                
                pyautogui.keyUp(key.lower())
                return {"status": "success", "message": f"Released key: {key}"}
            
            else:
                return {"status": "error", "message": f"Invalid keyboard action: {action}"}
                
        except Exception as e:
            return {"status": "error", "message": f"Keyboard control failed: {str(e)}"}
    
    def screen_automation(self, action, image_path=None, save_path=None, region=None):
        """Advanced screen automation"""
        try:
            if action == "screenshot":
                if not save_path:
                    save_path = f"screenshot_{int(time.time())}.png"
                
                if region:
                    coords = [int(c.strip()) for c in region.split(',')]
                    screenshot = pyautogui.screenshot(region=tuple(coords))
                else:
                    screenshot = pyautogui.screenshot()
                
                screenshot.save(save_path)
                return {"status": "success", "message": f"Screenshot saved to {save_path}"}
            
            elif action == "screen_size":
                width, height = pyautogui.size()
                return {
                    "status": "success", 
                    "message": f"Screen size: {width}x{height}",
                    "width": width,
                    "height": height
                }
            
            elif action == "find_image":
                if not image_path:
                    return {"status": "error", "message": "Image path required"}
                
                import os
                if not os.path.exists(image_path):
                    return {"status": "error", "message": f"Image not found: {image_path}"}
                
                try:
                    location = pyautogui.locateOnScreen(image_path, confidence=0.8)
                    if location:
                        center = pyautogui.center(location)
                        return {
                            "status": "success",
                            "message": f"Found image at ({center.x}, {center.y})",
                            "location": {"x": center.x, "y": center.y}
                        }
                    else:
                        return {"status": "error", "message": "Image not found on screen"}
                except Exception:
                    return {"status": "error", "message": "Image recognition failed (opencv-python may be needed)"}
            
            elif action == "click_image":
                if not image_path:
                    return {"status": "error", "message": "Image path required"}
                
                import os
                if not os.path.exists(image_path):
                    return {"status": "error", "message": f"Image not found: {image_path}"}
                
                try:
                    location = pyautogui.locateOnScreen(image_path, confidence=0.8)
                    if location:
                        center = pyautogui.center(location)
                        pyautogui.click(center)
                        return {"status": "success", "message": f"Clicked image at ({center.x}, {center.y})"}
                    else:
                        return {"status": "error", "message": "Image not found on screen"}
                except Exception:
                    return {"status": "error", "message": "Image recognition failed"}
            
            elif action == "pixel_color":
                x, y = pyautogui.position()
                color = pyautogui.pixel(x, y)
                return {
                    "status": "success",
                    "message": f"Pixel color at ({x}, {y}): RGB{color}",
                    "color": {"r": color[0], "g": color[1], "b": color[2]}
                }
            
            else:
                return {"status": "error", "message": f"Invalid screen automation action: {action}"}
                
        except Exception as e:
            return {"status": "error", "message": f"Screen automation failed: {str(e)}"}