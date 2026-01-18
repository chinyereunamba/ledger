"""Repository for user data access."""

from typing import Optional

from ..config import get_settings
from ..domain.user import User
from .file_manager import FileManager


class UserRepository:
    """Repository for user CRUD operations."""

    def __init__(self, file_manager: Optional[FileManager] = None):
        """
        Initialize user repository.

        Args:
            file_manager: FileManager instance. Creates new one if None.
        """
        self.settings = get_settings()
        self.file_manager = file_manager or FileManager(self.settings)

    def load(self) -> Optional[User]:
        """
        Load user data from file.

        Returns:
            User instance or None if no user exists
        """
        data = self.file_manager.load_json(self.settings.user_file, default={})
        return User.from_dict(data)

    def save(self, user: User) -> None:
        """
        Save user data to file.

        Args:
            user: User instance to save
        """
        self.file_manager.save_json(self.settings.user_file, user.to_dict())

    def delete(self) -> None:
        """Delete user data."""
        self.file_manager.save_json(self.settings.user_file, {})

    def exists(self) -> bool:
        """Check if user exists."""
        user = self.load()
        return user is not None

