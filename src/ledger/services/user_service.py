"""Service for user business logic."""

from typing import Optional

from ..domain.user import User
from ..repositories import UserRepository


class UserService:
    """Service for user operations."""

    def __init__(self, repository: Optional[UserRepository] = None):
        """
        Initialize user service.

        Args:
            repository: UserRepository instance. Creates new one if None.
        """
        self.repository = repository or UserRepository()

    def create_user(self, username: str, password: str) -> User:
        """
        Create a new user.

        Args:
            username: Username
            password: Password

        Returns:
            Created User instance
        """
        if self.repository.exists():
            raise ValueError("User already exists")

        user = User(username=username, password=password)
        self.repository.save(user)
        return user

    def get_user(self) -> Optional[User]:
        """
        Get current user.

        Returns:
            User instance or None if no user exists
        """
        return self.repository.load()

    def delete_user(self) -> None:
        """Delete current user."""
        self.repository.delete()

    def user_exists(self) -> bool:
        """Check if user exists."""
        return self.repository.exists()

