"""User domain model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """
    Represents a user account.

    Attributes:
        username: Username
        password: Password (should be hashed in production)
    """

    username: str
    password: str  # TODO: Should be hashed in production

    def __post_init__(self) -> None:
        """Validate user data."""
        if not self.username or not self.username.strip():
            raise ValueError("Username cannot be empty")
        if not self.password:
            raise ValueError("Password cannot be empty")

    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {"username": self.username, "password": self.password}

    @classmethod
    def from_dict(cls, data: dict) -> Optional["User"]:
        """
        Create user from dictionary.

        Args:
            data: Dictionary with username and password

        Returns:
            User instance or None if data is empty/invalid
        """
        if not data or not data.get("username"):
            return None
        return cls(username=data["username"], password=data.get("password", ""))

