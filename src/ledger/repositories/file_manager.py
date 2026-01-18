"""File management and backup utilities."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from ..config import get_settings


class FileManager:
    """Manages file operations with automatic backup support."""

    def __init__(self, settings=None):
        """
        Initialize file manager.

        Args:
            settings: Settings instance. If None, uses global settings.
        """
        if settings is None:
            from ..config import get_settings

            settings = get_settings()
        self.settings = settings

    def create_backup(self, file_path: Path) -> Optional[Path]:
        """
        Create a backup of a file.

        Args:
            file_path: Path to file to backup

        Returns:
            Path to backup file, or None if file doesn't exist
        """
        if not file_path.exists():
            return None

        self.settings.paths.ensure_directories()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.settings.backup_dir / f"{file_path.stem}_backup_{timestamp}.json"
        shutil.copy2(file_path, backup_file)

        # Keep only the last N backups
        self._cleanup_old_backups(file_path.stem)

        return backup_file

    def _cleanup_old_backups(self, file_stem: str) -> None:
        """
        Remove old backups, keeping only the most recent N.

        Args:
            file_stem: Stem of the file (e.g., "ledger", "categories")
        """
        backups = sorted(
            self.settings.backup_dir.glob(f"{file_stem}_backup_*.json"),
            reverse=True,
        )
        if len(backups) > self.settings.max_backups:
            for old_backup in backups[self.settings.max_backups :]:
                old_backup.unlink()

    def load_json(self, file_path: Path, default: Optional[Dict] = None) -> Dict:
        """
        Load JSON data from file.

        Args:
            file_path: Path to JSON file
            default: Default value if file doesn't exist

        Returns:
            Dictionary with loaded data
        """
        if default is None:
            default = {}

        try:
            if not file_path.exists():
                return default

            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise IOError(f"Error loading {file_path}: {e}") from e

    def save_json(
        self, file_path: Path, data: Dict, create_backup: Optional[bool] = None
    ) -> None:
        """
        Save JSON data to file with optional backup.

        Args:
            file_path: Path to JSON file
            data: Data to save
            create_backup: Whether to create backup. Uses settings default if None.
        """
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create backup if enabled
        if create_backup is None:
            create_backup = self.settings.auto_backup

        if create_backup and file_path.exists():
            self.create_backup(file_path)

        # Save file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"Error saving {file_path}: {e}") from e

    def file_exists(self, file_path: Path) -> bool:
        """Check if file exists."""
        return file_path.exists()

    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes."""
        if not file_path.exists():
            return 0
        return file_path.stat().st_size

    def list_backups(self, file_stem: str) -> list[Path]:
        """
        List backup files for a given file stem.

        Args:
            file_stem: Stem of the file (e.g., "ledger", "categories")

        Returns:
            List of backup file paths, sorted by modification time (newest first)
        """
        backups = sorted(
            self.settings.backup_dir.glob(f"{file_stem}_backup_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return backups

