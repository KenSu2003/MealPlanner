#!/usr/bin/env python3
import sqlite3

def fix_database():
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    try:
        # Add user_id column to meals table if it doesn't exist
        cursor.execute("PRAGMA table_info(meals)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' not in columns:
            print("Adding user_id column to meals table...")
            cursor.execute('ALTER TABLE meals ADD COLUMN user_id INTEGER')
            print("✓ Added user_id column to meals table")
        
        # Add user_id column to ingredients table if it doesn't exist
        cursor.execute("PRAGMA table_info(ingredients)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' not in columns:
            print("Adding user_id column to ingredients table...")
            cursor.execute('ALTER TABLE ingredients ADD COLUMN user_id INTEGER')
            print("✓ Added user_id column to ingredients table")
        
        # Add user_id column to meal_plan table if it doesn't exist
        cursor.execute("PRAGMA table_info(meal_plan)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' not in columns:
            print("Adding user_id column to meal_plan table...")
            cursor.execute('ALTER TABLE meal_plan ADD COLUMN user_id INTEGER')
            print("✓ Added user_id column to meal_plan table")
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
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
            print("✓ Created users table")
        
        conn.commit()
        print("\n🎉 Database fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    fix_database() 