"""Test suite for dynamic ignored character configuration in FilenameGenerator."""
import pytest
from pathlib import Path
from utils.filename_generator import FilenameGenerator
from config import IGNORED_CHARACTERS_FOR_NAMING
import config.naming_config


def test_ignored_characters_cleaned_from_values(tmp_path):
    """Test that characters in IGNORED_CHARACTERS_FOR_NAMING are removed from values."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    naming_keys = ["finding_type", "severity"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    # Values with brackets (which are in default ignored list)
    row = {
        "finding_type": "[[Minor]]",
        "severity": "[[Low]]"
    }
    
    filename = generator.generate_filename(row, 0)
    
    # Brackets should be removed, leaving just the text
    assert filename == "Minor - Low"
    assert "[" not in filename
    assert "]" not in filename


def test_ignored_characters_with_mixed_content(tmp_path):
    """Test ignored characters mixed with other content."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    naming_keys = ["title"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    row = {"title": "[Important] Security [Alert]"}
    filename = generator.generate_filename(row, 0)
    
    # Brackets removed, spaces preserved
    assert filename == "Important Security Alert"


def test_multiple_ignored_characters(tmp_path):
    """Test that all characters in the ignored list are removed."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Temporarily modify config to test multiple characters
    original_ignored = config.naming_config.IGNORED_CHARACTERS_FOR_NAMING.copy()
    try:
        config.naming_config.IGNORED_CHARACTERS_FOR_NAMING.extend(['(', ')', '{', '}'])
        
        naming_keys = ["description"]
        generator = FilenameGenerator(naming_keys, output_dir)
        
        row = {"description": "[[Test]] (with) {various} brackets"}
        filename = generator.generate_filename(row, 0)
        
        # All bracket types should be removed
        assert filename == "Test with various brackets"
        assert "[" not in filename
        assert "]" not in filename
        assert "(" not in filename
        assert ")" not in filename
        assert "{" not in filename
        assert "}" not in filename
    finally:
        # Restore original config
        config.naming_config.IGNORED_CHARACTERS_FOR_NAMING = original_ignored


def test_ignored_characters_empty_list(tmp_path):
    """Test behavior when ignored characters list is empty."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Temporarily clear the ignored list
    original_ignored = config.naming_config.IGNORED_CHARACTERS_FOR_NAMING.copy()
    try:
        config.naming_config.IGNORED_CHARACTERS_FOR_NAMING.clear()
        
        naming_keys = ["name"]
        generator = FilenameGenerator(naming_keys, output_dir)
        
        row = {"name": "[[Test]]"}
        filename = generator.generate_filename(row, 0)
        
        # Brackets should NOT be removed (but may be sanitized by filesystem rules)
        # The double brackets will be sanitized to underscores due to being invalid chars
        assert "Test" in filename
    finally:
        # Restore original config
        config.naming_config.IGNORED_CHARACTERS_FOR_NAMING = original_ignored


def test_ignored_characters_do_not_affect_sanitization(tmp_path):
    """Test that filesystem-unsafe characters are still sanitized after cleaning."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    naming_keys = ["filename"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    # Combine ignored chars with unsafe filesystem chars
    row = {"filename": "[[test]]:invalid|name"}
    filename = generator.generate_filename(row, 0)
    
    # Brackets removed by cleaning, unsafe chars sanitized
    assert "[" not in filename
    assert "]" not in filename
    assert ":" not in filename
    assert "|" not in filename
    assert "test" in filename
    assert "invalid" in filename
    assert "name" in filename


def test_cleaning_preserves_word_boundaries(tmp_path):
    """Test that removing ignored characters doesn't incorrectly join words."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    naming_keys = ["title"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    row = {"title": "[Word1][Word2] [Word3]"}
    filename = generator.generate_filename(row, 0)
    
    # Should result in "Word1Word2 Word3" (brackets removed, space preserved)
    assert "Word1Word2 Word3" == filename


def test_ignored_characters_with_empty_result(tmp_path):
    """Test behavior when cleaning leaves an empty string."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    naming_keys = ["value"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    # Value contains only ignored characters
    row = {"value": "[[]]"}
    filename = generator.generate_filename(row, 0)
    
    # Should fall back to unnamed
    assert filename == "unnamed_row_1"


def test_ignored_characters_order_independence(tmp_path):
    """Test that character order in ignored list doesn't matter."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    naming_keys = ["text"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    row = {"text": "]]][[[Text[[["}
    filename = generator.generate_filename(row, 0)
    
    # All brackets removed regardless of order
    assert filename == "Text"


def test_config_changes_affect_output(tmp_path):
    """Test that changing the config variable changes the output without code changes."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    original_ignored = config.naming_config.IGNORED_CHARACTERS_FOR_NAMING.copy()
    
    try:
        # Test with default config
        naming_keys = ["tag"]
        generator1 = FilenameGenerator(naming_keys, output_dir)
        row = {"tag": "##HashTag##"}
        filename1 = generator1.generate_filename(row, 0)
        
        # '#' not in default ignored list, so it gets sanitized but stays
        assert "HashTag" in filename1
        
        # Now add '#' to ignored list
        config.naming_config.IGNORED_CHARACTERS_FOR_NAMING.append('#')
        
        generator2 = FilenameGenerator(naming_keys, output_dir)
        filename2 = generator2.generate_filename(row, 0)
        
        # Now '#' should be completely removed
        assert filename2 == "HashTag"
        assert "#" not in filename2
        
    finally:
        # Restore original config
        config.naming_config.IGNORED_CHARACTERS_FOR_NAMING = original_ignored


def test_unicode_ignored_characters(tmp_path):
    """Test that unicode characters can be in the ignored list."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    original_ignored = config.naming_config.IGNORED_CHARACTERS_FOR_NAMING.copy()
    
    try:
        # Add unicode characters to ignored list
        config.naming_config.IGNORED_CHARACTERS_FOR_NAMING.extend(['•', '→', '★'])
        
        naming_keys = ["item"]
        generator = FilenameGenerator(naming_keys, output_dir)
        
        row = {"item": "• Important → ★ Item"}
        filename = generator.generate_filename(row, 0)
        
        # Unicode symbols should be removed (may leave extra spaces)
        assert "•" not in filename
        assert "→" not in filename
        assert "★" not in filename
        assert "Important" in filename
        assert "Item" in filename
        
    finally:
        config.naming_config.IGNORED_CHARACTERS_FOR_NAMING = original_ignored


def test_conceptual_example_from_requirements(tmp_path):
    """Test the exact conceptual example from the requirements."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    naming_keys = ["finding type"]
    generator = FilenameGenerator(naming_keys, output_dir)
    
    # Exact example from requirements
    row = {"finding type": "[[Minor]]"}
    filename = generator.generate_filename(row, 0)
    
    # With default config containing '[' and ']', output should be "Minor"
    assert filename == "Minor"
