"""CLI commands for utility functions."""

import typer
from rich import print as rprint
from datetime import datetime

from ...ledger.config import get_settings
from ...ledger.repositories import FileManager
from ..presenters import TableFormatter


def register_utility_commands(app: typer.Typer):
    """Register utility CLI commands."""

    formatter = TableFormatter()
    settings = get_settings()
    file_manager = FileManager(settings)

    @app.command()
    def backups():
        """Show available backup files."""
        try:
            ledger_backups = file_manager.list_backups("ledger")
            category_backups = file_manager.list_backups("categories")

            if not ledger_backups and not category_backups:
                rprint("[yellow]No backup files found.[/yellow]")
                return

            rprint("\n[bold blue]📁 Available Backups[/bold blue]")

            if ledger_backups:
                rprint("\n[bold green]Ledger Backups:[/bold green]")
                backup_dicts = []
                for backup in ledger_backups[:10]:
                    stat = backup.stat()
                    created = datetime.fromtimestamp(stat.st_mtime)
                    backup_dicts.append({
                        "name": backup.name,
                        "created": created.strftime("%Y-%m-%d %H:%M:%S"),
                        "size": f"{stat.st_size} bytes",
                    })
                table = formatter.format_backups_table(backup_dicts)
                formatter.print_table(table)

            if category_backups:
                rprint("\n[bold yellow]Category Backups:[/bold yellow]")
                backup_dicts = []
                for backup in category_backups[:5]:
                    stat = backup.stat()
                    created = datetime.fromtimestamp(stat.st_mtime)
                    backup_dicts.append({
                        "name": backup.name,
                        "created": created.strftime("%Y-%m-%d %H:%M:%S"),
                        "size": f"{stat.st_size} bytes",
                    })
                table = formatter.format_backups_table(backup_dicts)
                formatter.print_table(table)

            rprint(f"\n[dim]Backup location: {settings.backup_dir}[/dim]")

        except Exception as e:
            rprint(f"[red]Error listing backups: {e}[/red]")

    @app.command()
    def info():
        """Show ledger configuration and file information."""
        try:
            from rich.table import Table
            from rich.console import Console

            console = Console()

            rprint("\n[bold blue]📋 Ledger Information[/bold blue]")

            info_table = Table("Setting", "Value")
            info_table.add_row("Ledger Directory", str(settings.paths.base_dir))
            info_table.add_row("Ledger File", str(settings.ledger_file))
            info_table.add_row("Categories File", str(settings.categories_file))
            info_table.add_row("Budget File", str(settings.budget_file))
            info_table.add_row("Backup Directory", str(settings.backup_dir))

            # File existence and sizes
            if file_manager.file_exists(settings.ledger_file):
                size = file_manager.get_file_size(settings.ledger_file)
                info_table.add_row("Ledger Size", f"{size} bytes")
            else:
                info_table.add_row("Ledger Status", "[red]Not created yet[/red]")

            if file_manager.file_exists(settings.categories_file):
                size = file_manager.get_file_size(settings.categories_file)
                info_table.add_row("Categories Size", f"{size} bytes")
            else:
                info_table.add_row("Categories Status", "[red]Not created yet[/red]")

            # Count backups
            backup_count = len(file_manager.list_backups("ledger")) + len(file_manager.list_backups("categories"))
            info_table.add_row("Backup Files", str(backup_count))

            console.print(info_table)

        except Exception as e:
            rprint(f"[red]Error getting ledger info: {e}[/red]")

