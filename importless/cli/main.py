import typer
from importless.cli.commands import scan, clean, export, update_pyproject

app = typer.Typer()

app.command(name="scan", help="Scan project for imports and dependencies")(scan)
app.command(name="clean", help="Clean unused imports from project files")(clean)
app.command(name="export", help="Export minimal requirements.txt")(export)
app.command(name="update-pyproject", help="Update pyproject.toml")(update_pyproject)

def main():
    app()

if __name__ == "__main__":
    main()