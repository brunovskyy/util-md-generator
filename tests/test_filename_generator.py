"""Test suite for FilenameGenerator."""
import pytest
from pathlib import Path
from utils.filename_generator import FilenameGenerator


def test_filename_generator_basic_functionality(tmp_path):
    """Test basic filename generation from ordered keys."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    naming_keys = ["department", "name"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    row = {"name": "Alice Smith", "department": "Engineering", "email": "alice@example.com"}
    filename = generator.generate_filename(row, 0)
    
    assert filename == "Engineering - Alice Smith"


def test_filename_generator_sanitizes_components(tmp_path):
    """Test that filename components are sanitized."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    naming_keys = ["title"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    row = {"title": "Report<>:with|bad*chars?"}
    filename = generator.generate_filename(row, 0)
    
    assert "<" not in filename
    assert ">" not in filename
    assert ":" not in filename
    assert "|" not in filename
    assert "*" not in filename
    assert "?" not in filename


def test_filename_generator_handles_empty_values(tmp_path):
    """Test filename generation when some naming keys have empty values."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    naming_keys = ["category", "title", "date"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    row = {"category": "Report", "title": "", "date": "2024-01-15"}
    filename = generator.generate_filename(row, 0)
    
    # Should skip empty title and join remaining values
    assert filename == "Report - 2024-01-15"


def test_filename_generator_handles_all_empty_values(tmp_path):
    """Test filename generation when all naming keys are empty."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    naming_keys = ["field1", "field2"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    row = {"field1": "", "field2": ""}
    filename = generator.generate_filename(row, 5)
    
    # Should fall back to unnamed with row index
    assert filename == "unnamed_row_6"


def test_filename_generator_ensures_uniqueness_in_memory(tmp_path):
    """Test that generator creates unique filenames for duplicates in same session."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    naming_keys = ["name"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    row = {"name": "John Doe"}
    
    filename1 = generator.generate_filename(row, 0)
    filename2 = generator.generate_filename(row, 1)
    filename3 = generator.generate_filename(row, 2)
    
    assert filename1 == "John Doe"
    assert filename2 == "John Doe - 2"
    assert filename3 == "John Doe - 3"


def test_filename_generator_checks_existing_files(tmp_path):
    """Test that generator checks for existing files on disk."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Create an existing file
    (output_dir / "Report.md").touch()
    
    naming_keys = ["title"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    row = {"title": "Report"}
    filename = generator.generate_filename(row, 0)
    
    # Should append number since file already exists
    assert filename == "Report - 2"


def test_filename_generator_preserves_order(tmp_path):
    """Test that filename components follow the order of naming keys."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    naming_keys = ["year", "month", "title"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    row = {"title": "Budget Report", "month": "January", "year": "2024"}
    filename = generator.generate_filename(row, 0)
    
    assert filename == "2024 - January - Budget Report"


def test_filename_generator_rejects_empty_naming_keys(tmp_path):
    """Test that generator rejects empty naming keys list."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    with pytest.raises(ValueError, match="naming_keys cannot be empty"):
        FilenameGenerator([], output_dir)


def test_filename_generator_rejects_invalid_output_dir():
    """Test that generator rejects non-existent output directory."""
    with pytest.raises(ValueError, match="does not exist"):
        FilenameGenerator(["name"], Path("/nonexistent/path"))


def test_filename_generator_limits_length(tmp_path):
    """Test that generator limits filename length."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    naming_keys = ["description"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    # Create a very long description
    long_text = "x" * 300
    row = {"description": long_text}
    
    filename = generator.generate_filename(row, 0)
    
    # Should be limited to 200 characters
    assert len(filename) <= 200


def test_filename_generator_reset(tmp_path):
    """Test that reset clears internal state."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    naming_keys = ["name"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    row = {"name": "Test"}
    filename1 = generator.generate_filename(row, 0)
    
    generator.reset()
    
    filename2 = generator.generate_filename(row, 0)
    
    # After reset, should get same filename again
    assert filename1 == "Test"
    assert filename2 == "Test"


def test_filename_generator_multiple_ordered_keys(tmp_path):
    """Test filename generation with multiple ordered keys in specific sequence."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    naming_keys = ["finding_type", "source", "issue_date"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    row = {
        "finding_type": "Critical",
        "source": "Audit Report",
        "issue_date": "2024-12-19",
        "description": "Some long description",
        "status": "Open"
    }
    
    filename = generator.generate_filename(row, 0)
    
    # Should only use the naming keys in specified order
    assert filename == "Critical - Audit Report - 2024-12-19"
    assert "Some long description" not in filename
    assert "Open" not in filename
