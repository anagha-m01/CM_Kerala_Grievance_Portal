import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db.session import get_db
from app.models.entities import User

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    iterations = 600_000
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
    return f'pbkdf2_sha256${iterations}${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}'


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, count, salt, expected = encoded.split('$')
        if algorithm != 'pbkdf2_sha256':
            return False
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), base64.b64decode(salt), int(count))
        return hmac.compare_digest(actual, base64.b64decode(expected))
    except (ValueError, TypeError):
        return False


def create_token(user: User) -> str:
    settings = get_settings()
    if len(settings.JWT_SECRET.encode('utf-8')) < 32:
        raise HTTPException(status_code=503, detail='JWT_SECRET must be configured with at least 32 bytes')
    claims = {'sub': str(user.id), 'role': user.role, 'exp': datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)}
    return jwt.encode(claims, settings.JWT_SECRET, algorithm='HS256')


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme), db: Session = Depends(get_db)) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail='Authentication required')
    secret = get_settings().JWT_SECRET
    if len(secret.encode('utf-8')) < 32:
        raise HTTPException(status_code=503, detail='JWT_SECRET must be configured with at least 32 bytes')
    try:
        payload = jwt.decode(credentials.credentials, secret, algorithms=['HS256'])
        user_id = int(payload['sub'])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail='Invalid or expired token')
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    return user


def require_roles(*roles: str):
    def dependency(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Insufficient permissions')
        return user
    return dependency
