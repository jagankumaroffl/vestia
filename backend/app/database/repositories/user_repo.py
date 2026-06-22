from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.models import User, UserPreference


class UserRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Create ────────────────────────────────────────────────────────────────

    def create(
        self,
        username: str,
        email: str,
        body_type: str = "regular",
        gender: str = "unisex",
        preferred_style: Optional[str] = None,
    ) -> User:
        user = User(
            username=username,
            email=email,
            body_type=body_type,
            gender=gender,
            preferred_style=preferred_style,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Auto-create empty preferences row
        prefs = UserPreference(user_id=user.id)
        self.db.add(prefs)
        self.db.commit()

        return user

    def get_or_create_default(self) -> User:
        """Ensure the single default user (id=1) exists. Used in single-user mode."""
        user = self.get_by_id(1)
        if not user:
            user = self.create(username="default", email="user@vestia.app")
        return user

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, user_id: int, data: dict) -> Optional[User]:
        user = self.get_by_id(user_id)
        if not user:
            return None
        for key, value in data.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    # ── Preferences ───────────────────────────────────────────────────────────

    def get_preferences(self, user_id: int) -> Optional[UserPreference]:
        return (
            self.db.query(UserPreference)
            .filter(UserPreference.user_id == user_id)
            .first()
        )

    def update_preferences(self, user_id: int, data: dict) -> Optional[UserPreference]:
        prefs = self.get_preferences(user_id)
        if not prefs:
            prefs = UserPreference(user_id=user_id)
            self.db.add(prefs)

        for key, value in data.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)

        self.db.commit()
        self.db.refresh(prefs)
        return prefs

    # ── Delete ────────────────────────────────────────────────────────────────

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
