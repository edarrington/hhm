"""Household authentication and authorization"""
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jwt import decode, encode, ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta
from uuid import UUID
from src.config import get_settings

settings = get_settings()
security = HTTPBearer()


class AuthTokenPayload:
    """JWT token payload"""
    def __init__(self, household_id: UUID, user_id: UUID, email: str, role: str):
        self.household_id = household_id
        self.user_id = user_id
        self.email = email
        self.role = role


def create_access_token(
    household_id: UUID,
    user_id: UUID,
    email: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.jwt_expiration_hours)
    
    expire = datetime.utcnow() + expires_delta
    payload = {
        "household_id": str(household_id),
        "user_id": str(user_id),
        "email": email,
        "role": role,
        "exp": expire,
    }
    
    return encode(
        payload,
        settings.household_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def verify_token(token: str) -> AuthTokenPayload:
    """Verify and decode JWT token"""
    try:
        payload = decode(
            token,
            settings.household_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        
        household_id = UUID(payload.get("household_id"))
        user_id = UUID(payload.get("user_id"))
        email = payload.get("email")
        role = payload.get("role", "member")
        
        return AuthTokenPayload(
            household_id=household_id,
            user_id=user_id,
            email=email,
            role=role,
        )
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
) -> AuthTokenPayload:
    """Get current authenticated user"""
    token = credentials.credentials
    return verify_token(token)


async def require_admin(
    user: AuthTokenPayload = Depends(get_current_user),
) -> AuthTokenPayload:
    """Require admin role"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
