#!/usr/bin/env python3
"""
Database migration script to add user_id and is_community columns
to existing tables for the meal planner application.
"""

import sqlite3
import os

def migrate_database():
    """Migrate the existing database to include user_id and is_community columns."""
    
    db_path = 'meal_planner.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. Creating new database with updated schema...")
        return
    
    print("Starting database migration...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        users_table_exists = cursor.fetchone() is not None
        
        if not users_table_exists:
            print("Creating users table...")
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("✓ Users table created")
        else:
            print("✓ Users table already exists")
        
        # Check if meals table has user_id column
        cursor.execute("PRAGMA table_info(meals)")
        meals_columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' not in meals_columns:
            print("Adding user_id column to meals table...")
            cursor.execute('ALTER TABLE meals ADD COLUMN user_id INTEGER')
            print("✓ user_id column added to meals table")
        else:
            print("✓ user_id column already exists in meals table")
        
        if 'is_community' not in meals_columns:
            print("Adding is_community column to meals table...")
            cursor.execute('ALTER TABLE meals ADD COLUMN is_community BOOLEAN DEFAULT FALSE')
            print("✓ is_community column added to meals table")
        else:
            print("✓ is_community column already exists in meals table")
        
        # Check if ingredients table has user_id column
        cursor.execute("PRAGMA table_info(ingredients)")
        ingredients_columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' not in ingredients_columns:
            print("Adding user_id column to ingredients table...")
            cursor.execute('ALTER TABLE ingredients ADD COLUMN user_id INTEGER')
            print("✓ user_id column added to ingredients table")
        else:
            print("✓ user_id column already exists in ingredients table")
        
        # Check if meal_plan table has user_id column
        cursor.execute("PRAGMA table_info(meal_plan)")
        meal_plan_columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' not in meal_plan_columns:
            print("Adding user_id column to meal_plan table...")
            cursor.execute('ALTER TABLE meal_plan ADD COLUMN user_id INTEGER')
            print("✓ user_id column added to meal_plan table")
        else:
            print("✓ user_id column already exists in meal_plan table")
        
        # Commit all changes
        conn.commit()
        print("\n✓ Database migration completed successfully!")
        
        # Show table structure
        print("\nUpdated table structure:")
        for table_name in ['users', 'meals', 'ingredients', 'meal_plan']:
            print(f"\n{table_name} table:")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database() 