#!/usr/bin/env python3
"""
Database Migration System for Meal Planner
Handles database schema updates and migrations between versions.
"""

import sqlite3
import os
import sys
from datetime import datetime

class DatabaseMigration:
    def __init__(self, db_path='meal_planner.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.migrations_table = 'database_migrations'
    
    def connect(self):
        """Connect to the database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the database"""
        if self.conn:
            self.conn.close()
    
    def create_migrations_table(self):
        """Create the migrations tracking table"""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS database_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    migration_name TEXT UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    version TEXT,
                    description TEXT
                )
            ''')
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error creating migrations table: {e}")
            return False
    
    def get_applied_migrations(self):
        """Get list of applied migrations"""
        try:
            self.cursor.execute('SELECT migration_name FROM database_migrations ORDER BY applied_at')
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"❌ Error getting applied migrations: {e}")
            return []
    
    def mark_migration_applied(self, migration_name, version=None, description=None):
        """Mark a migration as applied"""
        try:
            self.cursor.execute('''
                INSERT INTO database_migrations (migration_name, version, description)
                VALUES (?, ?, ?)
            ''', (migration_name, version, description))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error marking migration as applied: {e}")
            return False
    
    def run_migration(self, migration_name, sql_commands, version=None, description=None):
        """Run a specific migration"""
        try:
            print(f"🔄 Running migration: {migration_name}")
            
            # Check if migration already applied
            applied_migrations = self.get_applied_migrations()
            if migration_name in applied_migrations:
                print(f"⚠️  Migration {migration_name} already applied, skipping...")
                return True
            
            # Execute migration
            for command in sql_commands:
                self.cursor.execute(command)
            
            self.conn.commit()
            
            # Mark as applied
            self.mark_migration_applied(migration_name, version, description)
            
            print(f"✅ Migration {migration_name} completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error running migration {migration_name}: {e}")
            self.conn.rollback()
            return False
    
    def run_all_migrations(self):
        """Run all pending migrations"""
        print("🔄 Running all pending migrations...")
        
        # Create migrations table if it doesn't exist
        if not self.create_migrations_table():
            return False
        
        # Define all migrations
        migrations = [
            {
                'name': '001_initial_schema',
                'version': '1.0.0',
                'description': 'Initial database schema with all tables',
                'sql': [
                    '''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    ''',
                    '''
                    CREATE TABLE IF NOT EXISTS meals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        ingredients TEXT NOT NULL,
                        instructions TEXT,
                        prep_time INTEGER,
                        cook_time INTEGER,
                        servings INTEGER,
                        category TEXT,
                        user_id INTEGER,
                        is_community BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                    ''',
                    '''
                    CREATE TABLE IF NOT EXISTS ingredients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        quantity REAL,
                        unit TEXT,
                        category TEXT,
                        expiry_date DATE,
                        user_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                    ''',
                    '''
                    CREATE TABLE IF NOT EXISTS meal_plan (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE NOT NULL,
                        meal_id INTEGER,
                        meal_type TEXT,
                        user_id INTEGER,
                        FOREIGN KEY (meal_id) REFERENCES meals (id),
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                    ''',
                    '''
                    CREATE TABLE IF NOT EXISTS favorites (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        meal_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (meal_id) REFERENCES meals (id),
                        UNIQUE(user_id, meal_id)
                    )
                    ''',
                    '''
                    CREATE TABLE IF NOT EXISTS shopping_list (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        quantity REAL,
                        unit TEXT,
                        category TEXT,
                        is_purchased BOOLEAN DEFAULT FALSE,
                        user_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                    '''
                ]
            },
            {
                'name': '002_add_indexes',
                'version': '1.1.0',
                'description': 'Add performance indexes',
                'sql': [
                    "CREATE INDEX IF NOT EXISTS idx_meals_user_id ON meals(user_id)",
                    "CREATE INDEX IF NOT EXISTS idx_meals_category ON meals(category)",
                    "CREATE INDEX IF NOT EXISTS idx_meal_plan_date ON meal_plan(date)",
                    "CREATE INDEX IF NOT EXISTS idx_meal_plan_user_id ON meal_plan(user_id)",
                    "CREATE INDEX IF NOT EXISTS idx_ingredients_user_id ON ingredients(user_id)",
                    "CREATE INDEX IF NOT EXISTS idx_ingredients_category ON ingredients(category)",
                    "CREATE INDEX IF NOT EXISTS idx_shopping_list_user_id ON shopping_list(user_id)",
                    "CREATE INDEX IF NOT EXISTS idx_shopping_list_category ON shopping_list(category)",
                    "CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id)",
                    "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
                    "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"
                ]
            },
            {
                'name': '003_add_meal_notes',
                'version': '1.2.0',
                'description': 'Add notes field to meals table',
                'sql': [
                    "ALTER TABLE meals ADD COLUMN notes TEXT"
                ]
            },
            {
                'name': '004_add_ingredient_notes',
                'version': '1.2.1',
                'description': 'Add notes field to ingredients table',
                'sql': [
                    "ALTER TABLE ingredients ADD COLUMN notes TEXT"
                ]
            },
            {
                'name': '005_add_shopping_list_notes',
                'version': '1.2.2',
                'description': 'Add notes field to shopping list table',
                'sql': [
                    "ALTER TABLE shopping_list ADD COLUMN notes TEXT"
                ]
            }
        ]
        
        # Run each migration
        for migration in migrations:
            if not self.run_migration(
                migration['name'],
                migration['sql'],
                migration['version'],
                migration['description']
            ):
                return False
        
        print("✅ All migrations completed successfully!")
        return True
    
    def show_migration_status(self):
        """Show the status of all migrations"""
        try:
            print("\n📊 MIGRATION STATUS")
            print("=" * 50)
            
            # Get applied migrations
            self.cursor.execute('''
                SELECT migration_name, version, description, applied_at 
                FROM database_migrations 
                ORDER BY applied_at
            ''')
            applied_migrations = self.cursor.fetchall()
            
            if applied_migrations:
                print("✅ Applied Migrations:")
                for migration in applied_migrations:
                    print(f"  - {migration[0]} (v{migration[1]}) - {migration[2]}")
                    print(f"    Applied: {migration[3]}")
            else:
                print("⚠️  No migrations have been applied yet")
            
            # Show database version
            if applied_migrations:
                latest_version = applied_migrations[-1][1]
                print(f"\n📋 Current Database Version: {latest_version}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error showing migration status: {e}")
            return False
    
    def rollback_migration(self, migration_name):
        """Rollback a specific migration (WARNING: This can cause data loss)"""
        try:
            print(f"⚠️  WARNING: Rolling back migration {migration_name}")
            confirm = input("This may cause data loss. Type 'ROLLBACK' to confirm: ")
            
            if confirm != 'ROLLBACK':
                print("❌ Rollback cancelled")
                return False
            
            # Remove migration record
            self.cursor.execute('DELETE FROM database_migrations WHERE migration_name = ?', (migration_name,))
            self.conn.commit()
            
            print(f"✅ Migration {migration_name} rolled back")
            return True
            
        except Exception as e:
            print(f"❌ Error rolling back migration: {e}")
            return False

def main():
    """Main function for migration management"""
    print("🔄 MEAL PLANNER DATABASE MIGRATIONS")
    print("=" * 50)
    
    migration = DatabaseMigration()
    
    if not migration.connect():
        sys.exit(1)
    
    while True:
        print("\n📋 Available Operations:")
        print("1. Run all pending migrations")
        print("2. Show migration status")
        print("3. Rollback a migration (WARNING: may cause data loss)")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-3): ").strip()
        
        if choice == '1':
            migration.run_all_migrations()
        
        elif choice == '2':
            migration.show_migration_status()
        
        elif choice == '3':
            migration_name = input("Enter migration name to rollback: ").strip()
            if migration_name:
                migration.rollback_migration(migration_name)
        
        elif choice == '0':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")
    
    migration.disconnect()

if __name__ == "__main__":
    main() 