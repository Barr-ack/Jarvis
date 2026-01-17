"""
System Control Handler
Handles system-level operations and diagnostics
"""

import os
import sys
import subprocess
import webbrowser
import psutil

try:
    import pycaw
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False

try:
    import screen_brightness_control as sbc
    SBC_AVAILABLE = True
except ImportError:
    SBC_AVAILABLE = False

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    wmi = None

from datetime import datetime as dt_datetime


class SystemControl:
    def __init__(self):
        pass
    
    def open_application(self, application_name):
        """Open/launch a desktop application"""
        print(f">>> [DEBUG] Attempting to open application: '{application_name}'")
        try:
            if not application_name or not isinstance(application_name, str):
                return {"status": "error", "message": "Invalid application name provided."}
            
            command, shell_mode = [], False
            
            if sys.platform == "win32":
                app_map = {
                    "calculator": "calc:",
                    "notepad": "notepad",
                    "chrome": "chrome",
                    "google chrome": "chrome",
                    "firefox": "firefox",
                    "explorer": "explorer",
                    "file explorer": "explorer"
                }
                app_command = app_map.get(application_name.lower(), application_name)
                command, shell_mode = f"start {app_command}", True
            
            elif sys.platform == "darwin":
                app_map = {
                    "calculator": "Calculator",
                    "chrome": "Google Chrome",
                    "firefox": "Firefox",
                    "finder": "Finder",
                    "textedit": "TextEdit"
                }
                app_name = app_map.get(application_name.lower(), application_name)
                command = ["open", "-a", app_name]
            
            else:
                command = [application_name.lower()]
            
            subprocess.Popen(command, shell=shell_mode)
            return {"status": "success", "message": f"Successfully launched '{application_name}'."}
        
        except FileNotFoundError:
            return {"status": "error", "message": f"Application '{application_name}' not found."}
        except Exception as e:
            return {"status": "error", "message": f"An error occurred: {str(e)}"}
    
    def open_website(self, url):
        """Open a website in the default browser"""
        print(f">>> [DEBUG] Attempting to open URL: '{url}'")
        try:
            if not url or not isinstance(url, str):
                return {"status": "error", "message": "Invalid URL provided."}
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            webbrowser.open(url)
            return {"status": "success", "message": f"Successfully opened '{url}'."}
        except Exception as e:
            return {"status": "error", "message": f"An error occurred: {str(e)}"}
    
    def system_control(self, action, value=None):
        """Control system settings and power options"""
        try:
            if action == "volume":
                if value is None:
                    return {"status": "error", "message": "Volume value required (0-100)."}
                
                try:
                    if sys.platform == "win32" and PYCAW_AVAILABLE:
                        devices = AudioUtilities.GetSpeakers()
                        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                        volume = cast(interface, POINTER(IAudioEndpointVolume))
                        volume.SetMasterVolumeLevelScalar(value / 100.0, None)
                        return {"status": "success", "message": f"Volume set to {value}%."}
                except:
                    if sys.platform == "darwin":
                        os.system(f"osascript -e 'set volume output volume {value}'")
                    elif sys.platform.startswith("linux"):
                        os.system(f"amixer set Master {value}%")
                    return {"status": "success", "message": f"Volume set to {value}%."}
            
            elif action == "brightness":
                if value is None:
                    return {"status": "error", "message": "Brightness value required (0-100)."}
                
                try:
                    if SBC_AVAILABLE:
                        sbc.set_brightness(value)
                        return {"status": "success", "message": f"Brightness set to {value}%."}
                    else:
                        return {"status": "error", "message": "Brightness control not available."}
                except:
                    return {"status": "error", "message": "Could not control brightness."}
            
            elif action == "battery":
                try:
                    battery = psutil.sensors_battery()
                    if battery:
                        percent = battery.percent
                        plugged = "Plugged in" if battery.power_plugged else "On battery"
                        return {"status": "success", "message": f"Battery: {percent}% - {plugged}"}
                    else:
                        return {"status": "error", "message": "No battery information available."}
                except:
                    return {"status": "error", "message": "Could not get battery status."}
            
            elif action == "wifi_toggle":
                try:
                    if sys.platform == "win32":
                        result = subprocess.run(
                            ["netsh", "interface", "show", "interface"], 
                            capture_output=True, text=True
                        )
                        if "Wi-Fi" in result.stdout and "Connected" in result.stdout:
                            subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "disabled"])
                            return {"status": "success", "message": "Wi-Fi disabled."}
                        else:
                            subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "enabled"])
                            return {"status": "success", "message": "Wi-Fi enabled."}
                    else:
                        return {"status": "info", "message": "Wi-Fi toggle requires manual implementation for this OS."}
                except Exception as e:
                    return {"status": "error", "message": f"Wi-Fi control failed: {str(e)}"}
            
            elif action == "shutdown":
                try:
                    if sys.platform == "win32":
                        subprocess.run(["shutdown", "/s", "/t", "5"])
                    elif sys.platform == "darwin":
                        subprocess.run(["sudo", "shutdown", "-h", "+1"])
                    else:
                        subprocess.run(["sudo", "shutdown", "-h", "now"])
                    return {"status": "success", "message": "System shutdown initiated."}
                except Exception as e:
                    return {"status": "error", "message": f"Shutdown failed: {str(e)}"}
            
            elif action == "restart":
                try:
                    if sys.platform == "win32":
                        subprocess.run(["shutdown", "/r", "/t", "5"])
                    elif sys.platform == "darwin":
                        subprocess.run(["sudo", "shutdown", "-r", "+1"])
                    else:
                        subprocess.run(["sudo", "reboot"])
                    return {"status": "success", "message": "System restart initiated."}
                except Exception as e:
                    return {"status": "error", "message": f"Restart failed: {str(e)}"}
            
            elif action == "lock":
                try:
                    if sys.platform == "win32":
                        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
                    elif sys.platform == "darwin":
                        subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
                    else:
                        subprocess.run(["gnome-screensaver-command", "--lock"])
                    return {"status": "success", "message": "System locked."}
                except Exception as e:
                    return {"status": "error", "message": f"Lock failed: {str(e)}"}
            
            elif action == "sleep":
                try:
                    if sys.platform == "win32":
                        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
                    elif sys.platform == "darwin":
                        subprocess.run(["pmset", "sleepnow"])
                    else:
                        subprocess.run(["systemctl", "suspend"])
                    return {"status": "success", "message": "System entering sleep mode."}
                except Exception as e:
                    return {"status": "error", "message": f"Sleep failed: {str(e)}"}
            
            else:
                return {"status": "error", "message": "Invalid system control action."}
                
        except Exception as e:
            return {"status": "error", "message": f"System control failed: {str(e)}"}
    
    def system_diagnostics(self, operation, detailed=False):
        """System diagnostics and troubleshooting"""
        try:
            if operation == "wifi_check":
                if sys.platform == "win32":
                    result = subprocess.run(
                        ["netsh", "wlan", "show", "profiles"], 
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        return {"status": "success", "message": "Wi-Fi profiles found", "data": result.stdout}
                    else:
                        return {"status": "error", "message": "Wi-Fi check failed"}
                else:
                    result = subprocess.run(
                        ["ping", "-c", "4", "8.8.8.8"], 
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        return {"status": "success", "message": "Internet connectivity: OK"}
                    else:
                        return {"status": "error", "message": "Internet connectivity: FAILED"}
            
            elif operation == "health_check":
                health_info = []
                
                cpu_percent = psutil.cpu_percent(interval=1)
                health_info.append(f"CPU Usage: {cpu_percent}%")
                
                memory = psutil.virtual_memory()
                health_info.append(
                    f"Memory Usage: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)"
                )
                
                disk = psutil.disk_usage('/')
                health_info.append(
                    f"Disk Usage: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)"
                )
                
                boot_time = psutil.boot_time()
                uptime = dt_datetime.now() - dt_datetime.fromtimestamp(boot_time)
                health_info.append(f"System Uptime: {str(uptime).split('.')[0]}")
                
                return {"status": "success", "message": "System Health Check:\n• " + "\n• ".join(health_info)}
            
            elif operation == "disk_cleanup":
                cleanup_info = []
                temp_dirs = []
                
                if sys.platform == "win32":
                    temp_dirs = [os.environ.get('TEMP', ''), os.environ.get('TMP', '')]
                else:
                    temp_dirs = ['/tmp', '/var/tmp']
                
                total_cleaned = 0
                for temp_dir in temp_dirs:
                    if os.path.exists(temp_dir):
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                try:
                                    file_size = os.path.getsize(file_path)
                                    if file.endswith('.tmp') or file.startswith('~'):
                                        os.remove(file_path)
                                        total_cleaned += file_size
                                except:
                                    continue
                
                cleanup_info.append(f"Cleaned {total_cleaned // 1024}KB of temporary files")
                return {"status": "success", "message": "Disk Cleanup:\n• " + "\n• ".join(cleanup_info)}
            
            elif operation == "driver_scan":
                if sys.platform == "win32" and WMI_AVAILABLE:
                    try:
                        c = wmi.WMI()
                        drivers = []
                        for driver in c.Win32_SystemDriver():
                            if driver.State == "Running":
                                drivers.append(f"{driver.Name}: {driver.State}")
                        
                        return {
                            "status": "success", 
                            "message": f"Found {len(drivers)} running drivers", 
                            "data": drivers[:10] if not detailed else drivers
                        }
                    except:
                        return {"status": "info", "message": "Driver scan requires WMI support"}
                else:
                    result = subprocess.run(["lsmod"], capture_output=True, text=True)
                    if result.returncode == 0:
                        return {"status": "success", "message": "Kernel modules loaded", "data": result.stdout}
                    else:
                        return {"status": "error", "message": "Driver scan not available on this system"}
            
            else:
                return {"status": "error", "message": "Invalid diagnostics operation"}
                
        except Exception as e:
            return {"status": "error", "message": f"Diagnostics failed: {str(e)}"}