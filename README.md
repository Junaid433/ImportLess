# ImportLess

ImportLess is a command-line tool designed to help Python developers generate minimal dependency lists by analyzing the actual imports used in their source code. This makes your `requirements.txt` lean, accurate, and free from unused or redundant packages.

---

## Table of Contents

1. [Why ImportLess?](#why-importless)
2. [Features](#features)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Command Reference](#command-reference)
6. [How It Works](#how-it-works)
7. [Project Structure](#project-structure)
8. [Contributing](#contributing)
9. [License](#license)
10. [Support](#support)

---

## Why ImportLess?

Managing dependencies in Python projects can be tricky:

- `requirements.txt` files often include packages no longer used.
- Manual dependency tracking is error-prone and time-consuming.
- Over-installed dependencies increase project size and complexity.

ImportLess automates this process by:

- Scanning your Python files for actual import statements.
- Filtering and identifying the exact packages your project depends on.
- Helping you keep your dependency list minimal and up to date.

---

## Features

- **Comprehensive scanning** of Python source files in any directory.
- **Supports both top-level and detailed import listings.**
- **CLI progress display** with rich formatting using the `rich` library.
- **Configurable scanning delay** to simulate progress or manage performance.
- **Clear, formatted output tables** of detected imports.
- Designed to be **extensible and modular**.

---

## Installation

### Prerequisites

- Python 3.8 or higher
- `pip` package manager

### Install from PyPI

Simply run:

```bash
pip install importless
````

### Install from Source

If you prefer the bleeding edge or want to contribute:

```bash
git clone https://github.com/yourusername/importless.git
cd importless
pip install -e .
```

This will install the package in editable mode so you can modify and test easily.

---

## Quick Start

Navigate to your Python project directory, then run:

```bash
importless scan
```

This will scan the current directory and show the top-level imports detected.

To see **all imports** (including from `from module import name` style), use:

```bash
importless scan --all
```

If you want to slow down scanning to watch the progress bar more clearly (default delay is 0.05 seconds), specify the delay:

```bash
importless scan --delay 0.1
```

---

## Command Reference

### `scan`

Scans the specified directory for Python files and extracts import statements.

#### Arguments

- `path` *(optional)*: Path to the directory you want to scan. Defaults to the current working directory (`.`).

#### Options

- `--all`: Show **all** imports, including nested/local imports. By default, only top-level imports are shown.
- `--delay <FLOAT>`: Delay (in seconds) between processing each file. Default is `0.05`. Use `--delay 0` for faster execution.

#### Examples

```bash
# Scan current directory, show top-level imports only
importless scan

# Scan a specific directory and show all imports
importless scan --all ./myproject

# Scan with no delay for faster scanning
importless scan --delay 0
```

---

### `export`

Exports the scanned imports as a minimal `requirements.txt` file.

#### Options

- `-o, --output <FILE>`: Specify the output file path. Defaults to `requirements.trimmed.txt`.
- `--freeze`: Match versions using `pip freeze` for already-installed packages.
- `--no-comments`: Omit inline comments showing where imports were found.

#### Examples

```bash
# Export requirements to the default file
importless export
```

---

### `clean`

Removes unused or redundant packages from your environment or requirements file.

#### Options

- `-f, --file <FILE>`: Path to the original `requirements.txt` file. Defaults to `requirements.txt`.
- `--dry-run`: Preview the changes without making modifications.

#### Examples

```bash
# Clean default requirements file
importless clean

# Preview what would be removed
importless clean --dry-run
```

---

## How It Works

1. **File Discovery:** Uses `filewalker` utility to recursively find all `.py` files in the target directory.
2. **Source Parsing:** Reads each Python file and analyzes it for import statements using the `analyze_source` core function.
3. **Import Extraction:** Collects import details such as the module name, imported names, and aliases.
4. **Filtering:** By default, only top-level imports (e.g., `import module`) are shown unless `--all` is specified.
5. **Presentation:** Shows a nicely formatted table of imports using the `rich` library and prints summary messages.

---

## Project Structure

```
importless/
├── cli/               # CLI commands implemented with Typer
├── core/              # Core logic for analyzing source and imports
├── models/            # Data models representing import nodes
├── utils/             # Utility functions (filewalker, formatting, etc.)
├── config.py          # Configuration handling
tests/                  # Unit and integration tests
examples/               # Sample projects to try ImportLess
scripts/                # Helper scripts for development
docs/                   # Documentation files
```

---

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository** on GitHub and clone it locally.

2. **Set up your environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Make your changes.**

4. **Write tests** for new features or bug fixes.

5. **Run tests** with `pytest` to ensure nothing is broken:

   ```bash
   pytest
   ```

6. **Format your code** using `black`:

   ```bash
   black .
   ```

7. **Commit your changes** with clear messages.

8. **Submit a pull request** describing your improvements.

---

## License

ImportLess is licensed under the [MIT License](LICENSE).

---

## Support

If you encounter any issues or have questions, please:

* Open an issue on the [GitHub repository](https://github.com/yourusername/importless/issues).
* Or reach out to the maintainers via email.

---

Thank you for using ImportLess! Keep your Python projects clean and dependency-minimal.
