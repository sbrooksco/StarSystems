"""Tests for DatabaseConnection."""

import pytest
import sqlite3
from starsystems.database import DatabaseConnection


class TestDatabaseConnection:
    """Test cases for DatabaseConnection."""
    
    def test_connection_creation(self, temp_db_path):
        """Test creating a database connection."""
        db = DatabaseConnection(temp_db_path)
        assert db.db_path == temp_db_path
    
    def test_initialize_schema(self, temp_db_path):
        """Test schema initialization."""
        db = DatabaseConnection(temp_db_path)
        db.initialize_schema()
        
        # Verify tables exist
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check star_systems table
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='star_systems'
            """)
            assert cursor.fetchone() is not None
            
            # Check planets table
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='planets'
            """)
            assert cursor.fetchone() is not None
    
    def test_initialize_schema_creates_indexes(self, temp_db_path):
        """Test that indexes are created."""
        db = DatabaseConnection(temp_db_path)
        db.initialize_schema()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check for indexes
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name='idx_distance'
            """)
            assert cursor.fetchone() is not None
            
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name='idx_spectral_type'
            """)
            assert cursor.fetchone() is not None
    
    def test_get_connection_context_manager(self, db_connection):
        """Test context manager for connections."""
        with db_connection.get_connection() as conn:
            assert isinstance(conn, sqlite3.Connection)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
    
    def test_multiple_initialize_calls_idempotent(self, temp_db_path):
        """Test that multiple initialize calls don't cause errors."""
        db = DatabaseConnection(temp_db_path)
        
        # Should be safe to call multiple times
        db.initialize_schema()
        db.initialize_schema()
        db.initialize_schema()
        
        # Verify still works
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            assert len(tables) >= 2  # At least star_systems and planets


class TestDatabaseConnectionIntegration:
    """Integration tests for database connection."""
    
    def test_basic_insert_query(self, db_connection):
        """Test basic database operations."""
        with db_connection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert
            cursor.execute("""
                INSERT INTO star_systems (name, spectral_type, distance_ly)
                VALUES (?, ?, ?)
            """, ("Test System", "G2V", 10.0))
            conn.commit()
            
            # Query
            cursor.execute("SELECT * FROM star_systems WHERE name = ?", ("Test System",))
            row = cursor.fetchone()
            
            assert row[0] == "Test System"
            assert row[1] == "G2V"
            assert row[2] == 10.0
    
    def test_foreign_key_constraint(self, db_connection):
        """Test that foreign key constraints work."""
        with db_connection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert system
            cursor.execute("""
                INSERT INTO star_systems (name, spectral_type, distance_ly)
                VALUES (?, ?, ?)
            """, ("Parent System", "K5V", 15.0))
            
            # Insert planet with valid foreign key
            cursor.execute("""
                INSERT INTO planets (name, mass, radius, orbit_distance, system_name)
                VALUES (?, ?, ?, ?, ?)
            """, ("Planet", 1.0, 1.0, 1.0, "Parent System"))
            
            conn.commit()
            
            # Verify planet was inserted
            cursor.execute("SELECT COUNT(*) FROM planets WHERE system_name = ?", 
                         ("Parent System",))
            count = cursor.fetchone()[0]
            assert count == 1
