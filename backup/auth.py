from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.core.config import settings

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configure OAuth2 for token retrieval (maps to the login endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


def _normalize_bcrypt_secret(password: str) -> str:
    """Ensure password is no more than 72 bcrypt bytes."""
    password_bytes = password.encode("utf-8")[:72]
    return password_bytes.decode("utf-8", errors="ignore")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the hashed version."""
    return pwd_context.verify(_normalize_bcrypt_secret(plain_password), hashed_password)


def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(_normalize_bcrypt_secret(password))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a JWT Access Token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Validates the token and retrieves the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
        
    return user
