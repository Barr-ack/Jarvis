"""
Handlers package initialization
"""

from .file_operations import FileOperations
from .system_control import SystemControl
from .communication import Communication
from .automation import Automation
from .advanced_features import AdvancedFeatures
from .input_control import InputControl
from .pdf_handler import PDFHandler
from .tool_declarations import get_all_tool_declarations

__all__ = [
    'FileOperations',
    'SystemControl',
    'Communication',
    'Automation',
    'AdvancedFeatures',
    'InputControl',
    'PDFHandler',
    'get_all_tool_declarations'
]