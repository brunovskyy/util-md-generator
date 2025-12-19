"""Integration tests for MarkdownGenerator with FilenameGenerator."""
import pytest
from pathlib import Path
from core.markdown_generator import MarkdownGenerator


def test_markdown_generator_with_naming_keys(tmp_path):
    """Test that MarkdownGenerator uses naming keys for filename generation."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    rows = [
        {"department": "Engineering", "name": "Alice", "email": "alice@example.com"},
        {"department": "Sales", "name": "Bob", "email": "bob@example.com"}
    ]
    
    # Use naming keys in specific order: name, then department
    naming_keys = ["name", "department"]
    generator = MarkdownGenerator(str(output_dir), ["name", "email"], naming_keys)
    files_created = generator.generate_files(rows)
    
    assert files_created == 2
    assert (output_dir / "Alice - Engineering.md").exists()
    assert (output_dir / "Bob - Sales.md").exists()


def test_markdown_generator_with_naming_keys_handles_duplicates(tmp_path):
    """Test filename uniqueness with naming keys."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    rows = [
        {"category": "Report", "title": "Annual", "year": "2024"},
        {"category": "Report", "title": "Annual", "year": "2024"},
        {"category": "Report", "title": "Annual", "year": "2024"}
    ]
    
    naming_keys = ["category", "title"]
    generator = MarkdownGenerator(str(output_dir), ["category", "title", "year"], naming_keys)
    files_created = generator.generate_files(rows)
    
    assert files_created == 3
    assert (output_dir / "Report - Annual.md").exists()
    assert (output_dir / "Report - Annual - 2.md").exists()
    assert (output_dir / "Report - Annual - 3.md").exists()


def test_markdown_generator_with_single_naming_key(tmp_path):
    """Test filename generation with single naming key."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    rows = [
        {"id": "12345", "name": "Alice", "status": "Active"},
        {"id": "67890", "name": "Bob", "status": "Inactive"}
    ]
    
    naming_keys = ["id"]
    generator = MarkdownGenerator(str(output_dir), ["id", "name", "status"], naming_keys)
    files_created = generator.generate_files(rows)
    
    assert files_created == 2
    assert (output_dir / "12345.md").exists()
    assert (output_dir / "67890.md").exists()


def test_markdown_generator_with_many_naming_keys(tmp_path):
    """Test filename generation with multiple naming keys."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    rows = [
        {
            "year": "2024",
            "month": "December",
            "type": "Audit",
            "severity": "Critical",
            "id": "001"
        }
    ]
    
    naming_keys = ["year", "month", "type", "severity"]
    generator = MarkdownGenerator(
        str(output_dir),
        ["year", "month", "type", "severity", "id"],
        naming_keys
    )
    files_created = generator.generate_files(rows)
    
    assert files_created == 1
    assert (output_dir / "2024 - December - Audit - Critical.md").exists()


def test_markdown_generator_without_naming_keys_uses_legacy(tmp_path):
    """Test that MarkdownGenerator falls back to legacy method when no naming keys provided."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    rows = [
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": "bob@example.com"}
    ]
    
    # No naming_keys parameter - should use legacy method
    generator = MarkdownGenerator(str(output_dir), ["name", "email"])
    files_created = generator.generate_files(rows)
    
    assert files_created == 2
    # Legacy method uses first selected key
    assert (output_dir / "Alice.md").exists()
    assert (output_dir / "Bob.md").exists()


def test_markdown_generator_with_empty_naming_key_values(tmp_path):
    """Test handling of empty values in naming keys."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    rows = [
        {"prefix": "Dr", "name": "Smith", "suffix": ""},
        {"prefix": "", "name": "Jones", "suffix": "Jr"}
    ]
    
    naming_keys = ["prefix", "name", "suffix"]
    generator = MarkdownGenerator(str(output_dir), ["prefix", "name", "suffix"], naming_keys)
    files_created = generator.generate_files(rows)
    
    assert files_created == 2
    # Empty values should be skipped in filename
    assert (output_dir / "Dr - Smith.md").exists()
    assert (output_dir / "Jones - Jr.md").exists()


def test_markdown_generator_preserves_frontmatter_regardless_of_naming(tmp_path):
    """Test that frontmatter includes selected_keys, not just naming_keys."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    rows = [
        {
            "id": "001",
            "name": "Alice",
            "email": "alice@example.com",
            "department": "Engineering"
        }
    ]
    
    # Only use 'id' for filename, but include all fields in frontmatter
    naming_keys = ["id"]
    selected_keys = ["id", "name", "email", "department"]
    generator = MarkdownGenerator(str(output_dir), selected_keys, naming_keys)
    generator.generate_files(rows)
    
    content = (output_dir / "001.md").read_text()
    
    # All selected keys should be in frontmatter
    assert "id:" in content or "id :" in content
    assert "name:" in content or "name :" in content
    assert "email:" in content or "email :" in content
    assert "department:" in content or "department :" in content
