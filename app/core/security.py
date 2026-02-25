from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM

def _normalize_bcrypt_secret(password: str) -> str:
    """Ensure password is no more than 72 bcrypt bytes."""
    password_bytes = password.encode("utf-8")[:72]
    return password_bytes.decode("utf-8", errors="ignore")

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_normalize_bcrypt_secret(plain_password), hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(_normalize_bcrypt_secret(password))
