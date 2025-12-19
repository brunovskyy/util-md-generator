"""Interactive CLI UI module for key selection."""
import sys
import os
from typing import List, Set, Dict

# Windows console support
if sys.platform == 'win32':
    import msvcrt
else:
    import tty
    import termios


class CLIUI:
    """Handles interactive CLI interface with keyboard navigation."""
    
    def __init__(self):
        """Initialize CLI UI."""
        self.selected_indices: Set[int] = set()
        self.ordered_selection: Dict[int, int] = {}  # Maps index to selection order
        self.current_index: int = 0
    
    def clear_screen(self) -> None:
        """Clear terminal screen."""
        os.system('cls' if sys.platform == 'win32' else 'clear')
    
    def _get_key(self) -> str:
        """
        Get single keypress from user (blocking).
        
        Returns:
            Key code as string
        """
        if sys.platform == 'win32':
            # Windows - blocking wait for keypress
            while True:
                first = msvcrt.getch()
                if first in (b'\x00', b'\xe0'):  # Arrow keys
                    second = msvcrt.getch()
                    if second == b'H':
                        return 'up'
                    elif second == b'P':
                        return 'down'
                elif first == b'\r':  # Enter
                    return 'enter'
                elif first == b' ':  # Space
                    return 'space'
                elif first == b'\x1b':  # Escape
                    return 'escape'
                # Ignore other keys and continue waiting
        else:
            # Unix-like
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == '\x1b':  # Escape sequence
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':
                        ch3 = sys.stdin.read(1)
                        if ch3 == 'A':
                            return 'up'
                        elif ch3 == 'B':
                            return 'down'
                elif ch == '\r' or ch == '\n':
                    return 'enter'
                elif ch == ' ':
                    return 'space'
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ''
    
    def select_keys(self, keys: List[str], title: str = "Select CSV columns to include:") -> List[str]:
        """
        Interactive key selection UI.
        
        Args:
            keys: List of available keys
            title: Title to display
            
        Returns:
            List of selected keys
        """
        if not keys:
            return []
        
        # Initialize all as selected by default
        self.selected_indices = set(range(len(keys)))
        self.current_index = 0
        
        while True:
            self.clear_screen()
            
            # Print title
            print(f"\n{title}\n")
            print("Use ↑/↓ to navigate, SPACE to toggle, ENTER to confirm\n")
            
            # Print options
            for i, key in enumerate(keys):
                cursor = "→" if i == self.current_index else " "
                checkbox = "[✓]" if i in self.selected_indices else "[ ]"
                print(f"{cursor} {checkbox} {key}")
            
            print(f"\nSelected: {len(self.selected_indices)}/{len(keys)}")
            
            # Get user input (blocks until valid key pressed)
            key = self._get_key()
            
            if key == 'up':
                self.current_index = (self.current_index - 1) % len(keys)
            elif key == 'down':
                self.current_index = (self.current_index + 1) % len(keys)
            elif key == 'space':
                if self.current_index in self.selected_indices:
                    self.selected_indices.remove(self.current_index)
                else:
                    self.selected_indices.add(self.current_index)
            elif key == 'enter':
                if self.selected_indices:
                    return [keys[i] for i in sorted(self.selected_indices)]
                else:
                    print("\n⚠ You must select at least one column!")
                    input("Press Enter to continue...")
    
    def wait_for_enter(self, message: str = "Press ENTER to continue...") -> None:
        """
        Wait for user to press Enter.
        
        Args:
            message: Message to display
        """
        input(f"\n{message}")
    
    def show_message(self, message: str, wait: bool = False) -> None:
        """
        Display a message.
        
        Args:
            message: Message to display
            wait: If True, wait for user input
        """
        print(f"\n{message}")
        if wait:
            self.wait_for_enter()
    
    def select_keys_with_order(self, keys: List[str], title: str = "Select file naming pattern:") -> List[str]:
        """
        Interactive key selection UI with ordering support.
        Keys can be selected/deselected, and the order of selection determines their sequence.
        
        Args:
            keys: List of available keys to choose from
            title: Title to display at the top of the selection interface
            
        Returns:
            List of selected keys in the order they were selected
        """
        if not keys:
            return []
        
        # Reset selection state - start with nothing selected
        self.ordered_selection = {}
        self.current_index = 0
        next_order_number = 1
        
        while True:
            self.clear_screen()
            
            # Print title and instructions
            print(f"\n{title}\n")
            print("Use ↑/↓ to navigate, SPACE to toggle (order matters), ENTER to confirm")
            print("Selected keys will be used to build the filename in order\n")
            
            # Print options with order indicators
            for i, key in enumerate(keys):
                cursor = "→" if i == self.current_index else " "
                
                # Show order number if selected
                if i in self.ordered_selection:
                    order_num = self.ordered_selection[i]
                    checkbox = f"[{order_num}]"
                else:
                    checkbox = "[ ]"
                
                print(f"{cursor} {checkbox} {key}")
            
            # Display current selection count and preview
            selected_count = len(self.ordered_selection)
            print(f"\nSelected: {selected_count}/{len(keys)}")
            
            # Show filename preview if any keys are selected
            if self.ordered_selection:
                print("\nFilename preview:")
                ordered_keys = sorted(self.ordered_selection.items(), key=lambda x: x[1])
                preview_parts = [f"<{keys[idx]}>" for idx, _ in ordered_keys]
                print(f"  {' - '.join(preview_parts)}")
            
            # Get user input (blocks until valid key pressed)
            key_press = self._get_key()
            
            if key_press == 'up':
                self.current_index = (self.current_index - 1) % len(keys)
            elif key_press == 'down':
                self.current_index = (self.current_index + 1) % len(keys)
            elif key_press == 'space':
                if self.current_index in self.ordered_selection:
                    # Deselect: remove and recalculate order numbers
                    removed_order = self.ordered_selection[self.current_index]
                    del self.ordered_selection[self.current_index]
                    
                    # Recalculate order numbers for remaining selections
                    for idx in self.ordered_selection:
                        if self.ordered_selection[idx] > removed_order:
                            self.ordered_selection[idx] -= 1
                    
                    # Update next order number
                    next_order_number = len(self.ordered_selection) + 1
                else:
                    # Select: assign next order number
                    self.ordered_selection[self.current_index] = next_order_number
                    next_order_number += 1
            elif key_press == 'enter':
                if self.ordered_selection:
                    # Return keys in selection order
                    ordered_indices = sorted(self.ordered_selection.items(), key=lambda x: x[1])
                    return [keys[idx] for idx, _ in ordered_indices]
                else:
                    print("\n⚠ You must select at least one key for the filename!")
                    input("Press Enter to continue...")

