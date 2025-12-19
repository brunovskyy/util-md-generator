"""Windows file and folder picker utilities."""
import sys
from typing import Optional
from pathlib import Path


def pick_csv_file() -> Optional[str]:
    """
    Open Windows file picker for CSV file selection.
    
    Returns:
        Selected file path or None if cancelled
    """
    if sys.platform != 'win32':
        raise RuntimeError("This application only works on Windows")
    
    try:
        import win32gui
        import win32con
        from win32com.shell import shell, shellcon
        
        # Create file dialog
        filters = "CSV Files (*.csv)\0*.csv\0All Files (*.*)\0*.*\0"
        custom_filter = None
        file_name = None
        flags = (
            win32con.OFN_EXPLORER |
            win32con.OFN_FILEMUSTEXIST |
            win32con.OFN_HIDEREADONLY
        )
        
        try:
            file_name, custom_filter, flags = win32gui.GetOpenFileNameW(
                InitialDir=str(Path.home()),
                Flags=flags,
                Filter=filters,
                Title="Select CSV File"
            )
        except Exception:
            # User cancelled
            return None
        
        if file_name:
            return file_name
        return None
        
    except ImportError:
        raise RuntimeError("pywin32 is required for Windows file dialogs")


def pick_folder() -> Optional[str]:
    """
    Open Windows folder picker for output directory selection.
    
    Returns:
        Selected folder path or None if cancelled
    """
    if sys.platform != 'win32':
        raise RuntimeError("This application only works on Windows")
    
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        # Create root window and hide it
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        # Open folder dialog
        folder_path = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir=str(Path.home())
        )
        
        # Destroy root window
        root.destroy()
        
        return folder_path if folder_path else None
        
    except ImportError:
        raise RuntimeError("tkinter is required for folder dialogs")
