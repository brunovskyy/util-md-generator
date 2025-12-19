"""Test suite for CLIUI ordered key selection."""
import pytest
from unittest.mock import Mock, patch
from core.cli_ui import CLIUI


def test_select_keys_with_order_basic(monkeypatch):
    """Test basic ordered key selection."""
    ui = CLIUI()
    keys = ["name", "email", "department"]
    
    # Simulate: select index 0, then index 2, then press enter
    key_presses = ['space', 'down', 'down', 'space', 'enter']
    key_iter = iter(key_presses)
    
    monkeypatch.setattr(ui, '_get_key', lambda: next(key_iter))
    monkeypatch.setattr(ui, 'clear_screen', lambda: None)
    
    result = ui.select_keys_with_order(keys, "Test Selection")
    
    # Should return keys in selection order
    assert result == ["name", "department"]


def test_select_keys_with_order_preserves_selection_order(monkeypatch):
    """Test that selection order is preserved correctly."""
    ui = CLIUI()
    keys = ["field1", "field2", "field3", "field4"]
    
    # Simulate: select index 3, then 0, then 2 (skip 1), then enter
    key_presses = [
        'down', 'down', 'down', 'space',  # Select field4 (order 1)
        'up', 'up', 'up', 'space',         # Select field1 (order 2)
        'down', 'down', 'space',           # Select field3 (order 3)
        'enter'
    ]
    key_iter = iter(key_presses)
    
    monkeypatch.setattr(ui, '_get_key', lambda: next(key_iter))
    monkeypatch.setattr(ui, 'clear_screen', lambda: None)
    
    result = ui.select_keys_with_order(keys, "Test Selection")
    
    # Should return in the order they were selected
    assert result == ["field4", "field1", "field3"]


def test_select_keys_with_order_deselection_reorders(monkeypatch):
    """Test that deselecting a key recalculates order numbers."""
    ui = CLIUI()
    keys = ["a", "b", "c"]
    
    # Simulate: select all three, then deselect middle one
    key_presses = [
        'space',           # Select a (order 1)
        'down', 'space',   # Select b (order 2)
        'down', 'space',   # Select c (order 3)
        'up', 'space',     # Deselect b
        'enter'
    ]
    key_iter = iter(key_presses)
    
    monkeypatch.setattr(ui, '_get_key', lambda: next(key_iter))
    monkeypatch.setattr(ui, 'clear_screen', lambda: None)
    
    result = ui.select_keys_with_order(keys, "Test Selection")
    
    # Should have a and c, with recalculated order (1, 2)
    assert result == ["a", "c"]


def test_select_keys_with_order_toggle_same_key(monkeypatch):
    """Test toggling the same key multiple times."""
    ui = CLIUI()
    keys = ["key1", "key2"]
    
    # Simulate: select key1, deselect it, select it again, then enter
    key_presses = [
        'space',   # Select key1 (order 1)
        'space',   # Deselect key1
        'space',   # Select key1 again (order 1)
        'enter'
    ]
    key_iter = iter(key_presses)
    
    monkeypatch.setattr(ui, '_get_key', lambda: next(key_iter))
    monkeypatch.setattr(ui, 'clear_screen', lambda: None)
    
    result = ui.select_keys_with_order(keys, "Test Selection")
    
    assert result == ["key1"]


def test_select_keys_with_order_empty_list():
    """Test handling of empty key list."""
    ui = CLIUI()
    
    result = ui.select_keys_with_order([], "Test Selection")
    
    assert result == []


def test_select_keys_with_order_requires_at_least_one(monkeypatch, capsys):
    """Test that at least one key must be selected."""
    ui = CLIUI()
    keys = ["key1", "key2"]
    
    # Simulate: press enter without selecting anything, then select one and confirm
    key_presses = ['enter', 'space', 'enter']
    key_iter = iter(key_presses)
    
    # Mock input for the warning message
    input_called = [False]
    
    def mock_input(prompt):
        input_called[0] = True
        return ""
    
    monkeypatch.setattr(ui, '_get_key', lambda: next(key_iter))
    monkeypatch.setattr(ui, 'clear_screen', lambda: None)
    monkeypatch.setattr('builtins.input', mock_input)
    
    result = ui.select_keys_with_order(keys, "Test Selection")
    
    # Should show warning and require at least one selection
    assert input_called[0]  # Input was called for warning
    assert result == ["key1"]


def test_select_keys_with_order_navigation_wraps(monkeypatch):
    """Test that up/down navigation wraps around."""
    ui = CLIUI()
    keys = ["first", "middle", "last"]
    
    # Simulate: go up from first (should wrap to last), then select
    key_presses = ['up', 'space', 'enter']
    key_iter = iter(key_presses)
    
    monkeypatch.setattr(ui, '_get_key', lambda: next(key_iter))
    monkeypatch.setattr(ui, 'clear_screen', lambda: None)
    
    result = ui.select_keys_with_order(keys, "Test Selection")
    
    # Should have selected "last" due to wrap-around
    assert result == ["last"]
