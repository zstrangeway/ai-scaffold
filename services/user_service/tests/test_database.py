import pytest
from unittest.mock import patch, Mock
from app.database import create_tables, get_db, get_test_db, DATABASE_URL


class TestDatabase:
    """Unit tests for database module"""

    def test_database_url_default(self):
        """Test that DATABASE_URL has a default value"""
        assert DATABASE_URL is not None
        assert "postgresql://" in DATABASE_URL

    @patch('app.database.Base.metadata.create_all')
    @patch('app.database.engine')
    def test_create_tables(self, mock_engine, mock_create_all):
        """Test create_tables function calls SQLAlchemy properly"""
        create_tables()
        
        mock_create_all.assert_called_once_with(bind=mock_engine)

    @patch('app.database.SessionLocal')
    def test_get_db_generator(self, mock_session_local):
        """Test get_db function returns a generator that yields and closes session"""
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        
        # Get the generator
        db_gen = get_db()
        
        # Get the session from the generator
        session = next(db_gen)
        
        assert session == mock_session
        mock_session_local.assert_called_once()
        
        # Complete the generator to trigger cleanup
        try:
            next(db_gen)
        except StopIteration:
            pass
        
        mock_session.close.assert_called_once()

    @patch('app.database.SessionLocal')
    def test_get_test_db(self, mock_session_local):
        """Test get_test_db function creates and returns session"""
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        
        session = get_test_db()
        
        assert session == mock_session
        mock_session_local.assert_called_once()

    @patch.dict('os.environ', {'DATABASE_URL': 'postgresql://custom:pass@localhost:5432/test'})
    def test_database_url_from_env(self):
        """Test that DATABASE_URL can be set from environment variable"""
        # Need to reload the module to pick up new environment variable
        import importlib
        from app import database
        importlib.reload(database)
        
        assert database.DATABASE_URL == 'postgresql://custom:pass@localhost:5432/test' 