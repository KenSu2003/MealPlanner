#!/usr/bin/env python3
"""
Database Maintenance Script for Meal Planner
Provides backup, optimization, and health check functionality.
"""

import sqlite3
import os
import sys
import shutil
import gzip
from datetime import datetime, timedelta
import json

class DatabaseMaintenance:
    def __init__(self, db_path='meal_planner.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.backup_dir = 'database_backups'
    
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
    
    def create_backup_directory(self):
        """Create backup directory if it doesn't exist"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            print(f"✅ Created backup directory: {self.backup_dir}")
    
    def create_backup(self, compress=True):
        """Create a backup of the database"""
        try:
            self.create_backup_directory()
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"meal_planner_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Create backup
            shutil.copy2(self.db_path, backup_path)
            
            # Compress if requested
            if compress:
                compressed_path = backup_path + '.gz'
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove uncompressed backup
                os.remove(backup_path)
                backup_path = compressed_path
            
            # Get backup size
            size = os.path.getsize(backup_path)
            size_mb = size / (1024 * 1024)
            
            print(f"✅ Backup created: {backup_path}")
            print(f"📊 Backup size: {size_mb:.2f} MB")
            
            return backup_path
            
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return None
    
    def list_backups(self):
        """List all available backups"""
        try:
            self.create_backup_directory()
            
            backups = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('meal_planner_backup_') and (filename.endswith('.db') or filename.endswith('.db.gz')):
                    filepath = os.path.join(self.backup_dir, filename)
                    size = os.path.getsize(filepath)
                    size_mb = size / (1024 * 1024)
                    modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    backups.append({
                        'filename': filename,
                        'path': filepath,
                        'size_mb': size_mb,
                        'modified': modified_time
                    })
            
            # Sort by modification time (newest first)
            backups.sort(key=lambda x: x['modified'], reverse=True)
            
            if backups:
                print("\n📋 AVAILABLE BACKUPS")
                print("=" * 60)
                for backup in backups:
                    print(f"📁 {backup['filename']}")
                    print(f"   Size: {backup['size_mb']:.2f} MB")
                    print(f"   Created: {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
                    print()
            else:
                print("⚠️  No backups found")
            
            return backups
            
        except Exception as e:
            print(f"❌ Error listing backups: {e}")
            return []
    
    def restore_backup(self, backup_filename):
        """Restore database from backup"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            if not os.path.exists(backup_path):
                print(f"❌ Backup file not found: {backup_path}")
                return False
            
            # Confirm restoration
            print(f"⚠️  WARNING: This will overwrite the current database!")
            confirm = input(f"Type 'RESTORE' to confirm restoration from {backup_filename}: ")
            
            if confirm != 'RESTORE':
                print("❌ Restoration cancelled")
                return False
            
            # Create backup of current database before restoration
            print("🔄 Creating backup of current database...")
            self.create_backup(compress=False)
            
            # Restore from backup
            if backup_filename.endswith('.gz'):
                # Decompress first
                temp_path = backup_path[:-3]  # Remove .gz
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_path = temp_path
            
            # Close current connection
            self.disconnect()
            
            # Copy backup to main database
            shutil.copy2(backup_path, self.db_path)
            
            # Remove temporary file if it was decompressed
            if backup_filename.endswith('.gz') and os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Reconnect
            self.connect()
            
            print(f"✅ Database restored from {backup_filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error restoring backup: {e}")
            return False
    
    def optimize_database(self):
        """Optimize the database for better performance"""
        try:
            print("🔄 Optimizing database...")
            
            # VACUUM to reclaim space and optimize
            self.cursor.execute("VACUUM")
            
            # Analyze tables for better query planning
            self.cursor.execute("ANALYZE")
            
            # Update statistics
            self.cursor.execute("PRAGMA optimize")
            
            self.conn.commit()
            print("✅ Database optimization completed")
            return True
            
        except Exception as e:
            print(f"❌ Error optimizing database: {e}")
            return False
    
    def check_database_integrity(self):
        """Check database integrity"""
        try:
            print("🔍 Checking database integrity...")
            
            # Check integrity
            self.cursor.execute("PRAGMA integrity_check")
            integrity_result = self.cursor.fetchone()
            
            if integrity_result[0] == 'ok':
                print("✅ Database integrity check passed")
                return True
            else:
                print(f"❌ Database integrity issues found: {integrity_result[0]}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking database integrity: {e}")
            return False
    
    def get_database_stats(self):
        """Get comprehensive database statistics"""
        try:
            print("\n📊 DATABASE STATISTICS")
            print("=" * 50)
            
            # Database size
            if os.path.exists(self.db_path):
                size = os.path.getsize(self.db_path)
                size_mb = size / (1024 * 1024)
                print(f"Database size: {size_mb:.2f} MB")
            
            # Table statistics
            tables = ['users', 'meals', 'ingredients', 'meal_plan', 'favorites', 'shopping_list']
            
            print("\n📋 Table Statistics:")
            for table in tables:
                try:
                    self.cursor.execute(f'SELECT COUNT(*) FROM {table}')
                    count = self.cursor.fetchone()[0]
                    print(f"  {table.capitalize()}: {count} records")
                except Exception:
                    print(f"  {table.capitalize()}: Table not found")
            
            # Database settings
            print("\n⚙️  Database Settings:")
            settings = [
                ('journal_mode', 'PRAGMA journal_mode'),
                ('synchronous', 'PRAGMA synchronous'),
                ('cache_size', 'PRAGMA cache_size'),
                ('temp_store', 'PRAGMA temp_store')
            ]
            
            for setting_name, pragma in settings:
                try:
                    self.cursor.execute(pragma)
                    value = self.cursor.fetchone()[0]
                    print(f"  {setting_name}: {value}")
                except Exception:
                    print(f"  {setting_name}: Unable to retrieve")
            
            return True
            
        except Exception as e:
            print(f"❌ Error getting database stats: {e}")
            return False
    
    def cleanup_old_backups(self, days_to_keep=30):
        """Clean up old backup files"""
        try:
            self.create_backup_directory()
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            deleted_count = 0
            
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('meal_planner_backup_'):
                    filepath = os.path.join(self.backup_dir, filename)
                    modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    if modified_time < cutoff_date:
                        os.remove(filepath)
                        deleted_count += 1
                        print(f"🗑️  Deleted old backup: {filename}")
            
            if deleted_count == 0:
                print("✅ No old backups to clean up")
            else:
                print(f"✅ Cleaned up {deleted_count} old backup(s)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error cleaning up old backups: {e}")
            return False
    
    def export_data(self, export_path=None):
        """Export database data to JSON format"""
        try:
            if not export_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_path = f"meal_planner_export_{timestamp}.json"
            
            export_data = {}
            tables = ['users', 'meals', 'ingredients', 'meal_plan', 'favorites', 'shopping_list']
            
            for table in tables:
                try:
                    self.cursor.execute(f'SELECT * FROM {table}')
                    rows = self.cursor.fetchall()
                    
                    # Get column names
                    self.cursor.execute(f'PRAGMA table_info({table})')
                    columns = [col[1] for col in self.cursor.fetchall()]
                    
                    # Convert rows to dictionaries
                    table_data = []
                    for row in rows:
                        row_dict = dict(zip(columns, row))
                        table_data.append(row_dict)
                    
                    export_data[table] = table_data
                    
                except Exception as e:
                    print(f"⚠️  Error exporting table {table}: {e}")
            
            # Write to JSON file
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            print(f"✅ Data exported to: {export_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
            return False

def main():
    """Main function for database maintenance"""
    print("🔧 MEAL PLANNER DATABASE MAINTENANCE")
    print("=" * 50)
    
    maintenance = DatabaseMaintenance()
    
    if not maintenance.connect():
        sys.exit(1)
    
    while True:
        print("\n📋 Available Operations:")
        print("1. Create backup")
        print("2. List backups")
        print("3. Restore from backup")
        print("4. Optimize database")
        print("5. Check database integrity")
        print("6. Show database statistics")
        print("7. Clean up old backups")
        print("8. Export data to JSON")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-8): ").strip()
        
        if choice == '1':
            compress = input("Compress backup? (y/n): ").strip().lower() == 'y'
            maintenance.create_backup(compress)
        
        elif choice == '2':
            maintenance.list_backups()
        
        elif choice == '3':
            backups = maintenance.list_backups()
            if backups:
                backup_name = input("Enter backup filename to restore: ").strip()
                if backup_name:
                    maintenance.restore_backup(backup_name)
        
        elif choice == '4':
            maintenance.optimize_database()
        
        elif choice == '5':
            maintenance.check_database_integrity()
        
        elif choice == '6':
            maintenance.get_database_stats()
        
        elif choice == '7':
            days = input("Keep backups for how many days? (default 30): ").strip()
            days = int(days) if days.isdigit() else 30
            maintenance.cleanup_old_backups(days)
        
        elif choice == '8':
            export_path = input("Enter export filename (or press Enter for auto-generated): ").strip()
            if not export_path:
                export_path = None
            maintenance.export_data(export_path)
        
        elif choice == '0':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")
    
    maintenance.disconnect()

if __name__ == "__main__":
    main() 