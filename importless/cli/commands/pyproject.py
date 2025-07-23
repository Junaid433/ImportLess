import toml
import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from importless.utils.filewalker import find_python_files
from importless.core.analyzer import analyze_source
from importlib.metadata import version as get_version, PackageNotFoundError
from importless.models.STDLIB import stdlib_modules
import time
import shutil
import subprocess

app = typer.Typer()
console = Console()

def get_local_modules(project_root: Path) -> set[str]:
    py_files = {p.stem for p in project_root.rglob("*.py") if "__pycache__" not in str(p)}
    init_dirs = {p.name for p in project_root.rglob("__init__.py")}
    return py_files.union(init_dirs)

def get_version_pinned(pkg: str) -> str:
    try:
        return f"{pkg}=={get_version(pkg)}"
    except PackageNotFoundError:
        return pkg

@app.command()
def update_pyproject(
    path: str = typer.Argument(".", help="Path to the Python project directory"),
    pyproject_path: str = typer.Option("pyproject.toml", help="Path to pyproject.toml file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show changes without writing"),
    backup: bool = typer.Option(True, "--backup/--no-backup", help="Backup pyproject.toml before changes"),
    delay: float = typer.Option(0.05, help="Delay between processing files"),
):
    console.print(Panel.fit(f"📦 Updating pyproject.toml dependencies from [italic cyan]{path}[/]", title="ImportLess Pyproject Update"))

    project_root = Path(path).resolve()
    pyproject_file = Path(pyproject_path).resolve()
    if not pyproject_file.exists():
        console.print(f"[red]❌ pyproject.toml not found at {pyproject_file}[/]")
        raise typer.Exit(1)

    python_files = find_python_files(str(project_root))
    local_modules = get_local_modules(project_root)
    detected_packages = set()

    for filepath in track(python_files, description="🔍 Scanning files...", console=console):
        try:
            if filepath.endswith("__init__.py"):
                continue
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            imports = analyze_source(source)
            for imp in imports:
                if imp.module:
                    top_module = imp.module.split(".")[0]
                    if top_module not in local_modules and top_module not in stdlib_modules:
                        detected_packages.add(top_module)
        except Exception as e:
            console.log(f"[red]❌ Failed to analyze {filepath}: {e}")
        if delay > 0:
            time.sleep(delay)

    if not detected_packages:
        console.print("[yellow]No external imports found, nothing to update.[/]")
        raise typer.Exit()

    console.print(f"Detected [bold]{len(detected_packages)}[/] unique packages.")

    try:
        pyproject_data = toml.loads(pyproject_file.read_text(encoding="utf-8"))
    except Exception as e:
        console.print(f"[red]❌ Failed to parse pyproject.toml: {e}[/]")
        raise typer.Exit(1)

    deps_section = None
    if "tool" in pyproject_data and "poetry" in pyproject_data["tool"]:
        deps_section = pyproject_data["tool"]["poetry"].get("dependencies", {})
        poetry_style = True
    elif "project" in pyproject_data and "dependencies" in pyproject_data["project"]:
        deps_section = pyproject_data["project"]["dependencies"]
        poetry_style = False
    else:
        console.print("[red]❌ Could not find dependencies section in pyproject.toml[/]")
        raise typer.Exit(1)

    existing_deps = {}
    if poetry_style:
        for pkg, ver in deps_section.items():
            if isinstance(ver, str):
                existing_deps[pkg.lower()] = ver
            elif isinstance(ver, dict) and "version" in ver:
                existing_deps[pkg.lower()] = ver["version"]
    else:
        for entry in deps_section:
            if "==" in entry:
                pkg, ver = entry.split("==", 1)
                existing_deps[pkg.lower()] = f"=={ver}"
            elif " " in entry:
                pkg, ver = entry.split(" ", 1)
                existing_deps[pkg.lower()] = f"=={ver.strip()}"
            else:
                existing_deps[entry.lower()] = "*"

    frozen = {}
    try:
        output = subprocess.check_output(["pip", "freeze"], text=True)
        for line in output.splitlines():
            if "==" in line:
                pkg, ver = line.split("==", 1)
                frozen[pkg.lower()] = f"=={ver}"
    except Exception as e:
        console.log(f"[red]❌ Failed to run pip freeze: {e}[/]")

    new_deps = {}
    for pkg in detected_packages:
        key = pkg.lower()
        if key in frozen:
            new_deps[pkg] = frozen[key]
        else:
            ver = get_version_pinned(pkg)
            if "==" in ver:
                new_deps[pkg] = f"=={ver.split('==')[1]}"
            else:
                new_deps[pkg] = "*"

    for k, v in existing_deps.items():
        if k not in new_deps:
            new_deps[k] = v

    if poetry_style:
        poetry_deps = pyproject_data["tool"]["poetry"]["dependencies"]
        for pkg, ver in new_deps.items():
            poetry_deps[pkg] = ver
    else:
        proj_deps = []
        for pkg, ver in sorted(new_deps.items()):
            if ver in ["*", ""]:
                proj_deps.append(pkg)
            else:
                proj_deps.append(f"{pkg}=={ver.lstrip('=')}")
        pyproject_data["project"]["dependencies"] = proj_deps

    if dry_run:
        console.print(Panel.fit(f"[yellow]Dry run enabled, no file changes made.[/]\nUpdated dependencies:\n{new_deps}", title="Dry Run"))
        return

    if backup:
        backup_file = pyproject_file.with_suffix(pyproject_file.suffix + ".bak")
        shutil.copy(pyproject_file, backup_file)
        console.print(f"Backup created at {backup_file}")

    try:
        pyproject_file.write_text(toml.dumps(pyproject_data), encoding="utf-8")
        console.print(Panel.fit(f"✅ Updated dependencies in [bold green]{pyproject_file}[/]", border_style="bright_green"))
    except Exception as e:
        console.print(f"[red]❌ Failed to write pyproject.toml: {e}[/]")
