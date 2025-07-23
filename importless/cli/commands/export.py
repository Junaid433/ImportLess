import typer
import time
import subprocess
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from pathlib import Path
from importlib.metadata import version as get_version, PackageNotFoundError
from importless.models.STDLIB import stdlib_modules
from importless.utils.filewalker import find_python_files
from importless.core.analyzer import analyze_source
from importless.utils.formatter import print_message

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

def run_pip_freeze() -> dict[str, str]:
    try:
        output = subprocess.check_output(["pip", "freeze"], text=True)
    except Exception as e:
        console.log(f"[red]❌ Failed to run pip freeze: {e}[/]")
        return {}
    frozen = {}
    for line in output.splitlines():
        if "==" in line:
            pkg, ver = line.split("==", 1)
            frozen[pkg.lower()] = line
    return frozen

def get_transitive_dependencies(packages: set[str]) -> set[str]:
    try:
        result = subprocess.run(
            ["pipdeptree", "--json-tree"],
            capture_output=True,
            text=True,
            check=True,
        )
        tree = json.loads(result.stdout)
    except Exception as e:
        console.log(f"[red]❌ Failed to run pipdeptree: {e}[/]")
        return packages

    visited = set()

    def collect_deps(pkg_name):
        if pkg_name in visited:
            return
        visited.add(pkg_name)
        for node in tree:
            package_info = node.get("package")
            if not package_info:
                continue
            if package_info.get("key") == pkg_name:
                for dep in node.get("dependencies", []):
                    dep_package = dep.get("package")
                    if not dep_package:
                        continue
                    dep_key = dep_package.get("key")
                    if dep_key:
                        collect_deps(dep_key)

    for pkg in packages:
        collect_deps(pkg.lower())

    visited.update(pkg.lower() for pkg in packages)
    return visited

@app.command()
def export(
    path: str = typer.Argument(".", help="Path to the Python project directory"),
    output: str = typer.Option("requirements.txt", help="Output requirements file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print detected packages without writing to file"),
    show_table: bool = typer.Option(False, "--show-table", help="Show a table of file → packages"),
    delay: float = typer.Option(0.05, help="Delay between outputs to simulate real-time scanning (0 to disable)"),
):
    console.print(Panel.fit(f"📦 Starting Export of Requirements from [italic cyan]{path}[/]", title="ImportLess Export"))
    path_obj = Path(path).resolve()
    python_files = find_python_files(str(path_obj))
    local_modules = get_local_modules(path_obj)
    detected_packages = set()
    file_package_map = {}

    for filepath in track(python_files, description="🔍 Scanning files...", console=console):
        try:
            if filepath.endswith("__init__.py"):
                console.log(f"⏭️  Skipping [italic]{filepath}[/] (init file)")
                continue
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            imports = analyze_source(source)
            file_packages = set()
            for imp in imports:
                if imp.module:
                    top_module = imp.module.split('.')[0]
                    if top_module not in local_modules and top_module not in stdlib_modules:
                        detected_packages.add(top_module)
                        file_packages.add(top_module)
            if file_packages:
                file_package_map[filepath] = sorted(file_packages)
                console.log(f"[bold green]✓[/] [white]{filepath}[/] → [cyan]{', '.join(file_packages)}[/]")
            else:
                console.log(f"[dim]-[/] [white]{filepath}[/] → [yellow]No external packages detected[/]")
        except Exception as e:
            console.log(f"[red]❌ Failed to analyze {filepath}: {e}[/]")
        if delay > 0:
            time.sleep(delay)

    if not detected_packages:
        print_message("\nNo external imports found.", style="yellow")
        return

    print_message(f"\nDetected [bold]{len(detected_packages)}[/] unique top-level packages.")
    frozen_packages = run_pip_freeze()
    all_packages = get_transitive_dependencies(detected_packages)

    final_packages = set()
    for pkg in all_packages:
        if pkg in frozen_packages:
            final_packages.add(frozen_packages[pkg])
        else:
            final_packages.add(get_version_pinned(pkg))

    if show_table:
        table = Table(title="Detected Packages by File", show_header=True, header_style="bold magenta")
        table.add_column("File")
        table.add_column("Packages")
        for file, pkgs in file_package_map.items():
            table.add_row(file, ", ".join(pkgs))
        console.print()
        console.print(table)

    if dry_run:
        print_message("\nDry Run: Final list of required packages:")
        for pkg in sorted(final_packages, key=str.lower):
            console.print(f"[white]- {pkg}[/]")
    else:
        try:
            with open(output, "w", encoding="utf-8") as f:
                for pkg in sorted(final_packages, key=str.lower):
                    f.write(pkg + "\n")
            console.print(Panel.fit(
                f"✅ Exported full pinned requirements to [bold green]{output}[/]",
                border_style="bright_green"
            ))
        except Exception as e:
            console.print(f"[red]❌ Failed to write requirements file: {e}[/]")
