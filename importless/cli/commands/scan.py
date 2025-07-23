import typer
import time
from rich.console import Console
from rich.progress import track
from rich.table import Table
from importless.utils.filewalker import find_python_files
from importless.core.analyzer import analyze_source
from importless.cli.commands.clean import find_unused_imports
from importless.core.exceptions import FileParseError
from importless.utils.formatter import print_imports_table, print_message

app = typer.Typer()
console = Console()

@app.command()
def scan(
    path: str = typer.Argument(".", help="Path to the Python project directory"),
    delay: float = typer.Option(0.05, help="Delay between processing files to simulate scanning (seconds)"),
    all: bool = typer.Option(False, "--all", help="Show all imports instead of only top-level"),
):
    python_files = find_python_files(path)

    summary = []
    all_imports = []

    for filepath in track(python_files, description="🔍 Scanning Python files...", console=console):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()

            imports = analyze_source(source)
            unused = find_unused_imports(source)
            total_imports = len(imports)
            unused_count = len(unused)

            summary.append({
                "file": filepath,
                "total_imports": total_imports,
                "unused_imports": unused_count,
                "removable_lines": unused_count 
            })

            for imp in imports:
                all_imports.append({
                    "module": imp.module or "",
                    "name": imp.name or "",
                    "alias": imp.alias or "",
                    "file": filepath
                })

        except Exception as e:
            raise FileParseError(filepath, str(e))

        if delay > 0:
            time.sleep(delay)

    if all_imports:
        if not all:
            top_level_imports = [
                imp for imp in all_imports if imp["name"] == "" and imp["alias"] == ""
            ]
            print_imports_table(top_level_imports)
            print_message(f"Found [bold]{len(top_level_imports)}[/] top-level import statements across [bold]{len(python_files)}[/] files.")
        else:
            print_imports_table(all_imports)
            print_message(f"Found [bold]{len(all_imports)}[/] import statements across [bold]{len(python_files)}[/] files.")
    else:
        print_message("No import statements found.", style="yellow")

    if summary:
        table = Table(title="Unused Imports Summary", show_header=True, header_style="bold magenta")
        table.add_column("File", style="dim")
        table.add_column("Total Imports", justify="right")
        table.add_column("Unused Imports", justify="right")
        table.add_column("Removable Lines", justify="right")

        for entry in summary:
            table.add_row(
                entry["file"],
                str(entry["total_imports"]),
                str(entry["unused_imports"]),
                str(entry["removable_lines"]),
            )

        console.print(table)
