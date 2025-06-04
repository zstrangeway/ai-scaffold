from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from passlib.context import CryptContext
import uuid

Base = declarative_base()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """User model for the database"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=True)  # Nullable for users created without passwords
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def set_password(self, password: str) -> None:
        """Hash and set the user's password"""
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash"""
        if not self.password_hash:
            return False
        return pwd_context.verify(password, self.password_hash)

    def has_password(self) -> bool:
        """Check if the user has a password set"""
        return self.password_hash is not None

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>" 