from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt

from .config import settings
from .exceptions import AuthenticationException


class BaseJWTHandler(ABC):
    """Abstract base class for JWT handling."""

    @abstractmethod
    def encode(
        self,
        payload: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Encode payload to JWT token."""

    @abstractmethod
    def decode(self, token: str) -> Dict[str, Any]:
        """Decode JWT token to payload."""

    @abstractmethod
    def create_access_token(
        self,
        user_id: str,
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create access token."""

    @abstractmethod
    def create_refresh_token(
        self,
        user_id: str,
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create refresh token."""


class JWTHandler(BaseJWTHandler):
    """Concrete implementation of JWT handler using PyJWT."""

    def __init__(
        self,
        secret_key: str = settings.SECRET_KEY,
        algorithm: str = settings.ALGORITHM,
        access_token_expire_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days: int = settings.REFRESH_TOKEN_EXPIRE_DAYS,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def encode(
        self,
        payload: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        to_encode = payload.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            return payload
        except jwt.ExpiredSignatureError as exc:
            raise AuthenticationException("Token expired") from exc
        except jwt.InvalidTokenError as exc:
            raise AuthenticationException("Invalid token") from exc

    def create_access_token(
        self,
        user_id: str,
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        payload: Dict[str, Any] = {
            "sub": user_id,
            "type": "access",
            "iat": datetime.utcnow(),
        }

        if additional_claims:
            payload.update(additional_claims)

        expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        return self.encode(payload, expires_delta)

    def create_refresh_token(
        self,
        user_id: str,
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        payload: Dict[str, Any] = {
            "sub": user_id,
            "type": "refresh",
            "iat": datetime.utcnow(),
        }

        if additional_claims:
            payload.update(additional_claims)

        expires_delta = timedelta(days=self.refresh_token_expire_days)
        return self.encode(payload, expires_delta)


jwt_handler = JWTHandler()
