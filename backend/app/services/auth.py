from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.jwt import create_access_token
from backend.app.core.security import hash_password, verify_password
from backend.app.db.models import User


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, email: str, password: str) -> User:
        normalized_email = email.strip().lower()

        existing_user = self.db.scalar(
            select(User).where(User.email == normalized_email)
        )

        if existing_user:
            raise ValueError("Email is already registered.")

        user = User(
            email=normalized_email,
            password_hash=hash_password(password),
            is_active=True,
            is_verified=False,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def authenticate(self, email: str, password: str) -> str:
        normalized_email = email.strip().lower()

        user = self.db.scalar(
            select(User).where(User.email == normalized_email)
        )

        if not user or not verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password.")

        if not user.is_active:
            raise ValueError("User account is inactive.")

        user.last_login_at = datetime.now(timezone.utc)

        self.db.commit()

        return create_access_token(user.id)
