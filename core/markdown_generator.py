"""Markdown file generation with YAML frontmatter."""
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

from utils.filename_generator import FilenameGenerator


class MarkdownGenerationError(Exception):
    """Raised when markdown generation fails."""
    pass


class MarkdownGenerator:
    """Generates Markdown files with YAML frontmatter."""
    
    def __init__(self, output_dir: str, selected_keys: List[str], naming_keys: Optional[List[str]] = None):
        """
        Initialize markdown generator.
        
        Args:
            output_dir: Directory to save markdown files
            selected_keys: CSV columns to include in frontmatter
            naming_keys: Ordered list of keys to use for filename generation (optional)
            
        Raises:
            ValueError: If output_dir doesn't exist or selected_keys is empty
        """
        self.output_dir = Path(output_dir)
        
        if not self.output_dir.exists():
            raise ValueError(f"Output directory does not exist: {output_dir}")
        
        if not self.output_dir.is_dir():
            raise ValueError(f"Output path is not a directory: {output_dir}")
        
        if not selected_keys:
            raise ValueError("selected_keys cannot be empty")
        
        self.selected_keys = selected_keys
        self.naming_keys = naming_keys if naming_keys else []
        self.files_created = 0
        
        # Initialize filename generator if naming keys are provided
        if self.naming_keys:
            self.filename_generator = FilenameGenerator(self.naming_keys, self.output_dir)
        else:
            self.filename_generator = None
    
    def _escape_yaml_value(self, value: Any) -> Any:
        """
        Escape value for YAML if needed.
        
        Args:
            value: Value to escape
            
        Returns:
            Escaped value
        """
        if value is None or value == '':
            return ''
        
        value_str = str(value).strip()
        
        # Check if value needs quoting
        if not value_str:
            return ''
        
        # Let PyYAML handle the escaping
        return value_str
    
    def _create_frontmatter(self, row: Dict[str, Any]) -> str:
        """
        Create YAML frontmatter from row data.
        
        Args:
            row: Data row
            
        Returns:
            YAML frontmatter string
        """
        # Build frontmatter dict
        frontmatter = {}
        for key in self.selected_keys:
            value = row.get(key, '')
            frontmatter[key] = self._escape_yaml_value(value)
        
        # Convert to YAML
        yaml_content = yaml.dump(
            frontmatter,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False
        )
        
        return f"---\n{yaml_content}---\n"
    
    def generate_files(self, rows: List[Dict[str, Any]]) -> int:
        """
        Generate markdown files for all rows.
        
        Args:
            rows: List of data rows
            
        Returns:
            Number of files created
            
        Raises:
            MarkdownGenerationError: If generation fails
        """
        if not rows:
            raise MarkdownGenerationError("No rows to generate")
        
        self.files_created = 0
        
        # Use FilenameGenerator if available, otherwise use legacy method
        if self.filename_generator:
            # Reset generator state for new batch
            self.filename_generator.reset()
            
            for row_index, row in enumerate(rows):
                try:
                    # Generate unique filename using the filename generator
                    filename = self.filename_generator.generate_filename(row, row_index)
                    
                    # Create full path
                    file_path = self.output_dir / f"{filename}.md"
                    
                    # Generate content
                    content = self._create_frontmatter(row)
                    
                    # Write file
                    file_path.write_text(content, encoding='utf-8')
                    self.files_created += 1
                    
                except Exception as e:
                    raise MarkdownGenerationError(f"Failed to generate file for row {row_index + 1}: {e}")
        else:
            raise MarkdownGenerationError("No naming keys provided - cannot generate filenames")
        
        return self.files_created
    
    def get_files_created(self) -> int:
        """
        Get count of files created.
        
        Returns:
            Number of files created
        """
        return self.files_created
