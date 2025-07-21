from typer.testing import CliRunner
from importless.cli.main import app

runner = CliRunner()

def test_scan_simple_imports(tmp_path):
    file = tmp_path / "file1.py"
    file.write_text("import os\nimport sys")
    result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 0
    assert "os" in result.output
    assert "sys" in result.output

def test_scan_from_import(tmp_path):
    file = tmp_path / "file2.py"
    file.write_text("from collections import defaultdict")
    result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 0
    assert "collections" in result.output
    assert "defaultdict" in result.output

def test_scan_import_with_alias(tmp_path):
    file = tmp_path / "file3.py"
    file.write_text("import numpy as np")
    result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 0
    assert "numpy" in result.output
    assert "np" in result.output

def test_scan_no_imports(tmp_path):
    file = tmp_path / "file4.py"
    file.write_text("print('hello')")
    result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 0
    assert "No import statements found." in result.output

def test_scan_multiple_files(tmp_path):
    (tmp_path / "a.py").write_text("import os")
    (tmp_path / "b.py").write_text("from math import sqrt")
    result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 0
    assert "os" in result.output
    assert "math" in result.output
    assert "sqrt" in result.output

def test_scan_file_with_no_imports(tmp_path):
    file = tmp_path / "no_imports.py"
    file.write_text("print('Hello World')\ndef greet(): return 'Hi'")
    result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 0
    assert "No import statements found." in result.output

def test_scan_with_delay(tmp_path):
    file = tmp_path / "file_delay.py"
    file.write_text("import os")
    result = runner.invoke(app, ["scan", str(tmp_path), "--delay", "0.01"])
    assert result.exit_code == 0
    assert "os" in result.output

def test_scan_empty_directory(tmp_path):
    result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 0
    assert "No import statements found." in result.output

def test_scan_with_nested_import(tmp_path):
    file = tmp_path / "nested.py"
    file.write_text("from package.module import ClassName")
    result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 0
    assert "package.module" in result.output
    assert "ClassName" in result.output

def test_scan_import_star(tmp_path):
    file = tmp_path / "star.py"
    file.write_text("from math import *")
    result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 0
    assert "math" in result.output
    assert "*" in result.output