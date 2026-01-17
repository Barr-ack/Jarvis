"""
Tool Declarations
Contains all function declarations for Gemini API
"""

def get_all_tool_declarations():
    """Return all function declarations for Gemini"""
    
    return [
        # File Operations
        {
            "name": "create_folder",
            "description": "Creates a new folder at the specified path relative to the script's root directory.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "folder_path": {
                        "type": "STRING",
                        "description": "The path for the new folder (e.g., 'new_project/assets')."
                    }
                },
                "required": ["folder_path"]
            }
        },
        {
            "name": "create_file",
            "description": "Creates a new file with specified content at a given path.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "file_path": {
                        "type": "STRING",
                        "description": "The path for the new file (e.g., 'new_project/notes.txt')."
                    },
                    "content": {
                        "type": "STRING",
                        "description": "The content to write into the new file."
                    }
                },
                "required": ["file_path", "content"]
            }
        },
        {
            "name": "edit_file",
            "description": "Appends content to an existing file at a specified path.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "file_path": {
                        "type": "STRING",
                        "description": "The path of the file to edit (e.g., 'project/notes.txt')."
                    },
                    "content": {
                        "type": "STRING",
                        "description": "The content to append to the file."
                    }
                },
                "required": ["file_path", "content"]
            }
        },
        {
            "name": "list_files",
            "description": "Lists all files and directories within a specified folder.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "directory_path": {
                        "type": "STRING",
                        "description": "The path of the directory to inspect."
                    }
                }
            }
        },
        {
            "name": "read_file",
            "description": "Reads the entire content of a specified file.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "file_path": {
                        "type": "STRING",
                        "description": "The path of the file to read."
                    }
                },
                "required": ["file_path"]
            }
        },
        {
            "name": "file_management",
            "description": "Advanced file operations: search, move, rename, delete, organize files.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "operation": {
                        "type": "STRING",
                        "description": "Operation: 'search', 'move', 'rename', 'delete', 'organize', 'copy'"
                    },
                    "source_path": {
                        "type": "STRING",
                        "description": "Source file/folder path"
                    },
                    "target_path": {
                        "type": "STRING",
                        "description": "Target path (for move, rename, copy)"
                    },
                    "search_pattern": {
                        "type": "STRING",
                        "description": "Pattern to search for"
                    },
                    "file_type": {
                        "type": "STRING",
                        "description": "File type filter (e.g., '.txt', '.py')"
                    }
                },
                "required": ["operation"]
            }
        },
        {
            "name": "archive_operations",
            "description": "Compress or extract files and folders.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "operation": {
                        "type": "STRING",
                        "description": "Operation: 'compress', 'extract'"
                    },
                    "source_path": {
                        "type": "STRING",
                        "description": "Source file/folder path"
                    },
                    "target_path": {
                        "type": "STRING",
                        "description": "Target archive/extraction path"
                    },
                    "format": {
                        "type": "STRING",
                        "description": "Archive format: 'zip', 'tar', 'tar.gz'"
                    }
                },
                "required": ["operation", "source_path", "target_path"]
            }
        },
        
        # System Control
        {
            "name": "open_application",
            "description": "Opens or launches a desktop application on the user's computer.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "application_name": {
                        "type": "STRING",
                        "description": "The name of the application to open."
                    }
                },
                "required": ["application_name"]
            }
        },
        {
            "name": "open_website",
            "description": "Opens a given URL in the default web browser.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "url": {
                        "type": "STRING",
                        "description": "The full URL of the website to open."
                    }
                },
                "required": ["url"]
            }
        },
        {
            "name": "system_control",
            "description": "Control system settings and power options.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "action": {
                        "type": "STRING",
                        "description": "Action: 'volume', 'brightness', 'battery', 'wifi_toggle', 'shutdown', 'restart', 'lock', 'sleep'."
                    },
                    "value": {
                        "type": "INTEGER",
                        "description": "Value for volume (0-100) or brightness (0-100)."
                    }
                },
                "required": ["action"]
            }
        },
        {
            "name": "system_diagnostics",
            "description": "Run system diagnostics and troubleshooting.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "operation": {
                        "type": "STRING",
                        "description": "Operation: 'wifi_check', 'driver_scan', 'health_check', 'disk_cleanup'."
                    },
                    "detailed": {
                        "type": "BOOLEAN",
                        "description": "Show detailed results"
                    }
                },
                "required": ["operation"]
            }
        },
        
        # Communication
        {
            "name": "send_email",
            "description": "Send an email to specified recipients.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "to_email": {
                        "type": "STRING",
                        "description": "Recipient's email address."
                    },
                    "subject": {
                        "type": "STRING",
                        "description": "Email subject line."
                    },
                    "body": {
                        "type": "STRING",
                        "description": "Email message body."
                    },
                    "cc": {
                        "type": "STRING",
                        "description": "CC recipients (optional)."
                    }
                },
                "required": ["to_email", "subject", "body"]
            }
        },
        {
            "name": "read_email",
            "description": "Read recent emails from inbox.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "count": {
                        "type": "INTEGER",
                        "description": "Number of recent emails to read (default: 5)."
                    },
                    "unread_only": {
                        "type": "BOOLEAN",
                        "description": "Read only unread emails (default: true)."
                    }
                }
            }
        },
        {
            "name": "send_whatsapp",
            "description": "Send a WhatsApp message.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "phone_number": {
                        "type": "STRING",
                        "description": "Phone number with country code."
                    },
                    "message": {
                        "type": "STRING",
                        "description": "Message to send."
                    },
                    "delay": {
                        "type": "INTEGER",
                        "description": "Minutes to wait before sending (default: 1)."
                    }
                },
                "required": ["phone_number", "message"]
            }
        },
        {
            "name": "send_instagram_message",
            "description": "Send an Instagram direct message.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "username": {
                        "type": "STRING",
                        "description": "Instagram username to message."
                    },
                    "message": {
                        "type": "STRING",
                        "description": "Message to send."
                    }
                },
                "required": ["username", "message"]
            }
        },
        
        # Automation
        {
            "name": "clipboard_operations",
            "description": "Perform clipboard operations: copy text, paste content, or read current clipboard.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "operation": {
                        "type": "STRING",
                        "description": "Operation type: 'copy', 'paste', 'read'."
                    },
                    "text": {
                        "type": "STRING",
                        "description": "Text to copy (required for 'copy' operation)."
                    }
                },
                "required": ["operation"]
            }
        },
        {
            "name": "youtube_control",
            "description": "Search and play YouTube videos.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "search_query": {
                        "type": "STRING",
                        "description": "Video search query."
                    },
                    "action": {
                        "type": "STRING",
                        "description": "Action: 'search', 'play_first', 'open_channel'."
                    }
                },
                "required": ["search_query", "action"]
            }
        },
        {
            "name": "video_mode",
            "description": "Switches video input between webcam, screen capture, or none.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "mode": {
                        "type": "STRING",
                        "description": "Video source: 'camera', 'screen', or 'none'"
                    }
                },
                "required": ["mode"]
            }
        },
        
        # Advanced Features
        {
            "name": "news_weather",
            "description": "Get news and weather updates for daily briefings.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "type": {
                        "type": "STRING",
                        "description": "Type: 'news', 'weather', 'briefing'"
                    },
                    "location": {
                        "type": "STRING",
                        "description": "Location for weather (optional)"
                    },
                    "category": {
                        "type": "STRING",
                        "description": "News category (optional)"
                    }
                },
                "required": ["type"]
            }
        },
        {
            "name": "code_analysis",
            "description": "Analyze code for errors, suggest fixes, and write new code.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "operation": {
                        "type": "STRING",
                        "description": "Operation: 'analyze', 'debug', 'write', 'review'"
                    },
                    "code_content": {
                        "type": "STRING",
                        "description": "Code to analyze or base for writing"
                    },
                    "language": {
                        "type": "STRING",
                        "description": "Programming language"
                    },
                    "file_path": {
                        "type": "STRING",
                        "description": "Path to code file"
                    }
                },
                "required": ["operation"]
            }
        },
        {
            "name": "github_operations",
            "description": "GitHub integration for repository management.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "operation": {
                        "type": "STRING",
                        "description": "Operation: 'clone', 'push', 'pull', 'status', 'commit'"
                    },
                    "repo_url": {
                        "type": "STRING",
                        "description": "Repository URL"
                    },
                    "local_path": {
                        "type": "STRING",
                        "description": "Local repository path"
                    },
                    "commit_message": {
                        "type": "STRING",
                        "description": "Commit message"
                    }
                },
                "required": ["operation"]
            }
        },
        {
            "name": "web_automation",
            "description": "Automate web tasks: fill forms, scrape data, summarize pages.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "operation": {
                        "type": "STRING",
                        "description": "Operation: 'scrape', 'fill_form', 'summarize', 'screenshot'"
                    },
                    "url": {
                        "type": "STRING",
                        "description": "Target URL"
                    },
                    "form_data": {
                        "type": "STRING",
                        "description": "JSON form data"
                    },
                    "selector": {
                        "type": "STRING",
                        "description": "CSS selector for scraping"
                    }
                },
                "required": ["operation", "url"]
            }
        },
        {
            "name": "package_manager",
            "description": "Install, update, or manage software packages.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "operation": {
                        "type": "STRING",
                        "description": "Operation: 'install', 'update', 'uninstall', 'list'"
                    },
                    "package_type": {
                        "type": "STRING",
                        "description": "Type: 'python', 'node', 'system'"
                    },
                    "package_name": {
                        "type": "STRING",
                        "description": "Package name to manage"
                    }
                },
                "required": ["operation", "package_type"]
            }
        },
        {
            "name": "task_scheduler",
            "description": "Schedule reminders, alarms, and calendar events.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "operation": {
                        "type": "STRING",
                        "description": "Operation: 'add', 'list', 'remove', 'alarm'"
                    },
                    "task_name": {
                        "type": "STRING",
                        "description": "Task/reminder name"
                    },
                    "datetime": {
                        "type": "STRING",
                        "description": "Date/time (YYYY-MM-DD HH:MM)"
                    },
                    "message": {
                        "type": "STRING",
                        "description": "Reminder message"
                    }
                },
                "required": ["operation"]
            }
        },
        
        # Input Control
        {
            "name": "input_control_toggle",
            "description": "Enable or disable mouse and keyboard control.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "enable": {
                        "type": "BOOLEAN",
                        "description": "True to enable, False to disable"
                    }
                },
                "required": ["enable"]
            }
        },
        {
            "name": "mouse_control",
            "description": "Control mouse movements, clicks, and scrolling.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "action": {
                        "type": "STRING",
                        "description": "Action: 'move', 'click', 'double_click', 'right_click', 'drag', 'scroll', 'position'"
                    },
                    "x": {
                        "type": "INTEGER",
                        "description": "X coordinate"
                    },
                    "y": {
                        "type": "INTEGER",
                        "description": "Y coordinate"
                    },
                    "direction": {
                        "type": "STRING",
                        "description": "Scroll direction: 'up' or 'down'"
                    },
                    "amount": {
                        "type": "INTEGER",
                        "description": "Scroll amount or drag duration"
                    }
                },
                "required": ["action"]
            }
        },
        {
            "name": "keyboard_control",
            "description": "Control keyboard typing, shortcuts, and key presses.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "action": {
                        "type": "STRING",
                        "description": "Action: 'type', 'press', 'hotkey', 'hold', 'release'"
                    },
                    "text": {
                        "type": "STRING",
                        "description": "Text to type"
                    },
                    "key": {
                        "type": "STRING",
                        "description": "Key name"
                    },
                    "keys": {
                        "type": "STRING",
                        "description": "Comma-separated keys for hotkey"
                    }
                },
                "required": ["action"]
            }
        },
        {
            "name": "screen_automation",
            "description": "Advanced screen automation: find and click elements, take screenshots.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "action": {
                        "type": "STRING",
                        "description": "Action: 'screenshot', 'find_image', 'click_image', 'screen_size', 'pixel_color'"
                    },
                    "image_path": {
                        "type": "STRING",
                        "description": "Path to reference image"
                    },
                    "save_path": {
                        "type": "STRING",
                        "description": "Path to save screenshot"
                    },
                    "region": {
                        "type": "STRING",
                        "description": "Region as 'x,y,width,height'"
                    }
                },
                "required": ["action"]
            }
        },
        
        # PDF Handler
        {
            "name": "read_pdf",
            "description": "Read and extract text from PDF files.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "file_path": {
                        "type": "STRING",
                        "description": "Path to PDF file"
                    }
                },
                "required": ["file_path"]
            }
        },
        {
            "name": "extract_pdf_text",
            "description": "Extract text from specific pages of a PDF.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "file_path": {
                        "type": "STRING",
                        "description": "Path to PDF file"
                    },
                    "page_range": {
                        "type": "STRING",
                        "description": "Page range like '1-5' (optional)"
                    }
                },
                "required": ["file_path"]
            }
        }
    ]