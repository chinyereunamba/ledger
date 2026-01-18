"""CLI commands for user management."""

import typer
from rich import print as rprint

from ...ledger.services.user_service import UserService


def register_user_commands(app: typer.Typer, user_service: UserService):
    """Register user-related CLI commands."""

    user = typer.Typer()
    app.add_typer(user, name="user")

    @user.command("delete")
    def delete():
        """Delete user account"""
        sure = typer.confirm("Are you sure you want to delete user?")
        if sure:
            try:
                user_service.delete_user()
                rprint("[green]User deleted successfully[/green]")
            except Exception as e:
                rprint(f"[red]Error deleting user: {e}[/red]")
        else:
            typer.Exit()

