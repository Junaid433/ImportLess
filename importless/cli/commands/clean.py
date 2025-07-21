import re
import ast
import typer
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from importless.utils.filewalker import find_python_files

app = typer.Typer()
console = Console()

class ImportUsageVisitor(ast.NodeVisitor):
    def __init__(self):
        self.used_names = set()

    def visit_Name(self, node: ast.Name):
        self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        current = node
        while isinstance(current, ast.Attribute):
            current = current.value
        if isinstance(current, ast.Name):
            self.used_names.add(current.id)
        self.generic_visit(node)

def find_unused_imports(source: str):
    tree = ast.parse(source)
    import_nodes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            import_nodes.append(node)

    usage_visitor = ImportUsageVisitor()
    usage_visitor.visit(tree)
    used_names = usage_visitor.used_names

    unused_imports = []
    for node in import_nodes:
        if isinstance(node, ast.Import):
            for alias in node.names:
                asname = alias.asname or alias.name
                if asname not in used_names:
                    unused_imports.append((node.lineno, 'import', alias.name, alias.asname))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                asname = alias.asname or alias.name
                if asname not in used_names:
                    unused_imports.append((node.lineno, 'from', node.module, alias.name, alias.asname))
    return unused_imports

def remove_unused_imports_from_source(source: str, unused_imports):
    lines = source.splitlines()
    unused_by_line = {}
    for imp in unused_imports:
        lineno = imp[0] - 1
        unused_by_line.setdefault(lineno, []).append(imp)

    new_lines = []

    for idx, line in enumerate(lines):
        if idx not in unused_by_line:
            new_lines.append(line)
            continue

        unused_imps = unused_by_line[idx]

        if line.strip().startswith("from "):
            parts = line.split("import", 1)
            if len(parts) < 2:
                new_lines.append(line)
                continue

            before_import = parts[0] + "import"
            imports_part = parts[1]

            imported_names = [i.strip() for i in imports_part.split(",")]

            unused_names = set()
            for imp in unused_imps:
                if imp[1] == "from":
                    unused_names.add(imp[4] or imp[3])

            filtered_imports = []
            for imp_str in imported_names:
                m = re.match(r"(\w+)(\s+as\s+(\w+))?", imp_str)
                if m:
                    name = m.group(3) or m.group(1)
                    if name in unused_names:
                        continue
                filtered_imports.append(imp_str)

            if filtered_imports:
                new_line = before_import + " " + ", ".join(filtered_imports)
                new_lines.append(new_line)
            else:
                pass
        else:
            skip_line = False
            for imp in unused_imps:
                if imp[1] == "import":
                    name_to_check = imp[3] or imp[2]
                    if name_to_check and name_to_check in line:
                        skip_line = True
                        break
            if not skip_line:
                new_lines.append(line)

    return "\n".join(new_lines)

@app.command()
def clean(
    path: str = typer.Argument(".", help="Path to the Python project directory"),
    include_init: bool = typer.Option(False, "--include-init", help="Include __init__.py files in cleaning"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show changes without modifying files"),
    backup: bool = typer.Option(False, "--backup", help="Create .bak backups before modifying files"),
    delay: float = typer.Option(0.05, help="Delay between outputs to simulate real-time scanning (0 to disable)"),
):
    console.print(Panel.fit(f"[bold green]🧹 Starting Import Cleanup in [italic cyan]{path}[/]", title="ImportLess Clean"))
    python_files = find_python_files(path)
    total_removed = 0
    cleaned_count = 0

    for filepath in track(python_files, description="🔍 Scanning files...", console=console):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()

            if not include_init and filepath.endswith("__init__.py"):
                console.log(f"⏭️  Skipping [italic]{filepath}[/] (init file)")
                continue

            unused_imports = find_unused_imports(source)

            if unused_imports:
                new_source = remove_unused_imports_from_source(source, unused_imports)
                total_removed += len(unused_imports)

                table = Table(title=f"[bold green]{filepath}", show_header=True, header_style="bold blue")
                table.add_column("Line", justify="right")
                table.add_column("Type")
                table.add_column("Module")
                table.add_column("Alias", justify="center")

                for imp in unused_imports:
                    if imp[1] == "import":
                        table.add_row(str(imp[0]), "import", imp[2], imp[3] or "-")
                    else:
                        table.add_row(str(imp[0]), "from", f"{imp[2]}.{imp[3]}", imp[4] or "-")

                console.print(table)

                if dry_run:
                    console.log(f"[yellow]⚠️ Dry run: No changes written to [italic]{filepath}[/]")
                else:
                    if backup:
                        with open(filepath + ".bak", "w", encoding="utf-8") as f:
                            f.write(source)
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_source)
                    console.log(f"[green]✅ Cleaned {len(unused_imports)} unused import(s) in {filepath}[/]")
                    cleaned_count += 1
            else:
                console.log(f"✔ No unused imports in {filepath}")
            if delay > 0:
                time.sleep(delay)
        except Exception as e:
            console.log(f"[red]❌ Failed to process {filepath}: {e}[/]")

    console.print(Panel.fit(
        f"[bold green]🎉 Finished cleaning.\n[cyan]Files cleaned:[/] {cleaned_count}  |  [cyan]Total removed imports:[/] {total_removed}",
        title="✅ Summary",
        border_style="bright_green"
    ))
