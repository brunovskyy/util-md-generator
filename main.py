"""CSV to Obsidian Markdown Generator CLI Application."""
import sys
from pathlib import Path

from core.csv_parser import CSVParser, CSVParseError
from core.cli_ui import CLIUI
from core.markdown_generator import MarkdownGenerator, MarkdownGenerationError
from utils.file_picker import pick_csv_file, pick_folder


def main():
    """Main application entry point."""
    
    # Initialize UI
    ui = CLIUI()
    ui.clear_screen()
    
    # Show intro
    print("=" * 60)
    print("  CSV → Obsidian Markdown Generator")
    print("=" * 60)
    print("\nConvert CSV rows into individual Markdown files")
    print("with YAML frontmatter for Obsidian.\n")
    
    try:
        # Step 1: CSV File Selection
        print("Step 1: Select CSV File")
        ui.wait_for_enter("Press ENTER to select a CSV file...")
        
        csv_file = pick_csv_file()
        if not csv_file:
            print("\n❌ No file selected. Exiting.")
            return 1
        
        print(f"\n✓ Selected: {csv_file}")
        
        # Step 2: Load and Parse CSV
        print("\nStep 2: Loading CSV...")
        try:
            parser = CSVParser(csv_file)
            headers = parser.get_headers()
            rows = parser.get_rows()
            print(f"✓ Loaded {len(rows)} rows with {len(headers)} columns")
        except (FileNotFoundError, CSVParseError) as e:
            print(f"\n❌ Error: {e}")
            return 1
        
        ui.wait_for_enter("\nPress ENTER to select columns...")
        
        # Step 3: Key Selection
        selected_keys = ui.select_keys(
            headers,
            "Select CSV columns to include in Markdown frontmatter:"
        )
        
        if not selected_keys:
            print("\n❌ No columns selected. Exiting.")
            return 1
        
        ui.clear_screen()
        print("\n✓ Selected columns:")
        for key in selected_keys:
            print(f"  - {key}")
        
        ui.wait_for_enter("\nPress ENTER to configure file naming pattern...")
        
        # Step 4: File Naming Pattern Selection
        naming_keys = ui.select_keys_with_order(
            selected_keys,
            "Select keys for filename pattern (order matters):"
        )
        
        if not naming_keys:
            print("\n❌ No naming keys selected. Exiting.")
            return 1
        
        ui.clear_screen()
        print("\n✓ File naming pattern:")
        for idx, key in enumerate(naming_keys, 1):
            print(f"  {idx}. {key}")
        
        # Step 5: Output Folder Selection
        print("\nStep 5: Select Output Folder")
        ui.wait_for_enter("Press ENTER to select output folder...")
        
        output_dir = pick_folder()
        if not output_dir:
            print("\n❌ No folder selected. Exiting.")
            return 1
        
        print(f"\n✓ Output folder: {output_dir}")
        
        # Step 6: Generate Markdown Files
        print("\nStep 6: Generating Markdown files...")
        try:
            generator = MarkdownGenerator(output_dir, selected_keys, naming_keys)
            files_created = generator.generate_files(rows)
            
            # Step 7: Completion
            ui.clear_screen()
            print("\n" + "=" * 60)
            print("  ✓ Generation Complete!")
            print("=" * 60)
            print(f"\nFiles created: {files_created}")
            print(f"Output folder: {output_dir}")
            print("\nYou can now import these files into Obsidian.")
            print("=" * 60 + "\n")
            
        except (MarkdownGenerationError, ValueError) as e:
            print(f"\n❌ Error generating files: {e}")
            return 1
        
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
