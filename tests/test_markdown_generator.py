"""Test suite for markdown generator."""
import pytest
from pathlib import Path
from core.markdown_generator import MarkdownGenerator, MarkdownGenerationError


def test_markdown_generator_creates_files(tmp_path):
    """Test that generator creates markdown files."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    rows = [
        {"name": "Alice", "age": "30", "city": "NYC"},
        {"name": "Bob", "age": "25", "city": "LA"}
    ]
    
    generator = MarkdownGenerator(str(output_dir), ["name", "age"])
    files_created = generator.generate_files(rows)
    
    assert files_created == 2
    assert (output_dir / "Alice.md").exists()
    assert (output_dir / "Bob.md").exists()


def test_markdown_generator_creates_valid_yaml(tmp_path):
    """Test that generated files have valid YAML frontmatter."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    rows = [{"name": "Alice", "age": "30"}]
    
    generator = MarkdownGenerator(str(output_dir), ["name", "age"])
    generator.generate_files(rows)
    
    content = (output_dir / "Alice.md").read_text()
    
    assert content.startswith("---\n")
    assert "name: Alice" in content
    assert "age: '30'" in content or "age: 30" in content
    assert content.count("---") == 2


def test_markdown_generator_sanitizes_filenames(tmp_path):
    """Test that generator sanitizes invalid characters in filenames."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    rows = [{"name": "Alice/Bob<>|:*?", "age": "30"}]
    
    generator = MarkdownGenerator(str(output_dir), ["name"])
    generator.generate_files(rows)
    
    # Should replace invalid chars with underscores
    files = list(output_dir.glob("*.md"))
    assert len(files) == 1
    assert "<" not in files[0].name
    assert ">" not in files[0].name


def test_markdown_generator_handles_duplicates(tmp_path):
    """Test that generator handles duplicate filenames."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    rows = [
        {"name": "Alice", "age": "30"},
        {"name": "Alice", "age": "25"}
    ]
    
    generator = MarkdownGenerator(str(output_dir), ["name"])
    files_created = generator.generate_files(rows)
    
    assert files_created == 2
    assert (output_dir / "Alice.md").exists()
    assert (output_dir / "Alice_1.md").exists()


def test_markdown_generator_rejects_invalid_output_dir():
    """Test that generator rejects non-existent output directory."""
    with pytest.raises(ValueError, match="does not exist"):
        MarkdownGenerator("/nonexistent/path", ["name"])


def test_markdown_generator_rejects_empty_keys(tmp_path):
    """Test that generator rejects empty key list."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    with pytest.raises(ValueError, match="cannot be empty"):
        MarkdownGenerator(str(output_dir), [])
