from typer.testing import CliRunner
from importless.cli.main import app

runner = CliRunner()

def test_scan_command(tmp_path):
    file = tmp_path / "sample.py"
    file.write_text("import os\nimport sys")
    result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 0
    assert "os" in result.output
    assert "sys" in result.output

def test_scan_command_no_imports(tmp_path):
    file = tmp_path / "sample.py"
    file.write_text("print('Hello world')")
    result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 0
    assert "No import statements found" in result.output

def test_clean_command_dry_run(tmp_path):
    file = tmp_path / "sample.py"
    file.write_text("import os\nimport sys\nprint(os.name)")
    result = runner.invoke(app, ["clean", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0
    assert "sys" in result.output 
    assert "Cleaned" not in result.output

def test_clean_command_actual(tmp_path):
    file = tmp_path / "sample.py"
    file.write_text("import os\nimport sys\nprint(os.name)")
    result = runner.invoke(app, ["clean", str(tmp_path)])
    assert result.exit_code == 0
    cleaned_content = file.read_text()
    assert "import sys" not in cleaned_content
    assert "import os" in cleaned_content

def test_clean_command_backup(tmp_path):
    file = tmp_path / "sample.py"
    file.write_text("import os\nimport sys\nprint(os.name)")
    result = runner.invoke(app, ["clean", str(tmp_path), "--backup"])
    backup_file = tmp_path / "sample.py.bak"
    assert result.exit_code == 0
    assert backup_file.exists()
    assert "import sys" in backup_file.read_text()

def test_clean_command_include_init(tmp_path):
    init_file = tmp_path / "__init__.py"
    init_file.write_text("import os\nprint(os.name)")
    result = runner.invoke(app, ["clean", str(tmp_path), "--include-init"])
    assert result.exit_code == 0
    cleaned_content = init_file.read_text()
    assert "import os" in cleaned_content  

def test_clean_command_skip_init(tmp_path):
    init_file = tmp_path / "__init__.py"
    init_file.write_text("import os\nimport sys\nprint(os.name)")
    result = runner.invoke(app, ["clean", str(tmp_path)])
    assert result.exit_code == 0
    cleaned_content = init_file.read_text()
    assert "import sys" in cleaned_content

def test_clean_command_delay(tmp_path):
    file = tmp_path / "sample.py"
    file.write_text("import os\nimport sys\nprint(os.name)")
    import time
    start = time.time()
    result = runner.invoke(app, ["clean", str(tmp_path), "--delay", "0.1"])
    duration = time.time() - start
    assert result.exit_code == 0
    assert duration >= 0.1 

def test_scan_command_with_alias_import(tmp_path):
    file = tmp_path / "sample.py"
    file.write_text("import numpy as np")
    result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 0
    assert "numpy" in result.output
    assert "np" in result.output

def test_clean_command_removes_unused_alias_import(tmp_path):
    file = tmp_path / "sample.py"
    file.write_text("import numpy as np\nprint('hello')")
    result = runner.invoke(app, ["clean", str(tmp_path)])
    assert result.exit_code == 0
    cleaned_content = file.read_text()
    assert "import numpy" not in cleaned_content
