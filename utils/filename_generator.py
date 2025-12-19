"""Filename generation utility with pattern-based naming and uniqueness handling."""
import re
from pathlib import Path
from typing import List, Dict, Any, Set


class FilenameGenerator:
    """Generates unique filenames based on ordered key patterns."""
    
    def __init__(self, naming_keys: List[str], output_directory: Path):
        """
        Initialize filename generator.
        
        Args:
            naming_keys: Ordered list of CSV keys to use for filename construction
            output_directory: Directory where files will be created (for uniqueness checking)
            
        Raises:
            ValueError: If naming_keys is empty or output_directory doesn't exist
        """
        if not naming_keys:
            raise ValueError("naming_keys cannot be empty")
        
        if not output_directory.exists():
            raise ValueError(f"Output directory does not exist: {output_directory}")
        
        if not output_directory.is_dir():
            raise ValueError(f"Output path is not a directory: {output_directory}")
        
        self.naming_keys = naming_keys
        self.output_directory = output_directory
        self.generated_filenames: Set[str] = set()
        self.filename_counts: Dict[str, int] = {}
    
    def _sanitize_filename_component(self, text: str) -> str:
        """
        Sanitize a single component of the filename.
        
        Args:
            text: Raw text to sanitize
            
        Returns:
            Sanitized text safe for use in filenames
        """
        if not text or not text.strip():
            return ""
        
        # Remove invalid Windows filename characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', text)
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f]', '', sanitized)
        
        # Trim whitespace and dots
        sanitized = sanitized.strip('. ')
        
        return sanitized
    
    def _build_base_filename(self, row: Dict[str, Any]) -> str:
        """
        Build base filename from row data using naming keys in order.
        
        Args:
            row: Data row containing values for the naming keys
            
        Returns:
            Base filename constructed from naming key values
        """
        filename_components = []
        
        # Extract values for each naming key in order
        for key in self.naming_keys:
            value = row.get(key, '').strip()
            
            if value:
                sanitized_component = self._sanitize_filename_component(value)
                if sanitized_component:
                    filename_components.append(sanitized_component)
        
        # Join components with separator
        if filename_components:
            base_filename = ' - '.join(filename_components)
        else:
            # Fallback if all naming keys are empty
            base_filename = "unnamed"
        
        # Limit total length to prevent filesystem issues
        if len(base_filename) > 200:
            base_filename = base_filename[:200].strip()
        
        return base_filename
    
    def _ensure_unique_filename(self, base_filename: str) -> str:
        """
        Ensure filename is unique by appending sequential numbers if needed.
        
        Args:
            base_filename: Base filename without extension
            
        Returns:
            Unique filename (may have sequential number appended)
        """
        # Check if this exact filename already exists in current session
        if base_filename not in self.generated_filenames:
            # Also check if file exists on disk
            file_path = self.output_directory / f"{base_filename}.md"
            if not file_path.exists():
                self.generated_filenames.add(base_filename)
                return base_filename
        
        # Filename exists, need to append number
        if base_filename not in self.filename_counts:
            self.filename_counts[base_filename] = 1
        
        # Find next available number
        while True:
            self.filename_counts[base_filename] += 1
            numbered_filename = f"{base_filename} - {self.filename_counts[base_filename]}"
            
            # Check both in-memory tracking and filesystem
            if numbered_filename not in self.generated_filenames:
                file_path = self.output_directory / f"{numbered_filename}.md"
                if not file_path.exists():
                    self.generated_filenames.add(numbered_filename)
                    return numbered_filename
    
    def generate_filename(self, row: Dict[str, Any], row_index: int = 0) -> str:
        """
        Generate a unique filename for the given row.
        
        Args:
            row: Data row containing values for naming keys
            row_index: Index of row (used for fallback naming if needed)
            
        Returns:
            Complete unique filename without extension
        """
        base_filename = self._build_base_filename(row)
        
        # If base filename is just "unnamed", add row index for differentiation
        if base_filename == "unnamed":
            base_filename = f"unnamed_row_{row_index + 1}"
        
        unique_filename = self._ensure_unique_filename(base_filename)
        return unique_filename
    
    def reset(self) -> None:
        """
        Reset internal state tracking.
        Useful if generating a new batch of files.
        """
        self.generated_filenames.clear()
        self.filename_counts.clear()
