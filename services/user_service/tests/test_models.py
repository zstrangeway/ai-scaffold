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
        user1 = User(id="test-id", name="John Doe", email="john@example.com")
        user2 = User(id="test-id", name="John Doe", email="john@example.com")
        user3 = User(id="different-id", name="John Doe", email="john@example.com")
        
        # Note: SQLAlchemy models use identity comparison by default
        # These will not be equal unless they're the same instance
        assert user1 != user2  # Different instances
        assert user1 == user1  # Same instance
        assert user1 != user3  # Different IDs 