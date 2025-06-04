from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import User


class UserRepository:
    """Repository for user data access"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def create(self, name: str, email: str) -> User:
        """Create a new user"""
        user = User(name=name, email=email)
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"User with email {email} already exists")

    def update(self, user_id: str, name: str, email: str) -> Optional[User]:
        """Update an existing user"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        try:
            user.name = name
            user.email = email
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"User with email {email} already exists")

    def delete(self, user_id: str) -> bool:
        """Delete a user by ID"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True

    def list_users(self, page: int = 1, limit: int = 10) -> tuple[List[User], int]:
        """List users with pagination"""
        offset = (page - 1) * limit
        
        # Get total count
        total = self.db.query(User).count()
        
        # Get paginated results
        users = (
            self.db.query(User)
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        return users, total 