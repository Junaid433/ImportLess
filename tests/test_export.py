from typer.testing import CliRunner
from importless.cli.main import app

runner = CliRunner()

def test_export_multiple_files(tmp_path):
    (tmp_path / "a.py").write_text("import flask")
    (tmp_path / "b.py").write_text("import click")
    result = runner.invoke(app, ["export", str(tmp_path)])
    assert result.exit_code == 0
    assert "flask" in result.output
    assert "click" in result.output

def test_export_mixed_valid_and_invalid_files(tmp_path):
    (tmp_path / "valid.py").write_text("import requests\nprint('ok')")
    (tmp_path / "bad.py").write_text("def broken(:")
    result = runner.invoke(app, ["export", str(tmp_path)])
    assert "requests" in result.output

def test_export_nested_directory(tmp_path):
    nested = tmp_path / "src"
    nested.mkdir()
    (nested / "main.py").write_text("import numpy")
    result = runner.invoke(app, ["export", str(tmp_path)])
    assert "numpy" in result.output

def test_export_non_python_files_ignored(tmp_path):
    (tmp_path / "script.js").write_text("import lodash")
    (tmp_path / "main.py").write_text("import requests")
    result = runner.invoke(app, ["export", str(tmp_path)])
    assert "requests" in result.output
    assert "lodash" not in result.output

def test_export_help_command():
    result = runner.invoke(app, ["export", "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output or "export" in result.output
