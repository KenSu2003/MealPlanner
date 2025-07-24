#!/usr/bin/env python3
"""
Database Setup and Management Script for Meal Planner
This script provides comprehensive database initialization, sample data creation, and management functions.
"""

import sqlite3
import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import json

class MealPlannerDB:
    def __init__(self, db_path='meal_planner.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to the database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"✅ Connected to database: {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the database"""
        if self.conn:
            self.conn.close()
            print("✅ Disconnected from database")
    
    def create_tables(self):
        """Create all database tables"""
        try:
            # Users table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Meals table
            self.cursor.execute('''
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
            ''')
            
            # Ingredients table
            self.cursor.execute('''
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
            ''')
            
            # Meal plan table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS meal_plan (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    meal_id INTEGER,
                    meal_type TEXT,
                    user_id INTEGER,
                    FOREIGN KEY (meal_id) REFERENCES meals (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Favorites table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    meal_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (meal_id) REFERENCES meals (id),
                    UNIQUE(user_id, meal_id)
                )
            ''')
            
            # Shopping list table
            self.cursor.execute('''
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
            ''')
            
            self.conn.commit()
            print("✅ All tables created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
    
    def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Indexes for better query performance
            indexes = [
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
            
            for index in indexes:
                self.cursor.execute(index)
            
            self.conn.commit()
            print("✅ Database indexes created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating indexes: {e}")
            return False
    
    def insert_sample_data(self):
        """Insert sample data for testing and demonstration"""
        try:
            # Sample users
            sample_users = [
                ('admin', 'admin@mealplanner.com', 'admin123'),
                ('demo_user', 'demo@mealplanner.com', 'demo123'),
                ('test_user', 'test@mealplanner.com', 'test123')
            ]
            
            for username, email, password in sample_users:
                password_hash = generate_password_hash(password)
                try:
                    self.cursor.execute('''
                        INSERT INTO users (username, email, password_hash)
                        VALUES (?, ?, ?)
                    ''', (username, email, password_hash))
                except sqlite3.IntegrityError:
                    print(f"⚠️  User {username} already exists, skipping...")
            
            # Sample community meals
            sample_meals = [
                {
                    'name': 'Spaghetti Carbonara',
                    'ingredients': '400g spaghetti, 200g pancetta, 4 eggs, 100g parmesan, black pepper, salt',
                    'instructions': 'Cook pasta, fry pancetta, mix with eggs and cheese',
                    'prep_time': 10,
                    'cook_time': 20,
                    'servings': 4,
                    'category': 'Italian',
                    'is_community': True
                },
                {
                    'name': 'Chicken Stir Fry',
                    'ingredients': '500g chicken breast, 2 bell peppers, 1 onion, soy sauce, garlic, ginger, vegetable oil',
                    'instructions': 'Cut chicken, stir fry with vegetables and sauce',
                    'prep_time': 15,
                    'cook_time': 15,
                    'servings': 4,
                    'category': 'Asian',
                    'is_community': True
                },
                {
                    'name': 'Greek Salad',
                    'ingredients': '1 cucumber, 2 tomatoes, 1 red onion, 200g feta cheese, olives, olive oil, oregano',
                    'instructions': 'Chop vegetables, mix with cheese and dressing',
                    'prep_time': 10,
                    'cook_time': 0,
                    'servings': 4,
                    'category': 'Salad',
                    'is_community': True
                },
                {
                    'name': 'Beef Tacos',
                    'ingredients': '500g ground beef, taco seasoning, tortillas, lettuce, tomatoes, cheese, sour cream',
                    'instructions': 'Cook beef with seasoning, assemble tacos',
                    'prep_time': 10,
                    'cook_time': 15,
                    'servings': 4,
                    'category': 'Mexican',
                    'is_community': True
                },
                {
                    'name': 'Vegetable Curry',
                    'ingredients': '2 potatoes, 2 carrots, 1 onion, curry powder, coconut milk, rice',
                    'instructions': 'Cook vegetables in curry sauce, serve with rice',
                    'prep_time': 15,
                    'cook_time': 25,
                    'servings': 4,
                    'category': 'Indian',
                    'is_community': True
                }
            ]
            
            for meal in sample_meals:
                try:
                    self.cursor.execute('''
                        INSERT INTO meals (name, ingredients, instructions, prep_time, cook_time, servings, category, is_community)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (meal['name'], meal['ingredients'], meal['instructions'], 
                          meal['prep_time'], meal['cook_time'], meal['servings'], 
                          meal['category'], meal['is_community']))
                except sqlite3.IntegrityError:
                    print(f"⚠️  Meal {meal['name']} already exists, skipping...")
            
            # Sample ingredients
            sample_ingredients = [
                ('Chicken Breast', 2.0, 'lbs', 'Meat', None),
                ('Rice', 5.0, 'lbs', 'Pantry', None),
                ('Tomatoes', 6.0, 'pieces', 'Produce', None),
                ('Onions', 4.0, 'pieces', 'Produce', None),
                ('Olive Oil', 1.0, 'bottle', 'Pantry', None),
                ('Pasta', 2.0, 'lbs', 'Pantry', None),
                ('Cheese', 1.0, 'lbs', 'Dairy', None),
                ('Milk', 1.0, 'gallon', 'Dairy', None)
            ]
            
            # Get admin user ID for sample ingredients
            self.cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
            admin_id = self.cursor.fetchone()
            
            if admin_id:
                for ingredient in sample_ingredients:
                    try:
                        self.cursor.execute('''
                            INSERT INTO ingredients (name, quantity, unit, category, user_id)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (ingredient[0], ingredient[1], ingredient[2], ingredient[3], admin_id[0]))
                    except sqlite3.IntegrityError:
                        print(f"⚠️  Ingredient {ingredient[0]} already exists, skipping...")
            
            self.conn.commit()
            print("✅ Sample data inserted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error inserting sample data: {e}")
            return False
    
    def show_database_info(self):
        """Display database information and statistics"""
        try:
            print("\n📊 DATABASE INFORMATION")
            print("=" * 50)
            
            # Table counts
            tables = ['users', 'meals', 'ingredients', 'meal_plan', 'favorites', 'shopping_list']
            for table in tables:
                self.cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = self.cursor.fetchone()[0]
                print(f"{table.capitalize()}: {count} records")
            
            # Database size
            if os.path.exists(self.db_path):
                size = os.path.getsize(self.db_path)
                size_mb = size / (1024 * 1024)
                print(f"\nDatabase size: {size_mb:.2f} MB")
            
            # Sample data preview
            print("\n📋 SAMPLE DATA PREVIEW")
            print("=" * 50)
            
            # Show some users
            self.cursor.execute('SELECT username, email, created_at FROM users LIMIT 3')
            users = self.cursor.fetchall()
            print("\nUsers:")
            for user in users:
                print(f"  - {user[0]} ({user[1]}) - {user[2]}")
            
            # Show some meals
            self.cursor.execute('SELECT name, category, servings FROM meals WHERE is_community = TRUE LIMIT 3')
            meals = self.cursor.fetchall()
            print("\nCommunity Meals:")
            for meal in meals:
                print(f"  - {meal[0]} ({meal[1]}) - {meal[2]} servings")
            
            return True
            
        except Exception as e:
            print(f"❌ Error showing database info: {e}")
            return False
    
    def backup_database(self, backup_path=None):
        """Create a backup of the database"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"meal_planner_backup_{timestamp}.db"
        
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ Database backed up to: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Error backing up database: {e}")
            return False
    
    def reset_database(self):
        """Reset the database (delete all data)"""
        try:
            # Drop all tables
            tables = ['shopping_list', 'favorites', 'meal_plan', 'ingredients', 'meals', 'users']
            for table in tables:
                self.cursor.execute(f'DROP TABLE IF EXISTS {table}')
            
            # Drop indexes
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = self.cursor.fetchall()
            for index in indexes:
                if index[0] != 'sqlite_autoindex_users_1':  # Skip auto-created indexes
                    self.cursor.execute(f'DROP INDEX IF EXISTS {index[0]}')
            
            self.conn.commit()
            print("✅ Database reset successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error resetting database: {e}")
            return False

def main():
    """Main function to run database setup"""
    print("🍽️  MEAL PLANNER DATABASE SETUP")
    print("=" * 50)
    
    db = MealPlannerDB()
    
    if not db.connect():
        sys.exit(1)
    
    while True:
        print("\n📋 Available Operations:")
        print("1. Initialize database (create tables and indexes)")
        print("2. Insert sample data")
        print("3. Show database information")
        print("4. Backup database")
        print("5. Reset database (WARNING: deletes all data)")
        print("6. Full setup (initialize + sample data)")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == '1':
            print("\n🔄 Initializing database...")
            if db.create_tables() and db.create_indexes():
                print("✅ Database initialization completed!")
        
        elif choice == '2':
            print("\n🔄 Inserting sample data...")
            db.insert_sample_data()
        
        elif choice == '3':
            db.show_database_info()
        
        elif choice == '4':
            backup_name = input("Enter backup filename (or press Enter for auto-generated): ").strip()
            if not backup_name:
                backup_name = None
            db.backup_database(backup_name)
        
        elif choice == '5':
            confirm = input("⚠️  WARNING: This will delete ALL data! Type 'YES' to confirm: ")
            if confirm == 'YES':
                db.reset_database()
            else:
                print("❌ Reset cancelled")
        
        elif choice == '6':
            print("\n🔄 Running full database setup...")
            if db.create_tables() and db.create_indexes():
                db.insert_sample_data()
                db.show_database_info()
                print("✅ Full database setup completed!")
        
        elif choice == '0':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")
    
    db.disconnect()

if __name__ == "__main__":
    main() 