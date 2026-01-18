"""Application settings and configuration."""

from pathlib import Path
from typing import Optional
import os
from .paths import Paths, get_paths


class Settings:
    """Application-wide settings."""

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize settings.

        Args:
            base_dir: Base directory for ledger files. Defaults to ~/.ledger
        """
        self.paths = get_paths(base_dir)
        self.max_backups = int(os.getenv("LEDGER_MAX_BACKUPS", "10"))
        self.auto_backup = os.getenv("LEDGER_AUTO_BACKUP", "true").lower() == "true"

    @property
    def ledger_file(self) -> Path:
        """Path to ledger file."""
        return self.paths.ledger_file

    @property
    def categories_file(self) -> Path:
        """Path to categories file."""
        return self.paths.categories_file

    @property
    def budget_file(self) -> Path:
        """Path to budget file."""
        return self.paths.budget_file

    @property
    def user_file(self) -> Path:
        """Path to user file."""
        return self.paths.user_file

    @property
    def backup_dir(self) -> Path:
        """Path to backup directory."""
        return self.paths.backup_dir


# Global settings instance
_settings_instance: Optional[Settings] = None


def get_settings(base_dir: Optional[Path] = None) -> Settings:
    """
    Get or create the global settings instance.

    Args:
        base_dir: Optional base directory. Only used on first call.

    Returns:
        Settings instance
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings(base_dir)
    return _settings_instance


def reset_settings(base_dir: Optional[Path] = None) -> None:
    """
    Reset the global settings instance (useful for testing).

    Args:
        base_dir: Optional base directory for new instance.
    """
    global _settings_instance
    _settings_instance = None
    if base_dir is not None:
        get_settings(base_dir)

