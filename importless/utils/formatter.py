from rich.console import Console
from rich.table import Table
from typing import List, Dict, Optional

console = Console()

def print_imports_table(imports: List[Dict[str, Optional[str]]]) -> None:
    """
    Pretty-print a table of import statements.

    Each dict in imports should have keys: 'module', 'name', 'alias' (optional).
    """
    table = Table(title="Detected Imports")

    table.add_column("Module", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Alias", style="green", no_wrap=True)

    for imp in imports:
        module = imp.get("module") or ""
        name = imp.get("name") or ""
        alias = imp.get("alias") or ""
        table.add_row(module, name, alias)

    console.print(table)


def print_message(message: str, style: str = "bold green") -> None:
    """
    Print a styled message to the console.
    """
    console.print(message, style=style)
