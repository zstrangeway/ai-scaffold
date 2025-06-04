import pytest
from unittest.mock import patch, Mock
from app.models import User


class TestUserModel:
    """Unit tests for User model"""

    def test_user_creation(self):
        """Test creating a user model instance"""
        user = User(name="John Doe", email="john@example.com")
        
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.id is None  # Not set until saved to database
        assert user.created_at is None  # Not set until saved to database
        assert user.updated_at is None

    def test_user_creation_with_id(self):
        """Test creating a user model with explicit ID"""
        user = User(id="test-id", name="John Doe", email="john@example.com")
        
        assert user.id == "test-id"
        assert user.name == "John Doe"
        assert user.email == "john@example.com"

    def test_user_repr(self):
        """Test User __repr__ method"""
        user = User(id="test-id", name="John Doe", email="john@example.com")
        
        repr_str = repr(user)
        
        assert "User(id=test-id" in repr_str
        assert "name=John Doe" in repr_str
        assert "email=john@example.com" in repr_str

    def test_user_repr_without_id(self):
        """Test User __repr__ method without ID"""
        user = User(name="John Doe", email="john@example.com")
        
        repr_str = repr(user)
        
        assert "User(id=None" in repr_str
        assert "name=John Doe" in repr_str
        assert "email=john@example.com" in repr_str

    def test_user_table_name(self):
        """Test that User model has correct table name"""
        assert User.__tablename__ == "users"

    def test_user_columns(self):
        """Test that User model has expected columns"""
        # Check that the columns exist
        assert hasattr(User, 'id')
        assert hasattr(User, 'name')
        assert hasattr(User, 'email')
        assert hasattr(User, 'created_at')
        assert hasattr(User, 'updated_at')
        
        # Check column properties
        assert User.id.primary_key is True
        assert User.email.unique is True
        assert User.name.nullable is False
        assert User.email.nullable is False

    @patch('app.models.uuid.uuid4')
    def test_user_id_default_generation(self, mock_uuid):
        """Test that User ID default function generates UUID string"""
        mock_uuid.return_value.hex = "mock-uuid-hex"
        
        # Test the default function directly
        user = User(name="Test", email="test@example.com")
        default_func = User.id.default.arg
        
        # Call the default function with mock context (SQLAlchemy passes context)
        mock_context = Mock()
        result = default_func(mock_context)
        
        # Should return string representation of UUID
        assert isinstance(result, str)
        mock_uuid.assert_called_once()

    def test_user_attribute_assignment(self):
        """Test that user attributes can be assigned"""
        user = User()
        
        user.id = "test-id"
        user.name = "John Doe"
        user.email = "john@example.com"
        
        assert user.id == "test-id"
        assert user.name == "John Doe"
        assert user.email == "john@example.com"

    def test_user_equality(self):
        """Test user equality comparison"""
        user1 = User(id="same-id", name="John", email="john@example.com")
        user2 = User(id="same-id", name="John", email="john@example.com")
        user3 = User(id="different-id", name="John", email="john@example.com")
        
        # SQLAlchemy models use identity comparison by default
        # These will not be equal unless they're the same instance
        assert user1 != user2  # Different instances
        assert user1 == user1  # Same instance
        assert user1 != user3  # Different instances

    def test_user_set_password(self):
        """Test password setting functionality"""
        user = User(name="John Doe", email="john@example.com")
        
        # Initially no password
        assert not user.has_password()
        assert user.password_hash is None
        
        # Set password
        user.set_password("mypassword123")
        
        # Should now have password
        assert user.has_password()
        assert user.password_hash is not None
        assert user.password_hash != "mypassword123"  # Should be hashed

    def test_user_verify_password(self):
        """Test password verification"""
        user = User(name="John Doe", email="john@example.com")
        user.set_password("correct_password")
        
        # Should verify correct password
        assert user.verify_password("correct_password") is True
        
        # Should reject wrong password
        assert user.verify_password("wrong_password") is False
        assert user.verify_password("") is False

    def test_user_verify_password_no_password_set(self):
        """Test password verification when no password is set"""
        user = User(name="John Doe", email="john@example.com")
        
        # Should always return False if no password is set
        assert user.verify_password("any_password") is False
        assert user.verify_password("") is False

    def test_user_has_password(self):
        """Test has_password functionality"""
        user = User(name="John Doe", email="john@example.com")
        
        # Initially no password
        assert user.has_password() is False
        
        # Set password
        user.set_password("password123")
        assert user.has_password() is True
        
        # Clear password hash manually to test edge case
        user.password_hash = None
        assert user.has_password() is False

    def test_password_hashing_is_consistent(self):
        """Test that the same password produces different hashes (due to salt)"""
        user1 = User(name="User 1", email="user1@example.com")
        user2 = User(name="User 2", email="user2@example.com")
        
        password = "same_password_123"
        
        user1.set_password(password)
        user2.set_password(password)
        
        # Hashes should be different due to salt
        assert user1.password_hash != user2.password_hash
        
        # But both should verify the same password
        assert user1.verify_password(password) is True
        assert user2.verify_password(password) is True

    def test_password_update(self):
        """Test updating an existing password"""
        user = User(name="John Doe", email="john@example.com")
        
        # Set initial password
        user.set_password("old_password")
        old_hash = user.password_hash
        
        # Update password
        user.set_password("new_password")
        new_hash = user.password_hash
        
        # Hash should change
        assert old_hash != new_hash
        
        # Old password should no longer work
        assert user.verify_password("old_password") is False
        
        # New password should work
        assert user.verify_password("new_password") is True 