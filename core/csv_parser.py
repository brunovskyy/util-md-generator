"""CSV parsing and validation module."""
import csv
from pathlib import Path
from typing import List, Dict, Any


class CSVParseError(Exception):
    """Raised when CSV parsing fails."""
    pass


class CSVParser:
    """Handles CSV file parsing and data extraction."""
    
    def __init__(self, file_path: str):
        """
        Initialize CSV parser.
        
        Args:
            file_path: Path to CSV file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            CSVParseError: If file is not a valid CSV
        """
        self.file_path = Path(file_path)
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        if self.file_path.suffix.lower() != '.csv':
            raise CSVParseError(f"File must be a CSV file: {file_path}")
        
        self.headers: List[str] = []
        self.rows: List[Dict[str, Any]] = []
        self._load()
    
    def _load(self) -> None:
        """
        Load and parse CSV file.
        
        Raises:
            CSVParseError: If parsing fails
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                
                # Extract headers
                if reader.fieldnames is None:
                    raise CSVParseError("CSV file has no headers")
                
                self.headers = [h.strip() for h in reader.fieldnames if h]
                
                if not self.headers:
                    raise CSVParseError("CSV file has no valid headers")
                
                # Extract rows
                for row_num, row in enumerate(reader, start=2):
                    cleaned_row = {
                        key.strip(): value.strip() if value else ""
                        for key, value in row.items()
                        if key and key.strip()
                    }
                    self.rows.append(cleaned_row)
                
                if not self.rows:
                    raise CSVParseError("CSV file contains no data rows")
                    
        except csv.Error as e:
            raise CSVParseError(f"Failed to parse CSV: {e}")
        except Exception as e:
            raise CSVParseError(f"Error reading CSV file: {e}")
    
    def get_headers(self) -> List[str]:
        """
        Get list of CSV column headers.
        
        Returns:
            List of header names
        """
        return self.headers.copy()
    
    def get_rows(self) -> List[Dict[str, Any]]:
        """
        Get all data rows.
        
        Returns:
            List of dictionaries, each representing a row
        """
        return self.rows.copy()
    
    def get_row_count(self) -> int:
        """
        Get number of data rows.
        
        Returns:
            Row count
        """
        return len(self.rows)
