"""File path management for ledger application."""

from pathlib import Path
from typing import Optional
import os


class Paths:
    """Centralized file path management for ledger data files."""

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize paths with optional base directory.

        Args:
            base_dir: Base directory for ledger files. Defaults to ~/.ledger
        """
        if base_dir is None:
            base_dir = Path.home() / ".ledger"

        self.base_dir = Path(base_dir)
        self.backup_dir = self.base_dir / "backups"

    @property
    def ledger_file(self) -> Path:
        """Path to the main ledger JSON file."""
        return self.base_dir / "ledger.json"

    @property
    def categories_file(self) -> Path:
        """Path to the categories JSON file."""
        return self.base_dir / "categories.json"

    @property
    def budget_file(self) -> Path:
        """Path to the budget JSON file."""
        return self.base_dir / "budget.json"

    @property
    def user_file(self) -> Path:
        """Path to the user JSON file."""
        return self.base_dir / "user.json"

    def ensure_directories(self) -> None:
        """Create all necessary directories if they don't exist."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)


# Global paths instance
_paths_instance: Optional[Paths] = None


def get_paths(base_dir: Optional[Path] = None) -> Paths:
    """
    Get or create the global paths instance.

    Args:
        base_dir: Optional base directory. Only used on first call.

    Returns:
        Paths instance
    """
    global _paths_instance
    if _paths_instance is None:
        if base_dir is None:
            # Allow override via environment variable
            env_dir = os.getenv("LEDGER_DATA_DIR")
            if env_dir:
                base_dir = Path(env_dir)
        _paths_instance = Paths(base_dir)
        _paths_instance.ensure_directories()
    return _paths_instance


def reset_paths(base_dir: Optional[Path] = None) -> None:
    """
    Reset the global paths instance (useful for testing).

    Args:
        base_dir: Optional base directory for new instance.
    """
    global _paths_instance
    _paths_instance = None
    if base_dir is not None:
        get_paths(base_dir)

