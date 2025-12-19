# CSV → Obsidian Markdown Generator

A Windows-compatible CLI application that converts CSV files into individual Markdown files with YAML frontmatter, perfect for importing into Obsidian.

## Features

- Interactive CLI with keyboard navigation
- Native Windows file/folder picker dialogs
- Column selection with visual toggle interface
- **Custom filename pattern selection with ordering support**
- YAML frontmatter generation for Obsidian properties
- Automatic filename sanitization
- Intelligent duplicate filename handling with sequential numbering
- Production-grade error handling and validation

## Requirements

- Windows OS
- Python 3.14+ (managed via UV)
- UV package manager

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Install dependencies using UV:

```powershell
uv sync
```

## Usage

Run the application:

```powershell
uv run main.py
```

### Workflow

1. **Select CSV File**: Press Enter to open file picker and select your CSV file
2. **Review Data**: The app loads and validates your CSV
3. **Select Columns for Frontmatter**: Use arrow keys (↑/↓) to navigate, Space to toggle columns on/off, Enter to confirm
4. **Select File Naming Pattern**: Choose which columns to use for filenames and in what order (order matters!)
   - Previously selected columns are shown
   - Press Space to select/deselect (selection order determines position in filename)
   - Each selected column shows its order number: `[1]`, `[2]`, etc.
   - Live filename preview shows how files will be named
5. **Select Output Folder**: Press Enter to choose where markdown files will be saved
6. **Generate**: Files are created automatically with YAML frontmatter and custom filenames
7. **Done**: Summary shows number of files created and output location

### Example

Input CSV (`audit_findings.csv`):
```csv
finding_type,severity,source,issue_date,description
Security Vulnerability,Critical,External Audit,2024-12-15,SQL Injection risk
Configuration Issue,Medium,Internal Review,2024-12-10,Weak password policy
Compliance Gap,High,Regulatory Audit,2024-12-12,Missing encryption
```

**Step 3 - Select columns for frontmatter:**
Select: `finding_type`, `severity`, `source`, `issue_date`, `description`

**Step 4 - Select file naming pattern (order matters):**
Select in order:
1. `finding_type`
2. `severity`
3. `issue_date`

**Output files:**
- `Security Vulnerability - Critical - 2024-12-15.md`
- `Configuration Issue - Medium - 2024-12-10.md`
- `Compliance Gap - High - 2024-12-12.md`

Content of `Security Vulnerability - Critical - 2024-12-15.md`:
```markdown
---
finding_type: Security Vulnerability
severity: Critical
source: External Audit
issue_date: 2024-12-15
description: SQL Injection risk
---
```

**Duplicate Handling:**
If you have multiple findings with the same type, severity, and date, files will be automatically numbered:
- `Security Vulnerability - Critical - 2024-12-15.md`
- `Security Vulnerability - Critical - 2024-12-15 - 2.md`
- `Security Vulnerability - Critical - 2024-12-15 - 3.md`

## Project Structure

```
csv-to-md/
├── core/                    # Business logic
│   ├── csv_parser.py       # CSV loading and validation
│   ├── cli_ui.py           # Interactive CLI interface
│   └── markdown_generator.py # MD file generation
├── utils/                   # Helper modules
│   ├── file_picker.py      # Windows file dialogs
│   └── filename_generator.py # Filename pattern generation
├── tests/                   # Unit tests
│   ├── test_csv_parser.py
│   ├── test_cli_ui_ordered.py
│   ├── test_filename_generator.py
│   ├── test_markdown_generator.py
│   └── test_markdown_generator_integration.py
├── main.py                  # Application entry point
└── README.md
```

## Running Tests

Execute the test suite:

```powershell
uv run pytest
```

Run with coverage:

```powershell
uv run pytest --cov=core --cov=utils
```

## Technical Notes

- **Windows Only**: Uses `pywin32` for native file dialogs
- **Modular Design**: Separate concerns for parsing, UI, and generation
- **Error Handling**: Comprehensive validation at every step
- **YAML Compliant**: Proper escaping and formatting via PyYAML
- **Filename Safety**: Sanitizes invalid characters for Windows filesystems
- **Unique Filenames**: Checks both in-memory and on-disk for duplicates
- **Order-Preserving**: Filename components follow exact selection order

## Dependencies

- `pywin32`: Native Windows file dialogs
- `pyyaml`: YAML frontmatter generation
- `pytest`: Testing framework (dev)

## Future Enhancements

Potential features for future versions:
- Support for body content templates
- Tag processing and formatting
- Folder organization based on CSV columns
- Batch processing multiple CSV files

## License

This project is provided as-is for use and modification.
