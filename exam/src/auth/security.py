from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Dict, Optional

from passlib.context import CryptContext

from .jwt_handler import jwt_handler


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, password: str) -> str:
        ...

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        ...


class BcryptPasswordHasher(PasswordHasher):
    def __init__(self, context: CryptContext) -> None:
        self._ctx = context

    def hash(self, password: str) -> str:
        return self._ctx.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return self._ctx.verify(plain_password, hashed_password)


_password_hasher: PasswordHasher = BcryptPasswordHasher(pwd_context)


def get_password_hasher() -> PasswordHasher:
    """
    Dependency factory for password hasher.
    Can be overridden in tests or other environments.
    """

    return _password_hasher


def get_password_hash(password: str) -> str:
    """
    Hash a password using the configured hasher.
    """

    return get_password_hasher().hash(password)


def hash_password(password: str) -> str:
    """
    Backwards-compatible alias for get_password_hash.
    """

    return get_password_hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    """

    return get_password_hasher().verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, str],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create an access token from payload data.
    Uses JWTHandler under the hood.
    """

    user_id = data.get("sub")
    additional_claims = {k: v for k, v in data.items() if k != "sub"}

    # JWTHandler currently uses its internal expiry configuration.
    # expires_delta is accepted here for future flexibility.
    return jwt_handler.create_access_token(
        user_id=str(user_id),
        additional_claims=additional_claims or None,
    )


