import sqlite3
import pytest
from unittest.mock import patch

from src.database_engine import DatabaseEngine
from src.definitions import sScannerObject

TEST_PATH = "/fake/dir"

@pytest.fixture
def in_memory_db():
    """Fixture to create an in-memory database and engine for testing."""
    # Use :memory: to create a temporary, in-memory database
    engine = DatabaseEngine(db_path=":memory:")
    engine.create_schema()
    return engine

@patch('src.database_engine.get_volume_identifier', return_value='test_volume_id_123')
def test_session_creation_for_new_scan(mock_get_id, in_memory_db: DatabaseEngine):
    """
    Verify that a new scan creates a new session entry in the import_log.
    """
    # Act
    import_id = in_memory_db.get_or_create_import_session(TEST_PATH)

    # Assert
    assert import_id == 1  # First entry should have ID 1

    with in_memory_db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM import_log")
        count = cursor.fetchone()[0]
        assert count == 1

        cursor.execute("SELECT sourceIdentifier, sourcePath FROM import_log WHERE importId = ?", (import_id,))
        result = cursor.fetchone()
        assert result == ('test_volume_id_123', TEST_PATH)

@patch('src.database_engine.get_volume_identifier', return_value='test_volume_id_123')
def test_session_refresh_clears_old_data(mock_get_id, in_memory_db: DatabaseEngine):
    """
    Verify that re-scanning the same path reuses the session ID and clears old data.
    """
    # Arrange: First scan
    first_import_id = in_memory_db.get_or_create_import_session(TEST_PATH)
    assert first_import_id == 1

    # Insert some dummy data for the first scan
    dummy_object = sScannerObject("file.txt", 1, 2, 0, 1024, 123456, "")
    in_memory_db.insert_scanner_objects(iter([dummy_object]), import_id=first_import_id)

    # Check that data was inserted
    with in_memory_db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM scanned_objects WHERE importId = ?", (first_import_id,))
        count_before = cursor.fetchone()[0]
        assert count_before == 1

    # Act: Second scan of the same path
    second_import_id = in_memory_db.get_or_create_import_session(TEST_PATH)

    # Assert
    # 1. The import ID should be the same
    assert second_import_id == first_import_id

    # 2. The import_log should still have only one entry
    with in_memory_db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM import_log")
        log_count = cursor.fetchone()[0]
        assert log_count == 1

        # 3. The old data in scanned_objects for that importId should be gone
        cursor.execute("SELECT COUNT(*) FROM scanned_objects WHERE importId = ?", (second_import_id,))
        count_after = cursor.fetchone()[0]
        assert count_after == 0