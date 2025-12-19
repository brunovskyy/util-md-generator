"""Test suite for CSV parser."""
import pytest
from pathlib import Path
from core.csv_parser import CSVParser, CSVParseError


def test_csv_parser_loads_valid_file(tmp_path):
    """Test that parser loads a valid CSV file."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA")
    
    parser = CSVParser(str(csv_file))
    
    assert parser.get_headers() == ["name", "age", "city"]
    assert len(parser.get_rows()) == 2
    assert parser.get_row_count() == 2


def test_csv_parser_handles_empty_values(tmp_path):
    """Test parser handles empty values correctly."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("name,age,city\nAlice,,NYC\n,25,")
    
    parser = CSVParser(str(csv_file))
    rows = parser.get_rows()
    
    assert rows[0]["age"] == ""
    assert rows[1]["name"] == ""
    assert rows[1]["city"] == ""


def test_csv_parser_rejects_non_csv(tmp_path):
    """Test parser rejects non-CSV files."""
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("not a csv")
    
    with pytest.raises(CSVParseError, match="must be a CSV file"):
        CSVParser(str(txt_file))


def test_csv_parser_rejects_missing_file():
    """Test parser rejects non-existent files."""
    with pytest.raises(FileNotFoundError):
        CSVParser("nonexistent.csv")


def test_csv_parser_rejects_no_data(tmp_path):
    """Test parser rejects CSV with headers but no data."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("name,age,city\n")
    
    with pytest.raises(CSVParseError, match="no data rows"):
        CSVParser(str(csv_file))
