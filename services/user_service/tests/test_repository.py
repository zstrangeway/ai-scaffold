import pytest
from unittest.mock import Mock, patch
from sqlalchemy.exc import IntegrityError
from app.repository import UserRepository
from app.models import User


class TestUserRepository:
    """Unit tests for UserRepository"""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session"""
        return Mock()

    @pytest.fixture
    def user_repo(self, mock_session):
        """Create a user repository instance with mock session"""
        return UserRepository(mock_session)

    def test_create_user_success(self, user_repo, mock_session):
        """Test successful user creation"""
        # Mock the user creation
        mock_user = User(id="test-id", name="John Doe", email="john@example.com")
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None
        
        with patch('app.repository.User', return_value=mock_user):
            result = user_repo.create("John Doe", "john@example.com")
        
        assert result == mock_user
        mock_session.add.assert_called_once_with(mock_user)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_user)

    def test_create_user_duplicate_email(self, user_repo, mock_session):
        """Test creating user with duplicate email raises ValueError"""
        mock_session.commit.side_effect = IntegrityError("", "", "")
        mock_session.rollback.return_value = None
        
        with patch('app.repository.User'):
            with pytest.raises(ValueError, match="already exists"):
                user_repo.create("John Doe", "john@example.com")
        
        mock_session.rollback.assert_called_once()

    def test_get_by_id_existing_user(self, user_repo, mock_session):
        """Test getting user by existing ID"""
        mock_user = User(id="test-id", name="John Doe", email="john@example.com")
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = user_repo.get_by_id("test-id")
        
        assert result == mock_user
        mock_session.query.assert_called_once_with(User)
        mock_session.query.return_value.filter.assert_called_once()

    def test_get_by_id_nonexistent_user(self, user_repo, mock_session):
        """Test getting user by non-existent ID returns None"""
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = user_repo.get_by_id("nonexistent-id")
        
        assert result is None

    def test_get_by_email_existing_user(self, user_repo, mock_session):
        """Test getting user by existing email"""
        mock_user = User(id="test-id", name="John Doe", email="john@example.com")
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = user_repo.get_by_email("john@example.com")
        
        assert result == mock_user

    def test_get_by_email_nonexistent_user(self, user_repo, mock_session):
        """Test getting user by non-existent email returns None"""
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = user_repo.get_by_email("nonexistent@example.com")
        
        assert result is None

    def test_update_user_success(self, user_repo, mock_session):
        """Test successful user update"""
        mock_user = User(id="test-id", name="Old Name", email="old@example.com")
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        mock_session.commit.return_value = None
        
        result = user_repo.update("test-id", "New Name", "new@example.com")
        
        assert result == mock_user
        assert mock_user.name == "New Name"
        assert mock_user.email == "new@example.com"
        mock_session.commit.assert_called_once()

    def test_update_user_nonexistent(self, user_repo, mock_session):
        """Test updating non-existent user returns None"""
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = user_repo.update("nonexistent-id", "New Name", "new@example.com")
        
        assert result is None

    def test_update_user_duplicate_email(self, user_repo, mock_session):
        """Test updating user to duplicate email raises ValueError"""
        mock_user = User(id="test-id", name="Old Name", email="old@example.com")
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        mock_session.commit.side_effect = IntegrityError("", "", "")
        mock_session.rollback.return_value = None
        
        with pytest.raises(ValueError, match="already exists"):
            user_repo.update("test-id", "New Name", "duplicate@example.com")
        
        mock_session.rollback.assert_called_once()

    def test_delete_user_success(self, user_repo, mock_session):
        """Test successful user deletion"""
        mock_user = User(id="test-id", name="John Doe", email="john@example.com")
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        mock_session.delete.return_value = None
        mock_session.commit.return_value = None
        
        result = user_repo.delete("test-id")
        
        assert result is True
        mock_session.delete.assert_called_once_with(mock_user)
        mock_session.commit.assert_called_once()

    def test_delete_user_nonexistent(self, user_repo, mock_session):
        """Test deleting non-existent user returns False"""
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = user_repo.delete("nonexistent-id")
        
        assert result is False
        mock_session.delete.assert_not_called()

    def test_list_users_empty(self, user_repo, mock_session):
        """Test listing users when none exist"""
        mock_session.query.return_value.count.return_value = 0
        mock_session.query.return_value.offset.return_value.limit.return_value.all.return_value = []
        
        users, total = user_repo.list_users()
        
        assert users == []
        assert total == 0

    def test_list_users_with_data(self, user_repo, mock_session):
        """Test listing users with data"""
        mock_users = [
            User(id="1", name="User 1", email="user1@example.com"),
            User(id="2", name="User 2", email="user2@example.com"),
        ]
        mock_session.query.return_value.count.return_value = 2
        mock_session.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_users
        
        users, total = user_repo.list_users()
        
        assert users == mock_users
        assert total == 2

    def test_list_users_pagination(self, user_repo, mock_session):
        """Test pagination parameters"""
        mock_session.query.return_value.count.return_value = 10
        mock_session.query.return_value.offset.return_value.limit.return_value.all.return_value = []
        
        user_repo.list_users(page=2, limit=5)
        
        # Verify offset and limit were called with correct values
        # Page 2 with limit 5 should offset by 5
        mock_session.query.return_value.offset.assert_called_with(5)
        mock_session.query.return_value.offset.return_value.limit.assert_called_with(5) 